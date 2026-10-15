"""Tests CheckEngine — PM/QA mỗi phase; B5 retry ≤ 2 → cảnh báo (không chặn).

AGENTS.md rule 2 (Structured LLM output): thiếu PM/QA → retry ≤ 2 → cảnh báo,
không persist sai; fixture sai schema → retry ≤ 2 rồi fail rõ.
"""

from __future__ import annotations

from app.core import db
from app.llm.mock_client import MockLLMClient
from app.models import PipelineStep
from app.services import check_engine, wbs_engine
from tests.helpers import bid_status, create_bid, step_status, wait_until

BY_PHASE = {
    "poc": {"min": 8, "max": 12},
    "mvp": {"min": 20, "max": 30},
    "production": {"min": 10, "max": 16},
}
MIDPOINT = 48.0


def _enriched(mode: str) -> list[dict]:
    from app.llm.mock_client import get_fixture
    from app.schemas.llm_schemas.wbs_structure import WbsStructure

    raw = get_fixture(WbsStructure, mode)
    tasks = WbsStructure.model_validate(raw).model_dump(mode="json")["tasks"]
    tasks = wbs_engine.assign_man_days(tasks, BY_PHASE)
    return wbs_engine.enrich_items(tasks)


def test_good_wbs_passes_pm_qa():
    check = check_engine.check_wbs(_enriched("good"), MIDPOINT, BY_PHASE)
    assert check["pm_qa_ok"] is True


def test_missing_pm_detected():
    check = check_engine.check_wbs(_enriched("missing_pm"), MIDPOINT, BY_PHASE)
    assert check["pm_qa_ok"] is False
    assert check["warning"] and "PM" in check["warning"]


def test_missing_qa_detected():
    check = check_engine.check_wbs(_enriched("missing_qa"), MIDPOINT, BY_PHASE)
    assert check["pm_qa_ok"] is False
    assert check["warning"] and "QA" in check["warning"]


def test_pipeline_wbs_missing_pm_retries_then_warns(client, mock_llm):
    """B5 với fixture missing_pm → retry ≤ 2 (3 lần gọi LLM) → completed + cảnh báo."""
    mock_llm["client"] = MockLLMClient(
        fixture_modes={"GapQuestions": "no_questions", "WbsStructure": "missing_pm"}
    )
    bid_id = create_bid(client)
    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")

    llm = mock_llm["client"]
    assert llm.call_counts["WbsStructure"] == 3  # lần đầu + retry ≤ 2

    session = db.SessionLocal()
    try:
        step = session.query(PipelineStep).filter_by(bid_id=bid_id, step_key="wbs").one()
        assert step.status == "completed"
        assert step.output_json is not None
        assert step.output_json["warning"]  # cảnh báo, không chặn
    finally:
        session.close()

    # GET /wbs hiển thị cờ pm_qa_ok=false + warning.
    resp = client.get(f"/api/bids/{bid_id}/wbs")
    assert resp.status_code == 200
    body = resp.json()
    assert body["check"]["pm_qa_ok"] is False
    assert body["check"]["warning"]


def test_pipeline_wbs_good_no_warning_single_call(client, mock_llm):
    """B5 với fixture good → 1 lần gọi LLM, không cảnh báo."""
    mock_llm["client"] = MockLLMClient(fixture_modes={"GapQuestions": "no_questions"})
    bid_id = create_bid(client)
    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")

    llm = mock_llm["client"]
    assert llm.call_counts["WbsStructure"] == 1

    session = db.SessionLocal()
    try:
        step = session.query(PipelineStep).filter_by(bid_id=bid_id, step_key="wbs").one()
        assert step.status == "completed"
        assert step.output_json is not None
        assert step.output_json["warning"] is None
    finally:
        session.close()

    resp = client.get(f"/api/bids/{bid_id}/wbs")
    assert resp.status_code == 200
    # Đợt 14 (C2): fixture "good" đã tách task để mọi lá ≤ 10 → WBS đạt 4/4,
    # không còn cảnh báo (khớp tên test "no_warning").
    assert resp.json()["check"]["warning"] is None


def test_pipeline_wbs_bad_schema_fails_clearly(client, mock_llm):
    """Fixture bad_schema (task nhóm có role) → retry ≤ 2 → bước wbs failed rõ."""
    mock_llm["client"] = MockLLMClient(
        fixture_modes={"GapQuestions": "no_questions", "WbsStructure": "bad_schema"}
    )
    bid_id = create_bid(client)
    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: step_status(client, bid_id, "wbs") == "failed")

    llm = mock_llm["client"]
    assert llm.call_counts["WbsStructure"] == 3  # schema retry ≤ 2

    session = db.SessionLocal()
    try:
        step = session.query(PipelineStep).filter_by(bid_id=bid_id, step_key="wbs").one()
        assert step.status == "failed"
        assert step.error_message and "WbsStructure" in step.error_message
    finally:
        session.close()
