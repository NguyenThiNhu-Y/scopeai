"""Tests cho persist/resume pipeline — FR-023 (contract §5.1/§5.3)."""

from __future__ import annotations

import time

from app.core import db
from app.llm.gateway import LLMSchemaError
from app.llm.mock_client import MockLLMClient
from app.models import PipelineStep
from tests.helpers import bid_status, create_bid, step_status, wait_until

STEP_KEYS = ["intake", "gap", "solution", "evaluate", "wbs", "proposal"]


class FailingOnceClient(MockLLMClient):
    """Fail đúng 1 lần cho schema chỉ định (raise LLMSchemaError) rồi trả fixture tốt."""

    def __init__(self, fail_schema: str, **kwargs):
        super().__init__(**kwargs)
        self.fail_schema = fail_schema
        self.failed = False

    def complete(self, **kwargs):
        name = kwargs["schema"].__name__
        if name == self.fail_schema and not self.failed:
            self.failed = True
            raise LLMSchemaError(f"Output LLM không đúng schema {name} (giả lập)")
        return super().complete(**kwargs)


class SlowMockClient(MockLLMClient):
    """Client chậm — pipeline chạy nền đủ lâu để test guard 409."""

    def __init__(self, delay: float = 0.5, **kwargs):
        super().__init__(**kwargs)
        self.delay = delay

    def complete(self, **kwargs):
        time.sleep(self.delay)
        return super().complete(**kwargs)


class ProviderErrorClient(MockLLMClient):
    """Mô phỏng lỗi provider (mạng/timeout) — KHÔNG phải LLMSchemaError.

    M-1 (review): lỗi ngoài schema phải đánh dấu bước failed để rerun cứu được.
    """

    def __init__(self, fail_schema: str, **kwargs):
        super().__init__(**kwargs)
        self.fail_schema = fail_schema
        self.failed = False

    def complete(self, **kwargs):
        name = kwargs["schema"].__name__
        if name == self.fail_schema and not self.failed:
            self.failed = True
            raise RuntimeError("LLM provider mất kết nối (giả lập)")
        return super().complete(**kwargs)


def _steps(session, bid_id: int) -> dict[str, PipelineStep]:
    rows = session.query(PipelineStep).filter(PipelineStep.bid_id == bid_id).all()
    return {s.step_key: s for s in rows}


def test_start_registers_all_steps(client, mock_llm):
    """Đăng ký các bước thực tế và hoàn tất proposal."""
    mock_llm["client"] = MockLLMClient(fixture_modes={"GapQuestions": "no_questions"})
    bid_id = create_bid(client)
    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    data = resp.json()
    assert data["bid_id"] == bid_id
    assert data["status"] == "analyzing"
    assert {s["step_key"] for s in data["steps"]} == set(STEP_KEYS)

    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")

    session = db.SessionLocal()
    try:
        steps = _steps(session, bid_id)
        assert set(steps) == set(STEP_KEYS)
        assert steps["proposal"].status == "completed"
        for key in ("intake", "gap", "solution", "wbs"):
            assert steps[key].status == "completed"
    finally:
        session.close()


def test_rerun_from_intake_after_failure(client, mock_llm):
    """Intake fail → rerun (from_step=null) chạy lại từ intake → thành công."""
    mock_llm["client"] = FailingOnceClient(
        fail_schema="IntakeExtraction", fixture_modes={"GapQuestions": "no_questions"}
    )
    bid_id = create_bid(client)

    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: step_status(client, bid_id, "intake") == "failed")

    session = db.SessionLocal()
    try:
        step = _steps(session, bid_id)["intake"]
        assert step.error_message and "IntakeExtraction" in step.error_message
    finally:
        session.close()

    resp = client.post(f"/api/bids/{bid_id}/rerun", json={"from_step": None, "reason": "Resume sau lỗi"})
    assert resp.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")

    session = db.SessionLocal()
    try:
        step = _steps(session, bid_id)["intake"]
        assert step.status == "completed"
        assert step.attempts == 2  # lần đầu fail + lần rerun
        assert step.error_message is None
    finally:
        session.close()


def test_rerun_from_gap_keeps_completed_steps(client, mock_llm):
    """Gap fail → rerun từ gap; intake completed KHÔNG chạy lại."""
    mock_llm["client"] = FailingOnceClient(
        fail_schema="GapQuestions", fixture_modes={"GapQuestions": "no_questions"}
    )
    bid_id = create_bid(client)

    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: step_status(client, bid_id, "gap") == "failed")
    assert step_status(client, bid_id, "intake") == "completed"

    client_llm = mock_llm["client"]
    assert client_llm.call_counts["IntakeExtraction"] == 1

    resp = client.post(f"/api/bids/{bid_id}/rerun", json={"from_step": None})
    assert resp.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")

    # Intake không bị gọi lại (completed giữ nguyên).
    assert client_llm.call_counts["IntakeExtraction"] == 1
    session = db.SessionLocal()
    try:
        steps = _steps(session, bid_id)
        assert steps["intake"].status == "completed"
        assert steps["intake"].attempts == 1
        assert steps["gap"].status == "completed"
        assert steps["gap"].attempts == 2
    finally:
        session.close()


def test_provider_error_marks_step_failed_and_rerunnable(client, mock_llm):
    """M-1 (review): lỗi provider (không phải schema) → bước failed + rerun cứu được."""
    mock_llm["client"] = ProviderErrorClient(
        fail_schema="IntakeExtraction", fixture_modes={"GapQuestions": "no_questions"}
    )
    bid_id = create_bid(client)

    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: step_status(client, bid_id, "intake") == "failed")

    session = db.SessionLocal()
    try:
        step = _steps(session, bid_id)["intake"]
        assert step.error_message and "mất kết nối" in step.error_message
    finally:
        session.close()

    # Rerun từ bước failed → thành công (client hết lỗi).
    resp = client.post(f"/api/bids/{bid_id}/rerun", json={"from_step": None})
    assert resp.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")


def test_rerun_without_failed_step_returns_422(client, mock_llm):
    """Không có bước failed → rerun trả 422 PIPELINE_ERROR."""
    mock_llm["client"] = MockLLMClient(fixture_modes={"GapQuestions": "no_questions"})
    bid_id = create_bid(client)
    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")

    resp = client.post(f"/api/bids/{bid_id}/rerun", json={"from_step": None})
    assert resp.status_code == 422
    body = resp.json()["error"]
    assert body["code"] == "PIPELINE_ERROR"
    assert body["details"]["step"] is None


def test_409_state_conflict_while_running(client, mock_llm):
    """Guard 409 STATE_CONFLICT khi pipeline đang chạy."""
    mock_llm["client"] = SlowMockClient(
        delay=0.5, fixture_modes={"GapQuestions": "no_questions"}
    )
    bid_id = create_bid(client)

    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202

    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "STATE_CONFLICT"

    resp = client.post(f"/api/bids/{bid_id}/rerun", json={"from_step": None})
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "STATE_CONFLICT"

    # Chờ pipeline chạy xong để không rò rỉ task sang test sau.
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval", timeout=8.0)


def test_409_clarify_pending_with_unanswered_questions(client, mock_llm):
    """Guard 409 CLARIFY_PENDING khi còn câu hỏi chưa trả lời."""
    bid_id = create_bid(client)
    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_clarification")

    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 409
    body = resp.json()["error"]
    assert body["code"] == "CLARIFY_PENDING"
