"""Integration checks for the M6 parse gate and B3 pipeline step."""

from __future__ import annotations

from app.core import db
from app.llm.mock_client import MockLLMClient
from app.models import Attachment, Requirement, Bid
from tests.helpers import bid_status, create_bid, step_status, wait_until
from app.api.errors import ApiError
from app.services.attachment_service import add as add_attachment
from app.services.parse_service import confirm as confirm_parse


class EvaluationFixtureClient(MockLLMClient):
    def complete(self, *, schema, prompt, context=None):
        if schema.__name__ == "EvaluationBatch":
            return {
                "batch": [
                    {
                        "req_code": code,
                        "rating": "○",
                        "needs_clarification": False,
                        "note_vi": "Đáp ứng trong phạm vi hướng hiện tại.",
                    }
                    for code in (context or {}).get("batch_codes", [])
                ]
            }
        return super().complete(schema=schema, prompt=prompt, context=context)


def test_pipeline_rejects_m6_attachment_without_parse_confirmation(client, mock_llm):
    bid_id = create_bid(client)
    session = db.SessionLocal()
    try:
        session.add(
            Attachment(
                bid_id=bid_id,
                filename="requirements.csv",
                file_type="requirement",
                detected_type="requirement",
                size_bytes=10,
                path="data/uploads/test/requirements.csv",
            )
        )
        session.commit()
    finally:
        session.close()

    response = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "STATE_CONFLICT"
    assert "xác nhận" in response.json()["error"]["message"]


def test_confirm_rejects_attachment_before_successful_parse(client):
    bid_id = create_bid(client)
    session = db.SessionLocal()
    try:
        add_attachment(session, bid_id, "requirements.csv", b"content\nCRM")
        try:
            confirm_parse(session, bid_id, "medium", True)
        except ApiError as exc:
            assert exc.code == "STATE_CONFLICT"
        else:
            raise AssertionError("confirm must reject an attachment that was not parsed")
    finally:
        session.close()


def test_pipeline_runs_evaluation_after_gap_when_parse_is_confirmed(client, mock_llm):
    mock_llm["client"] = EvaluationFixtureClient(fixture_modes={"GapQuestions": "no_questions"})
    bid_id = create_bid(client)
    session = db.SessionLocal()
    try:
        bid = session.get(Bid, bid_id)
        assert bid is not None
        bid.data_readiness = "medium"
        session.add(
            Requirement(
                bid_id=bid_id,
                internal_code="REQ-001",
                content="Hệ thống phải hỗ trợ tra cứu dữ liệu giả lập.",
                priority="mandatory",
                category="functional",
                source_sheet="CSV",
                source_row=2,
            )
        )
        attachment = Attachment(
            bid_id=bid_id,
            filename="requirements.csv",
            file_type="requirement",
            detected_type="requirement",
            size_bytes=10,
            path="data/uploads/test/requirements.csv",
            parse_status="ok",
        )
        session.add(attachment)
        session.commit()
    finally:
        session.close()

    response = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert response.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")
    assert step_status(client, bid_id, "evaluate") == "completed"

    evaluations = client.get(f"/api/bids/{bid_id}/evaluations").json()
    assert evaluations["stats"]["total"] == 1
    assert evaluations["stats"]["evaluated"] == 1
    assert evaluations["items"][0]["req_code"] == "REQ-001"
