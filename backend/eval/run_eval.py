"""Chạy eval harness — thiet_ke_danh_gia.md §6.

Lệnh: ``cd backend && python -m eval.run_eval [--case gc_crm_ja] [--repeat 1]``
hoặc ``make eval``. Dùng LLM_PROVIDER hiện tại (mặc định mock).

Luồng mỗi case: nạp sample → xác nhận parse → chạy pipeline (đồng bộ) → tự trả
lời câu hỏi làm rõ bằng ``answers`` trong case → đọc WBS/lịch/confidence → tính
chỉ số §6.2 → report.py ghi báo cáo (md + json).

Với mock, GapQuestions dùng fixture ``no_questions`` để pipeline chạy thẳng
(harness đo độ chính xác ước lượng, không đo UX làm rõ); vòng tự trả lời vẫn
hoạt động cho LLM thật.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from datetime import date
from pathlib import Path

EVAL_ROOT = Path(__file__).resolve().parent
CASES_DIR = EVAL_ROOT / "cases"

sys.path.insert(0, str(EVAL_ROOT.parent))  # backend/ lên sys.path

import yaml  # noqa: E402

from app.core import db  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.llm.mock_client import MockLLMClient  # noqa: E402
from app.models import Attachment, Bid, Question  # noqa: E402
from app.pipeline import orchestrator  # noqa: E402
import sys as _sys  # noqa: E402

# LƯU Ý: app.pipeline.__init__ gán ``orchestrator`` = singleton instance, CHE
# module cùng tên → ``import app.pipeline.orchestrator as m`` trả instance.
# Lấy module thật qua sys.modules để rebind get_llm_client.
orchestrator_module = _sys.modules["app.pipeline.orchestrator"]  # noqa: E402
from app.services import sample_service  # noqa: E402
from app.services.bid_service import get_bid_or_404  # noqa: E402
from app.services.clarify_service import (  # noqa: E402
    count_rounds_used,
    list_questions,
    submit_answers,
)
from app.services.confidence_service import get_confidence  # noqa: E402
from app.services.schedule_service import get_schedule  # noqa: E402
from app.services.solution_service import current_choice  # noqa: E402
from app.services.wbs_engine import enrich_items  # noqa: E402
from app.services.wbs_service import build_wbs_out, load_items, item_to_dict  # noqa: E402

from eval.metrics import compute_metrics  # noqa: E402
from eval.report import write_report  # noqa: E402


class _CountingClient:
    """Bọc client để đếm số lần gọi LLM (chỉ số §6.2 ``llm_calls``)."""

    def __init__(self, inner) -> None:
        self.inner = inner
        self.calls = 0

    def complete(self, *, schema, prompt, context=None):
        self.calls += 1
        return self.inner.complete(schema=schema, prompt=prompt, context=context)


def _make_client() -> _CountingClient:
    if settings.llm_provider == "mock":
        inner = MockLLMClient(fixture_modes={"GapQuestions": "no_questions"})
    else:
        from app.llm import get_llm_client

        inner = get_llm_client()
    return _CountingClient(inner)


def load_cases(case_ids: list[str] | None = None) -> list[dict]:
    """Đọc file golden case trong eval/cases/ (mỗi case 1 file YAML)."""
    files = sorted(CASES_DIR.glob("*.yaml"))
    cases = []
    for path in files:
        case = yaml.safe_load(path.read_text(encoding="utf-8"))
        if case_ids and case["id"] not in case_ids:
            continue
        cases.append(case)
    if not cases:
        raise SystemExit(f"Không tìm thấy case nào (đã lọc: {case_ids})")
    return cases


def _confirm_parse(bid_id: int) -> None:
    """Parse attachment thật (tạo Requirement rows) + đánh dấu data_readiness.

    Không dùng confirm() chặt chẽ của M6: file phụ (PDF/docx mẫu) có thể parse
    lỗi nhưng requirement vẫn đọc được từ file requirement → eval vẫn chạy được.
    Pipeline chạy trực tiếp qua orchestrator.run() nên không bị chặn bởi gate M6.
    """
    from app.services.parse_service import parse as parse_attachments

    session = db.SessionLocal()
    try:
        try:
            parse_attachments(session, bid_id)
        except Exception:
            # Parse một phần lỗi — không chặn eval; requirement đã tạo nếu có.
            session.rollback()
        bid = session.get(Bid, bid_id)
        if bid is not None:
            bid.data_readiness = "medium"
            session.commit()
    finally:
        session.close()


def _run_pipeline(bid_id: int, case: dict) -> None:
    """Chạy pipeline đồng bộ + tự trả lời câu hỏi làm rõ bằng answers trong case."""
    session = db.SessionLocal()
    try:
        orchestrator._register_steps(session, bid_id)
        bid = session.get(Bid, bid_id)
        assert bid is not None
        bid.status = "analyzing"
        session.commit()
    finally:
        session.close()

    max_rounds = int(case.get("expected", {}).get("max_question_rounds", 2))
    default_answer = (case.get("answers") or {}).get("default", "Đúng như mô tả.")
    from_step: str | None = None
    last_status: str | None = None
    for _ in range(max_rounds + 2):
        asyncio.run(orchestrator.run(bid_id, from_step=from_step))
        session = db.SessionLocal()
        try:
            bid = session.get(Bid, bid_id)
            if bid is None:
                raise RuntimeError(f"Hồ sơ {bid_id} biến mất khi chạy pipeline")
            last_status = bid.status
            if bid.status == "waiting_tech_approval":
                return
            if bid.status == "waiting_clarification":
                awaiting = [
                    q
                    for q in list_questions(session, bid_id)["items"]
                    if q.status == "awaiting_answer"
                ]
                if not awaiting:
                    # Không còn câu hỏi chờ (vd mock vòng 2 trả câu trùng) → chạy tiếp.
                    from_step = "gap"
                    continue
                answers = [
                    {"question_id": q.id, "answer": default_answer, "is_assumption": False}
                    for q in awaiting
                ]
                submit_answers(
                    session, bid_id, awaiting[0].round_no, answers, answered_by="eval"
                )
                from_step = "gap"
                continue
            if bid.status == "error":
                raise RuntimeError(f"Pipeline lỗi cho hồ sơ {bid_id}")
        finally:
            session.close()
    raise RuntimeError(
        f"Pipeline không hoàn thành sau {max_rounds + 2} vòng (hồ sơ {bid_id}, "
        f"trạng thái cuối: {last_status})"
    )


def _collect_run(bid_id: int, counting: _CountingClient, seconds: float) -> dict:
    """Đọc kết quả pipeline (WBS, lịch, confidence, câu hỏi) thành dict thô."""
    session = db.SessionLocal()
    try:
        bid = get_bid_or_404(session, bid_id)
        choice = current_choice(session, bid_id)
        direction = choice.direction if choice else None

        wbs = build_wbs_out(session, bid, load_items(session, bid_id))
        wbs_total = wbs["totals"]["man_day"]
        wbs_by_phase = wbs["totals"]["by_phase"]
        effort_range = wbs["trace"]["range"]

        covered_codes = {
            code
            for item in wbs["items"]
            if item.get("is_leaf")
            for code in (item.get("requirement_codes") or [])
        }
        total_requirements = _requirement_count(session, bid_id)

        schedule = get_schedule(session, bid_id)
        start_date = schedule["start_date"]
        end_date = schedule["end_date"]
        duration_weeks = round((end_date - start_date).days / 7, 1)
        poc_weeks = None
        if schedule.get("go_no_go_start"):
            poc_weeks = round((schedule["go_no_go_start"] - start_date).days / 7, 1)
        schedule_ok = (
            schedule.get("warning") is None and not schedule.get("deadline_violation")
        )

        confidence = get_confidence(session, bid_id)
        rounds = count_rounds_used(session, bid_id)
        question_count = session.query(Question).filter_by(bid_id=bid_id).count()

        return {
            "bid_id": bid_id,
            "direction": direction,
            "wbs_total": wbs_total,
            "wbs_by_phase": wbs_by_phase,
            "effort_range": effort_range,
            "wbs_checks": {
                key: wbs["check"][key]
                for key in ("pm_qa_ok", "within_20pct", "cycle_free", "leaf_within_limit")
            },
            "schedule_ok": schedule_ok,
            "duration_weeks": duration_weeks,
            "poc_duration_weeks": poc_weeks,
            "traceability": {
                "covered": len(covered_codes),
                "total": total_requirements,
                "covered_codes": covered_codes,
            },
            "question_rounds": rounds,
            "question_count": question_count,
            "confidence_level": confidence["level"],
            "llm_calls": counting.calls,
            "seconds": seconds,
        }
    finally:
        session.close()


def _requirement_count(session, bid_id: int) -> int:
    from app.models import Requirement

    return session.query(Requirement).filter_by(bid_id=bid_id).count()


def run_case(case: dict, counting: _CountingClient, repeat: int = 1) -> list[dict]:
    """Chạy một golden case ``repeat`` lần; trả danh sách chỉ số mỗi lần."""
    results: list[dict] = []
    wbs_totals: list[float] = []
    for _ in range(repeat):
        session = db.SessionLocal()
        try:
            bid = sample_service.load_sample(
                session, case["input"]["sample_key"], created_by="eval"
            )
            bid_id = bid.id
        finally:
            session.close()
        _confirm_parse(bid_id)
        started = time.time()
        _run_pipeline(bid_id, case)
        elapsed = time.time() - started
        run = _collect_run(bid_id, counting, elapsed)
        wbs_totals.append(run["wbs_total"])
        run["wbs_totals_across_repeats"] = list(wbs_totals)
        results.append(compute_metrics(run, case.get("expected") or {}))
        results[-1]["bid_id"] = bid_id
    return results


def run_eval(
    case_ids: list[str] | None = None,
    repeat: int = 1,
    reports_dir: Path | None = None,
) -> dict:
    """Chạy toàn bộ (hoặc subset) golden case; trả dict để report.py ghi file."""
    db.init_db()  # đảm bảo schema mới nhất (migration cột nullable, BR-09)
    cases = load_cases(case_ids)
    counting = _make_client()
    # Pipeline đọc client qua get_llm_client() trong module orchestrator — trỏ
    # về client đếm (app.pipeline.orchestrator là singleton instance, không phải module).
    orchestrator_module.get_llm_client = lambda: counting

    started = time.time()
    all_results: list[dict] = []
    per_case: dict[str, list[dict]] = {}
    for case in cases:
        results = run_case(case, counting, repeat)
        per_case[case["id"]] = results
        all_results.extend(results)

    from eval.metrics import aggregate_metrics

    summary = aggregate_metrics(all_results)
    # Với mock, model hiển thị là "mock" — không gán tên model thật (harness
    # không gọi LLM thật, tên model cấu hình chỉ dành cho provider openai_compat).
    model = "mock" if settings.llm_provider == "mock" else (settings.llm_model or settings.llm_provider)
    return {
        "provider": settings.llm_provider,
        "model": model,
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "repeat": repeat,
        "case_ids": [case["id"] for case in cases],
        "per_case": per_case,
        "summary": summary,
        "seconds": round(time.time() - started, 2),
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Eval harness (thiet_ke_danh_gia.md §6)")
    parser.add_argument("--case", action="append", dest="case_ids", help="Chạy 1 case (lặp lại để chọn nhiều)")
    parser.add_argument("--repeat", type=int, default=1, help="Số lần chạy mỗi case (chỉ có ý nghĩa với LLM thật)")
    args = parser.parse_args(argv)

    result = run_eval(args.case_ids, repeat=max(1, args.repeat))
    paths = write_report(result)
    print(f"Đã ghi báo cáo: {paths['md']}")
    print(f"                 {paths['json']}")
    print(f"Tổng hợp: MAPE={result['summary'].get('mape')}%, "
          f"total_in_expected={result['summary'].get('total_in_expected_rate')}, "
          f"interval_hit={result['summary'].get('interval_hit_rate')}, "
          f"direction_ok={result['summary'].get('direction_ok_pct')}%")


if __name__ == "__main__":
    main()