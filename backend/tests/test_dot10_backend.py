"""Tests Đợt 10 — backend: lịch song song + go/no-go, mốc khách, WBS theo hướng,
rủi ro/khả thi, vòng hỏi 2, Bid/No-bid mặc định. Mọi số do code tính (AGENTS.md)."""

from __future__ import annotations

import asyncio
import math
from datetime import date

from app.core import db
from app.llm.mock_client import MockLLMClient
from app.models import Bid, PipelineStep, Schedule, WbsItem
from app.pipeline.steps.b1_intake import _apply_customer_constraints, run_intake
from app.pipeline.steps.b5_wbs import run_wbs
from app.services import schedule_engine, wbs_engine
from app.services.reference_service import load_holidays, load_payment
from app.services.solution_service import choose_solution
from sqlalchemy import select
from tests.helpers import create_bid, wait_until

BY_PHASE = {
    "poc": {"min": 8, "max": 12},
    "mvp": {"min": 20, "max": 30},
    "production": {"min": 10, "max": 16},
}


def _enriched_good() -> list[dict]:
    from app.llm.mock_client import get_fixture
    from app.schemas.llm_schemas.wbs_structure import WbsStructure

    raw = get_fixture(WbsStructure, "good")
    tasks = WbsStructure.model_validate(raw).model_dump(mode="json")["tasks"]
    tasks = wbs_engine.assign_man_days(tasks, BY_PHASE)
    return wbs_engine.enrich_items(tasks)


def _schedule(items: list[dict], allocation: dict, gap: int = 10) -> dict:
    return schedule_engine.compute_schedule(
        items=items,
        start_date=date(2026, 11, 1),
        buffer_days=0,
        team_allocation=allocation,
        working_calendar="vn",
        payment_milestones=load_payment()["milestones"],
        holidays=load_holidays(),
        go_no_go_gap_working_days=gap,
    )


# ---------------------------------------------------------------- A1 + A2

def test_mvp_starts_after_go_no_go_end():
    """N1: task MVP đầu tiên >= go_no_go_end; Production > MVP end."""
    result = _schedule(_enriched_good(), {
        "pm": 1, "ba": 1, "brse": 1, "ai_engineer": 1,
        "backend": 2, "frontend": 1, "qa": 1, "infra": 1,
    })
    mvp_tasks = [t for t in result["tasks"] if t["phase"] == "mvp"]
    production_tasks = [t for t in result["tasks"] if t["phase"] == "production"]
    assert mvp_tasks and production_tasks
    assert result["go_no_go_end"] is not None
    first_mvp_start = min(date.fromisoformat(t["start_date"]) for t in mvp_tasks)
    assert first_mvp_start >= result["go_no_go_end"], (
        f"MVP bắt đầu {first_mvp_start} trước go_no_go_end {result['go_no_go_end']}"
    )
    last_mvp_end = max(date.fromisoformat(t["end_date"]) for t in mvp_tasks)
    first_production_start = min(date.fromisoformat(t["start_date"]) for t in production_tasks)
    assert first_production_start > last_mvp_end
    # earliest_mvp_start khớp lịch thực (trước đây mâu thuẫn).
    assert result["earliest_mvp_start"] == first_mvp_start


def _sequential_end(items: list[dict], allocation: dict, start_date: date) -> date:
    """Lịch tuần tự cũ (một cursor chung) — baseline để so sánh N2."""
    leaves = sorted(
        [i for i in items if i["is_leaf"] and i.get("role")],
        key=lambda t: (t["phase"], t.get("sort_order") or 0, t["task_code"]),
    )
    holiday_set = {date.fromisoformat(d) for d in load_holidays().get("vn", [])}
    cursor = schedule_engine.to_working_day(start_date, holiday_set)
    end_map: dict[str, date] = {}
    for task in leaves:
        headcount = int(allocation.get(task["role"]) or 1)
        duration = math.ceil(float(task["man_day"]) / headcount)
        deps_end = [end_map[d] for d in task.get("depends_on") or [] if d in end_map]
        start = max(cursor, max(deps_end)) if deps_end else cursor
        start = schedule_engine.to_working_day(start, holiday_set)
        end = schedule_engine.add_working_days(start, duration, holiday_set)
        end_map[task["task_code"]] = end
        cursor = schedule_engine.next_working_day(end, holiday_set)
    return max(end_map.values()) if end_map else start_date


def _wbs_210_man_days() -> list[dict]:
    """WBS giả lập tổng 210 man-day (không gọi LLM — code tự dựng để test)."""
    raw = [
        # poc = 40
        {"task_code": "T-001", "name_vi": "P", "phase": "poc", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "T-001-01", "name_vi": "PM P", "phase": "poc", "parent_code": "T-001", "role": "pm", "weight": 5, "depends_on": []},
        {"task_code": "T-001-02", "name_vi": "BA P", "phase": "poc", "parent_code": "T-001", "role": "ba", "weight": 10, "depends_on": []},
        {"task_code": "T-001-03", "name_vi": "BE P", "phase": "poc", "parent_code": "T-001", "role": "backend", "weight": 10, "depends_on": []},
        {"task_code": "T-001-04", "name_vi": "FE P", "phase": "poc", "parent_code": "T-001", "role": "frontend", "weight": 10, "depends_on": []},
        {"task_code": "T-001-05", "name_vi": "QA P", "phase": "poc", "parent_code": "T-001", "role": "qa", "weight": 5, "depends_on": []},
        # mvp = 100
        {"task_code": "T-002", "name_vi": "M", "phase": "mvp", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "T-002-01", "name_vi": "PM M", "phase": "mvp", "parent_code": "T-002", "role": "pm", "weight": 10, "depends_on": []},
        {"task_code": "T-002-02", "name_vi": "AI M", "phase": "mvp", "parent_code": "T-002", "role": "ai_engineer", "weight": 20, "depends_on": []},
        {"task_code": "T-002-03", "name_vi": "BE M", "phase": "mvp", "parent_code": "T-002", "role": "backend", "weight": 25, "depends_on": []},
        {"task_code": "T-002-04", "name_vi": "FE M", "phase": "mvp", "parent_code": "T-002", "role": "frontend", "weight": 25, "depends_on": []},
        {"task_code": "T-002-05", "name_vi": "QA M", "phase": "mvp", "parent_code": "T-002", "role": "qa", "weight": 10, "depends_on": []},
        {"task_code": "T-002-06", "name_vi": "INF M", "phase": "mvp", "parent_code": "T-002", "role": "infra", "weight": 10, "depends_on": []},
        # production = 70
        {"task_code": "T-003", "name_vi": "R", "phase": "production", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "T-003-01", "name_vi": "PM R", "phase": "production", "parent_code": "T-003", "role": "pm", "weight": 10, "depends_on": []},
        {"task_code": "T-003-02", "name_vi": "AI R", "phase": "production", "parent_code": "T-003", "role": "ai_engineer", "weight": 10, "depends_on": []},
        {"task_code": "T-003-03", "name_vi": "BE R", "phase": "production", "parent_code": "T-003", "role": "backend", "weight": 20, "depends_on": []},
        {"task_code": "T-003-04", "name_vi": "FE R", "phase": "production", "parent_code": "T-003", "role": "frontend", "weight": 15, "depends_on": []},
        {"task_code": "T-003-05", "name_vi": "QA R", "phase": "production", "parent_code": "T-003", "role": "qa", "weight": 10, "depends_on": []},
        {"task_code": "T-003-06", "name_vi": "INF R", "phase": "production", "parent_code": "T-003", "role": "infra", "weight": 5, "depends_on": []},
    ]
    man_days = {
        "T-001-01": 5, "T-001-02": 10, "T-001-03": 10, "T-001-04": 10, "T-001-05": 5,
        "T-002-01": 10, "T-002-02": 20, "T-002-03": 25, "T-002-04": 25, "T-002-05": 10, "T-002-06": 10,
        "T-003-01": 10, "T-003-02": 10, "T-003-03": 20, "T-003-04": 15, "T-003-05": 10, "T-003-06": 5,
    }
    for task in raw:
        task["man_day"] = man_days.get(task["task_code"])
    items = wbs_engine.enrich_items(raw)
    assert abs(sum(i["man_day"] for i in items if i["is_leaf"]) - 210) < 0.5
    return items


def test_parallel_roles_shorter_than_sequential():
    """N2: 210 man-day với PM3 BA1 AI2 BE3 FE3 QA2 Infra1 ngắn hơn rõ so với tuần tự."""
    items = _wbs_210_man_days()
    allocation = {
        "pm": 3, "ba": 1, "ai_engineer": 2, "backend": 3,
        "frontend": 3, "qa": 2, "infra": 1,
    }
    parallel = _schedule(items, allocation)
    sequential_end = _sequential_end(items, allocation, date(2026, 11, 1))
    parallel_end = parallel["end_date"]
    assert parallel_end < sequential_end, (
        f"Song song {parallel_end} phải ngắn hơn tuần tự {sequential_end}"
    )
    # Ngắn hơn rõ: chênh ít nhất 20 ngày làm việc.
    assert (sequential_end - parallel_end).days >= 20


def test_parallel_roles_within_same_phase_overlap():
    """N2: task backend và frontend cùng phase chạy đè thời gian (không nối đuôi)."""
    items = _wbs_210_man_days()
    allocation = {
        "pm": 1, "ba": 1, "ai_engineer": 1, "backend": 1,
        "frontend": 1, "qa": 1, "infra": 1,
    }
    result = _schedule(items, allocation)
    mvp = [t for t in result["tasks"] if t["phase"] == "mvp"]
    be = next(t for t in mvp if t["role"] == "backend")
    fe = next(t for t in mvp if t["role"] == "frontend")
    # Hai task khác vai trò cùng phase phải trùng khoảng thời gian.
    assert date.fromisoformat(be["start_date"]) < date.fromisoformat(fe["end_date"])
    assert date.fromisoformat(fe["start_date"]) < date.fromisoformat(be["end_date"])


# ---------------------------------------------------------------- A3

_JAPANESE_RFP = (
    "希望スケジュール：2027年1月に着手、同年6月までにMVPを利用開始、"
    "同年9月に本番展開を予定しています。予算は1,500万円（税別）程度です。"
)


def test_intake_extracts_japanese_milestones():
    """A3: trích đủ mốc bắt đầu/MVP/Production từ RFP Nhật; end = Production."""
    from app.models import Bid

    bid = Bid(
        project_name="T", customer_name="C", submission_deadline=date(2026, 12, 15),
        customer_language="ja", request_content=_JAPANESE_RFP,
    )
    _apply_customer_constraints(bid, _JAPANESE_RFP)
    assert bid.customer_schedule_start == date(2027, 1, 1)
    assert bid.customer_mvp_start == date(2027, 6, 1)
    assert bid.customer_production_start == date(2027, 9, 1)
    assert bid.customer_schedule_end == date(2027, 9, 1)  # trước đây sai
    assert bid.budget_amount == 15_000_000
    assert bid.budget_currency == "JPY"


def _register_steps(session, bid_id: int) -> None:
    for step_key in ("intake", "gap", "solution", "evaluate", "wbs", "proposal", "ja_check"):
        session.add(PipelineStep(bid_id=bid_id, step_key=step_key, status="pending"))


def test_wbs_default_schedule_starts_from_customer_milestone(client):
    """A3: lịch mặc định bắt đầu từ mốc khách; hướng none không có AI Engineer."""
    bid_id = create_bid(
        client,
        customer_language="ja",
        request_content=_JAPANESE_RFP,
    )
    session = db.SessionLocal()
    try:
        _register_steps(session, bid_id)
        session.commit()
    finally:
        session.close()

    llm = MockLLMClient(fixture_modes={"GapQuestions": "no_questions"})
    asyncio.run(run_intake(bid_id, llm))

    session = db.SessionLocal()
    try:
        bid = session.get(Bid, bid_id)
        assert bid is not None
        assert bid.customer_schedule_start == date(2027, 1, 1)
        choose_solution(session, bid_id, "none", "Lý do giả lập", by="test")
        session.commit()
    finally:
        session.close()

    asyncio.run(run_wbs(bid_id, llm))

    session = db.SessionLocal()
    try:
        sched = (
            session.execute(
                select(Schedule).where(Schedule.bid_id == bid_id).order_by(Schedule.id.desc())
            )
            .scalars()
            .first()
        )
        assert sched is not None
        assert sched.start_date == date(2027, 1, 1), f"Lịch phải bắt đầu từ mốc khách, got {sched.start_date}"
        roles = {
            item.role
            for item in session.query(WbsItem).filter_by(bid_id=bid_id).all()
            if item.role
        }
        names = " ".join(
            item.name_vi for item in session.query(WbsItem).filter_by(bid_id=bid_id).all()
        )
        assert "ai_engineer" not in roles, f"Hướng none không được có AI Engineer: {roles}"
        assert "RAG" not in names and "Huấn luyện mô hình" not in names
    finally:
        session.close()


# ---------------------------------------------------------------- B

def test_wbs_mock_none_has_no_ai_engineer():
    from app.llm.mock_client import get_fixture
    from app.schemas.llm_schemas.wbs_structure import WbsStructure

    raw = get_fixture(WbsStructure, "good", {"direction": "none"})
    tasks = WbsStructure.model_validate(raw).model_dump(mode="json")["tasks"]
    roles = {t["role"] for t in tasks if t["role"]}
    names = " ".join(t["name_vi"] for t in tasks)
    assert "ai_engineer" not in roles
    assert "RAG" not in names and "Huấn luyện mô hình" not in names


def test_evaluations_expose_risks_and_feasibility(client):
    """B: GET /evaluations trả rủi ro (loại, mức 1-5, mô tả, giảm thiểu) + điểm khả thi."""
    bid_id = create_bid(client)
    session = db.SessionLocal()
    try:
        choose_solution(
            session,
            bid_id,
            "none",
            "Lý do giả lập",
            by="test",
            risks=[
                {"type_vi": "Phạm vi", "level": 3, "description_vi": "Phạm vi có thể thay đổi.", "mitigation_vi": "Chốt phạm vi trước."},
                {"type_vi": "Dữ liệu", "level": 4, "description_vi": "Dữ liệu chưa đồng nhất.", "mitigation_vi": "Chuẩn hóa sớm."},
                {"type_vi": "Tích hợp", "level": 2, "description_vi": "Giao diện thay đổi.", "mitigation_vi": "Chốt hợp đồng tích hợp."},
                {"type_vi": "Vận hành", "level": 2, "description_vi": "Quy trình cần xác nhận.", "mitigation_vi": "Hướng dẫn vận hành."},
            ],
            feasibility_score={"score": 4, "reason_vi": "Khả thi sau khi xác nhận tiền đề."},
        )
    finally:
        session.close()

    resp = client.get(f"/api/bids/{bid_id}/evaluations")
    assert resp.status_code == 200, resp.text
    direction = resp.json()["solution_direction"]
    assert direction is not None
    assert len(direction["risks"]) >= 4
    for risk in direction["risks"]:
        assert 1 <= risk["level"] <= 5
        assert risk["type_vi"] and risk["description_vi"] and risk["mitigation_vi"]
    assert direction["feasibility_score"] is not None
    assert 1 <= direction["feasibility_score"]["score"] <= 5


# ---------------------------------------------------------------- C

def _start_pipeline(client, bid_id: int):
    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202, resp.text


def _get_questions(client, bid_id: int, round_no: int | None = None) -> dict:
    params = {"round": round_no} if round_no else None
    resp = client.get(f"/api/bids/{bid_id}/questions", params=params)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_mock_stops_after_round_one_when_answered_enough(client, mock_llm):
    """C: trả lời ĐỦ vòng 1 → mock dừng ở vòng 1, pipeline chạy tiếp."""
    bid_id = create_bid(client)
    _start_pipeline(client, bid_id)
    assert wait_until(lambda: _bid_status(client, bid_id) == "waiting_clarification")

    data = _get_questions(client, bid_id, 1)
    answers = [
        {"question_id": q["id"], "answer": "約100万件（仮の回答）", "is_assumption": False}
        for q in data["items"]
    ]
    resp = client.post(
        f"/api/bids/{bid_id}/questions/1/answers",
        json={"answers": answers},
        headers={"X-User": "Nhu"},
    )
    assert resp.status_code == 200, resp.text
    assert wait_until(lambda: _bid_status(client, bid_id) == "waiting_tech_approval")

    data = _get_questions(client, bid_id)
    assert data["rounds_used"] == 1
    assert not [q for q in data["items"] if q["round_no"] == 2]
    assert data["round_two_reason_vi"] is None


def test_round_two_only_when_blocking_answer_remains(client, mock_llm):
    """C: trả lời còn thông tin chặn (未定) → vòng 2 + round_two_reason_vi."""
    bid_id = create_bid(client)
    _start_pipeline(client, bid_id)
    assert wait_until(lambda: _bid_status(client, bid_id) == "waiting_clarification")

    data = _get_questions(client, bid_id, 1)
    answers = [
        {"question_id": q["id"], "answer": "未定（後日回答）", "is_assumption": False}
        for q in data["items"]
    ]
    resp = client.post(
        f"/api/bids/{bid_id}/questions/1/answers",
        json={"answers": answers},
        headers={"X-User": "Nhu"},
    )
    assert resp.status_code == 200, resp.text
    assert wait_until(lambda: _bid_status(client, bid_id) == "waiting_clarification")

    data = _get_questions(client, bid_id)
    assert data["rounds_used"] == 2
    assert data["round_two_reason_vi"]
    round2 = [q for q in data["items"] if q["round_no"] == 2]
    assert round2

    client_llm = mock_llm["client"]
    before = client_llm.call_counts.get("GapQuestions", 0)
    answers2 = [
        {"question_id": q["id"], "answer": "対応します", "is_assumption": False}
        for q in round2
    ]
    resp = client.post(
        f"/api/bids/{bid_id}/questions/2/answers",
        json={"answers": answers2},
        headers={"X-User": "Nhu"},
    )
    assert resp.status_code == 200, resp.text
    assert wait_until(lambda: _bid_status(client, bid_id) == "waiting_tech_approval")
    # FR-010.4: hết vòng 2 → không gọi LLM nữa.
    assert client_llm.call_counts.get("GapQuestions", 0) == before


def _bid_status(client, bid_id: int) -> str:
    resp = client.get(f"/api/bids/{bid_id}")
    assert resp.status_code == 200, resp.text
    return resp.json()["status"]


def test_schedule_warns_when_later_than_customer_milestones(client):
    """A3: cảnh báo khi lịch MVP/Production trễ hơn mốc khách."""
    from tests.helpers import default_team_allocation, put_schedule, setup_wbs_bid

    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    session = db.SessionLocal()
    try:
        bid = session.get(Bid, bid_id)
        assert bid is not None
        # Mốc khách rất sớm → lịch chắc chắn trễ.
        bid.customer_mvp_start = date(2026, 11, 15)
        bid.customer_production_start = date(2026, 12, 1)
        bid.customer_schedule_end = date(2026, 12, 15)
        session.commit()
    finally:
        session.close()

    sched = put_schedule(client, bid_id, team_allocation=default_team_allocation())
    assert sched["warning"], "Phải có cảnh báo trễ mốc khách"
    assert "trễ hơn mốc khách" in sched["warning"]


# ---------------------------------------------------------------- D

def test_bid_qualification_returns_default_criteria(client):
    """D: GET /bid-qualification trả 200 với tiêu chí mặc định từ Cài đặt."""
    bid_id = create_bid(client)
    resp = client.get(f"/api/bids/{bid_id}/bid-qualification")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["criteria"], "Phải có tiêu chí mặc định"
    assert abs(sum(item["weight"] for item in body["criteria"]) - 100) < 0.001
    for item in body["criteria"]:
        assert item["id"] and item["label_vi"]