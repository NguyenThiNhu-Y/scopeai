from __future__ import annotations

import asyncio

from app.core import db
from app.llm.mock_client import MockLLMClient
from app.models import Attachment, PipelineStep, Requirement
from app.pipeline.steps.b1_intake import run_intake
from app.pipeline.steps.b2_gap import run_gap
from app.pipeline.steps.b4_solution import run_solution
from tests.helpers import create_bid


class ContextClient(MockLLMClient):
    def __init__(self):
        super().__init__(fixture_modes={"GapQuestions": "no_questions"})
        self.contexts: list[tuple[str, dict]] = []

    def complete(self, *, schema, prompt, context=None):
        self.contexts.append((schema.__name__, context or {}))
        return super().complete(schema=schema, prompt=prompt, context=context)


def _register_steps(session, bid_id: int) -> None:
    for step_key in ("intake", "gap", "solution", "evaluate", "wbs", "proposal", "ja_check"):
        session.add(PipelineStep(bid_id=bid_id, step_key=step_key, status="pending"))


def test_intake_and_gap_send_rfp_and_requirement_context(client, tmp_path):
    bid_id = create_bid(client)
    path = tmp_path / "rfp.txt"
    path.write_text("RFP nội bộ có email customer@example.com", encoding="utf-8")
    session = db.SessionLocal()
    try:
        _register_steps(session, bid_id)
        session.add(Attachment(bid_id=bid_id, filename="rfp.txt", file_type="rfp", detected_type="text", size_bytes=10, path=str(path), parse_status="ok"))
        session.add(Requirement(bid_id=bid_id, internal_code="REQ-001", content="Yêu cầu CRM", priority="mandatory", category="functional"))
        session.commit()
    finally:
        session.close()

    llm = ContextClient()
    asyncio.run(run_intake(bid_id, llm))
    asyncio.run(run_gap(bid_id, llm))
    for schema_name, context in llm.contexts:
        if schema_name in {"IntakeExtraction", "GapQuestions"}:
            assert context["requirement_count"] == 1
            assert context["requirements"][0]["req_code"] == "REQ-001"
            assert context["rfp_files"][0]["filename"] == "rfp.txt"
            assert "customer@example.com" not in context["rfp_files"][0]["text"]


def test_solution_context_is_complete(client):
    bid_id = create_bid(client)
    session = db.SessionLocal()
    try:
        _register_steps(session, bid_id)
        session.add(Requirement(bid_id=bid_id, internal_code="REQ-001", content="Yêu cầu CRM", priority="mandatory", category="functional"))
        session.commit()
    finally:
        session.close()
    llm = ContextClient()
    asyncio.run(run_intake(bid_id, llm))
    asyncio.run(run_solution(bid_id, llm))
    context = next(context for name, context in llm.contexts if name == "SolutionProposal")
    assert {"intake", "questions_and_answers", "requirements_summary", "sample_profile"} <= set(context)
