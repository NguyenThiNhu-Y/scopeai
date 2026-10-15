"""Đợt 14 backend — WBS cùng midpoint effort (C1) và mock WBS lá ≤ 10 (C2).

- C1: WBS phải dùng CÙNG hệ số/midpoint với effort engine (cả customer_jp và
  many_requirements) — trước đây wbs_service/confidence_service gọi
  calculate_effort không session nên thiếu factor many_requirements.
- C2: mock WBS (Đợt 14) tách task để mọi lá ≤ 10 man-day kể cả factor cap 2.0;
  mẫu CRM ja (none) và Tokai (rag) đều đạt 4/4 kiểm tra WBS.
"""

from __future__ import annotations

from app.core import db
from app.llm.mock_client import get_fixture
from app.models import Requirement
from app.schemas.llm_schemas.wbs_structure import WbsStructure
from app.services import wbs_engine
from app.services.effort_engine import calculate_effort
from app.services.wbs_service import persist_wbs_items
from tests.helpers import create_bid


def _add_requirements(session, bid_id: int, prefix: str, count: int) -> None:
    """Thêm requirement giả lập với mã khách (FR-xxx / FR-QA-xxx)."""
    for index in range(1, count + 1):
        session.add(
            Requirement(
                bid_id=bid_id,
                internal_code=f"{prefix}-{index:03d}",
                content=f"Yêu cầu giả lập {index}",
                priority="Must",
                category="functional" if prefix.startswith("FR") else "non-functional",
                source_sheet="要件",
                source_row=index + 1,
            )
        )
    session.commit()


def _setup_bid_with_wbs(client, *, direction: str, requirement_count: int, prefix: str) -> int:
    """Tạo bid ja + requirement + chọn hướng + persist WBS mock (man-day do code gán)."""
    bid_id = create_bid(client, customer_language="ja")
    session = db.SessionLocal()
    try:
        _add_requirements(session, bid_id, prefix, requirement_count)
        resp = client.post(
            f"/api/bids/{bid_id}/solution",
            json={"direction": direction, "reason_vi": "Lý do giả lập", "by": "ai_developer"},
            headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
        )
        assert resp.status_code == 200, resp.text

        from app.models import Bid

        bid = session.get(Bid, bid_id)
        raw = get_fixture(WbsStructure, "good", context={"direction": direction})
        tasks = WbsStructure.model_validate(raw).model_dump(mode="json")["tasks"]
        effort = calculate_effort(bid, direction, session)
        tasks = wbs_engine.assign_man_days(tasks, effort["by_phase"])
        persist_wbs_items(session, bid_id, tasks, by="test")
        session.commit()
    finally:
        session.close()
    return bid_id


def test_wbs_midpoint_equals_effort_midpoint_for_crm_ja(client):
    """C1: WBS dùng cùng midpoint với effort engine.

    CRM ja 36 requirement, hướng none → factor customer_jp 1.2 ×
    many_requirements 1.15 = 1.38 → midpoint 241.5 (không còn 210).
    """
    bid_id = _setup_bid_with_wbs(client, direction="none", requirement_count=36, prefix="FR")

    wbs = client.get(f"/api/bids/{bid_id}/wbs").json()
    effort = client.get(f"/api/bids/{bid_id}/effort").json()

    assert effort["midpoint_total"] == 241.5
    assert wbs["check"]["midpoint"] == effort["midpoint_total"]
    assert wbs["totals"]["man_day"] == effort["midpoint_total"]


def test_mock_wbs_crm_ja_passes_four_of_four(client):
    """C2: mẫu CRM ja (none) → WBS 4/4, mọi lá ≤ 10 man-day."""
    bid_id = _setup_bid_with_wbs(client, direction="none", requirement_count=36, prefix="FR")

    body = client.get(f"/api/bids/{bid_id}/wbs").json()
    check = body["check"]
    assert check["pm_qa_ok"] is True
    assert check["within_20pct"] is True
    assert check["cycle_free"] is True
    assert check["leaf_within_limit"] is True
    assert check["leaf_max_man_day"] <= 10.0


def test_mock_wbs_tokai_rag_passes_four_of_four(client):
    """C2: bộ Tokai (rag, 41 requirement) → WBS 4/4, mọi lá ≤ 10 man-day."""
    bid_id = _setup_bid_with_wbs(client, direction="rag", requirement_count=41, prefix="FR-QA")

    body = client.get(f"/api/bids/{bid_id}/wbs").json()
    check = body["check"]
    assert check["pm_qa_ok"] is True
    assert check["within_20pct"] is True
    assert check["cycle_free"] is True
    assert check["leaf_within_limit"] is True
    assert check["leaf_max_man_day"] <= 10.0


def test_eval_reports_latest_resolves_from_code_location(client, tmp_path, monkeypatch):
    """D3: GET /api/eval/reports/latest không phụ thuộc thư mục chạy (D-13-1).

    Chạy từ CWD khác (tmp_path) vẫn tìm thấy báo cáo trong docs/eval/reports
    vì đường dẫn resolve từ vị trí file code.
    """
    monkeypatch.chdir(tmp_path)
    resp = client.get("/api/eval/reports/latest")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("provider") == "mock"


# ---------------------------------------------------------------- E — mock Tokai

def _tokai_context() -> dict:
    from pathlib import Path

    from app.parsers.excel import read_sheets
    from app.parsers.requirements import normalize

    real_dir = Path(__file__).resolve().parents[2] / "sample_data" / "rfp_tokai_minato" / "real"
    xlsx = next(real_dir.glob("*.xlsx"))
    reqs = normalize(read_sheets(xlsx.read_bytes(), xlsx.name))
    return {
        "customer_language": "ja",
        "request": "設備保全ナレッジAIアシスタントの構築を計画しております。",
        "rfp_files": [{"filename": "RFP.docx", "text": "設備保全ナレッジAI RFP 東海ミナトテック"}],
        "direction": "rag",
        "requirements": [{"req_code": r["internal_code"], "content": r["content"]} for r in reqs],
        "requirements_data": [{"req_code": r["internal_code"], "content": r["content"]} for r in reqs],
        "batch_codes": [r["internal_code"] for r in reqs],
    }


def test_mock_tokai_intake_is_maintenance_knowledge_assistant():
    from app.llm.mock_client import MockLLMClient
    from app.schemas.llm_schemas.intake_extraction import IntakeExtraction

    client = MockLLMClient()
    result = client.complete(schema=IntakeExtraction, prompt="intake", context=_tokai_context())
    text = " ".join([result["objectives_vi"], result["data_vi"], " ".join(result["constraints_vi"])])
    assert "bảo trì" in text
    assert "230" in result["users_vi"]
    assert "Japan East" in text
    assert "15 triệu JPY" in result["budget_note_vi"]
    assert "2026/12" in result["customer_schedule_note_vi"]
    assert "2027" in result["customer_schedule_note_vi"]


def test_mock_tokai_gap_questions_cover_scan_accuracy_and_integration():
    from app.llm.mock_client import MockLLMClient
    from app.schemas.llm_schemas.gap_questions import GapQuestions

    client = MockLLMClient()
    result = client.complete(
        schema=GapQuestions, prompt="gap", context={**_tokai_context(), "rounds_used": 0}
    )
    assert result["needs_clarification"] is True
    questions = " ".join(q["question"] for q in result["questions"])
    assert "スキャン" in questions
    assert "300問" in questions
    assert "MAINTE-PRO" in questions
    assert "Japan East" in questions


def test_mock_tokai_solution_is_rag_with_ocr_and_acceptance_risks():
    from app.llm.mock_client import MockLLMClient
    from app.schemas.llm_schemas.solution_proposal import SolutionProposal

    client = MockLLMClient()
    result = client.complete(schema=SolutionProposal, prompt="solution", context=_tokai_context())
    assert result["direction"] == "rag"
    risk_types = {risk["type_vi"] for risk in result["risks"]}
    assert "OCR" in risk_types
    assert "Nghiệm thu" in risk_types
    assert result["feasibility_score"]["score"] == 4


def test_mock_tokai_wbs_has_rag_tasks_and_assigns_customer_codes():
    from app.llm.mock_client import MockLLMClient
    from app.schemas.llm_schemas.wbs_structure import WbsStructure

    client = MockLLMClient()
    result = client.complete(schema=WbsStructure, prompt="wbs", context=_tokai_context())
    task_names = " ".join(t["name_vi"] for t in result["tasks"])
    assert "OCR" in task_names
    assert "chỉ mục" in task_names
    assert "song ngữ" in task_names
    assert "sự cố tương tự" in task_names
    assigned = {code for t in result["tasks"] for code in (t.get("requirement_codes") or [])}
    assert "FR-QA-001" in assigned
    assert len(assigned) == 41


def test_mock_tokai_evaluates_all_41_requirements():
    from app.llm.mock_client import MockLLMClient
    from app.schemas.llm_schemas.evaluation import EvaluationBatch

    client = MockLLMClient()
    result = client.complete(schema=EvaluationBatch, prompt="eval", context=_tokai_context())
    assert len(result["batch"]) == 41
    codes = {item["req_code"] for item in result["batch"]}
    assert "FR-QA-001" in codes
    assert "NFR-PF-001" in codes
    ratings = {item["rating"] for item in result["batch"]}
    assert ratings <= {"◎", "○", "△", "×", "cần làm rõ"}


def test_tokai_pipeline_runs_end_to_end(client):
    """E: bộ Tokai chạy pipeline đầy đủ (mock) → hướng RAG, WBS 4/4,
    midpoint WBS = effort midpoint, độ tin cậy tính được."""
    from tests.helpers import bid_status, wait_until

    sample_key = "tokai" + "_minato"
    resp = client.post("/api/bids/sample", json={"sample_key": sample_key})
    assert resp.status_code == 201, resp.text
    bid_id = resp.json()["id"]

    resp = client.post(f"/api/bids/{bid_id}/parse")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["requirements"]["count"] == 41
    assert all(a["status"] == "ok" for a in body["attachments"])

    resp = client.put(
        f"/api/bids/{bid_id}/parse/confirm",
        json={"data_readiness": "high", "confirmed": True},
    )
    assert resp.status_code == 200, resp.text

    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202, resp.text
    assert wait_until(lambda: bid_status(client, bid_id) in ("waiting_tech_approval", "waiting_clarification"))

    # Trả lời câu hỏi làm rõ (tối đa 2 vòng); endpoint answers tự resume pipeline
    # từ bước gap (questions.py) — KHÔNG gọi start lại để tránh chạy 2 lần.
    for _ in range(3):
        if bid_status(client, bid_id) != "waiting_clarification":
            break
        questions = client.get(f"/api/bids/{bid_id}/questions").json()["items"]
        awaiting = [q for q in questions if q["status"] == "awaiting_answer"]
        if not awaiting:
            break
        round_no = awaiting[0]["round_no"]
        answers = [
            {"question_id": q["id"], "answer": "想定どおりで問題ありません。", "is_assumption": False}
            for q in awaiting
        ]
        resp = client.post(
            f"/api/bids/{bid_id}/questions/{round_no}/answers", json={"answers": answers}
        )
        assert resp.status_code == 200, resp.text
        assert wait_until(lambda: bid_status(client, bid_id) in ("waiting_tech_approval", "waiting_clarification"))

    assert bid_status(client, bid_id) == "waiting_tech_approval"

    # Nội dung Tokai qua API.
    evaluations = client.get(f"/api/bids/{bid_id}/evaluations").json()
    assert evaluations["solution_direction"]["direction"] == "rag"
    risk_types = {r["type_vi"] for r in evaluations["solution_direction"]["risks"]}
    assert "OCR" in risk_types

    wbs = client.get(f"/api/bids/{bid_id}/wbs").json()
    effort = client.get(f"/api/bids/{bid_id}/effort").json()
    assert wbs["check"]["midpoint"] == effort["midpoint_total"]
    # Tổng WBS ≈ midpoint (sai số ≤ 0.5 do làm tròn man-day về bội số 0.5
    # và biểu diễn float của cùng giá trị 521.65).
    assert abs(wbs["totals"]["man_day"] - effort["midpoint_total"]) <= 0.5
    assert all(wbs["check"][k] for k in ("pm_qa_ok", "within_20pct", "cycle_free", "leaf_within_limit"))
    assert wbs["check"]["leaf_max_man_day"] <= 10.0

    confidence = client.get(f"/api/bids/{bid_id}/confidence").json()
    assert confidence["level"] in ("high", "medium", "low")
    assert len(confidence["signals"]) == 7


def test_tokai_mock_intake_returns_full_customer_milestones_and_schedule_respects_them(client):
    """Đợt 15: bộ Tokai — mock intake trả đủ mốc khách (Phase 3 mở "2027年10月〜"
    nên KHÔNG có customer_schedule_end); lịch không bắt đầu MVP/Production trước
    mốc khách và PoC dùng đúng khoảng khách (2026-12 → 2027-02)."""
    import asyncio
    from datetime import date

    from app.llm.mock_client import MockLLMClient
    from app.models import Bid, PipelineStep
    from app.pipeline.steps.b1_intake import run_intake
    from tests.helpers import put_schedule

    resp = client.post("/api/bids/sample", json={"sample_key": "tokai_minato"})
    assert resp.status_code == 201, resp.text
    bid_id = resp.json()["id"]

    resp = client.post(f"/api/bids/{bid_id}/parse")
    assert resp.status_code == 200, resp.text

    session = db.SessionLocal()
    try:
        for step_key in ("intake", "gap", "solution", "evaluate", "wbs", "proposal", "ja_check"):
            session.add(PipelineStep(bid_id=bid_id, step_key=step_key, status="pending"))
        session.commit()
    finally:
        session.close()

    asyncio.run(run_intake(bid_id, MockLLMClient()))

    session = db.SessionLocal()
    try:
        bid = session.get(Bid, bid_id)
        assert bid is not None
        assert bid.customer_schedule_start == date(2026, 12, 1)
        assert bid.customer_poc_end == date(2027, 2, 28)
        assert bid.customer_mvp_start == date(2027, 4, 1)
        assert bid.customer_production_start == date(2027, 10, 1)
        # Phase 3 mở ("2027年10月〜") → không có ngày kết thúc.
        assert bid.customer_schedule_end is None
        assert bid.budget_scope == "poc"
    finally:
        session.close()

    # Lịch: MVP/Production không bắt đầu trước mốc khách.
    resp = client.post(
        f"/api/bids/{bid_id}/solution",
        json={"direction": "rag", "reason_vi": "Lý do giả lập", "by": "ai_developer"},
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 200, resp.text

    session = db.SessionLocal()
    try:
        from app.llm.mock_client import get_fixture
        from app.schemas.llm_schemas.wbs_structure import WbsStructure
        from app.services import wbs_engine
        from app.services.effort_engine import calculate_effort
        from app.services.wbs_service import persist_wbs_items

        bid = session.get(Bid, bid_id)
        raw = get_fixture(WbsStructure, "good", context={"direction": "rag"})
        tasks = WbsStructure.model_validate(raw).model_dump(mode="json")["tasks"]
        effort = calculate_effort(bid, "rag", session)
        tasks = wbs_engine.assign_man_days(tasks, effort["by_phase"])
        persist_wbs_items(session, bid_id, tasks, by="test")
        session.commit()
    finally:
        session.close()

    sched = put_schedule(client, bid_id, start_date="2026-12-01", working_calendar="jp")
    assert sched["earliest_mvp_start"] >= "2027-04-01"
    assert sched["earliest_production_start"] >= "2027-10-01"
    # PoC dùng đúng khoảng khách: go/no-go bắt đầu SAU 2027-02-28 (không kết thúc sớm rồi chờ).
    assert sched["go_no_go_start"] >= "2027-03-01"