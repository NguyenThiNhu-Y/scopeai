from app.core import db
from app.llm.mock_client import MockLLMClient
from app.models import Requirement
from app.services.evaluation_service import evaluate
from tests.helpers import create_bid


class BatchClient(MockLLMClient):
    def __init__(self):
        super().__init__()
        self.batch_sizes = []

    def complete(self, *, schema, prompt, context=None):
        if schema.__name__ == "EvaluationBatch":
            self.call_count += 1
            self.call_counts["EvaluationBatch"] = self.call_counts.get("EvaluationBatch", 0) + 1
            self.batch_sizes.append(len((context or {}).get("batch_codes", [])))
            return {
                "batch": [
                    {
                        "req_code": code,
                        "rating": "○",
                        "needs_clarification": False,
                        "note_vi": "Đánh giá giả lập.",
                    }
                    for code in (context or {}).get("batch_codes", [])
                ]
            }
        return super().complete(schema=schema, prompt=prompt, context=context)


class RecordingClient(MockLLMClient):
    """Ghi lại prompt SAU khi che PII — đúng thứ provider thật nhận được."""

    def __init__(self):
        super().__init__()
        self.prompts = []

    def complete(self, *, schema, prompt, context=None):
        result = super().complete(schema=schema, prompt=prompt, context=context)
        self.prompts.append(self.last_prompt)
        return result


def test_235_requirements_are_evaluated_in_batches_of_at_most_40(client):
    bid_id = create_bid(client)
    session = db.SessionLocal()
    try:
        for index in range(235):
            session.add(
                Requirement(
                    bid_id=bid_id,
                    internal_code=f"REQ-{index + 1:03d}",
                    content=f"Yêu cầu giả lập {index + 1}",
                    priority="mandatory",
                    category="functional",
                    source_sheet="CSV",
                    source_row=index + 2,
                )
            )
        session.commit()
        client_llm = BatchClient()
        result = evaluate(session, bid_id, client=client_llm)
        assert result["total"] == 235
        assert client_llm.call_counts["EvaluationBatch"] == 6
        assert client_llm.batch_sizes == [40, 40, 40, 40, 40, 35]
    finally:
        session.close()


def test_evaluation_prompt_contains_requirement_codes_and_content(client):
    """Prompt thật phải chứa mã + nội dung requirement (provider openai_compat
    chỉ gửi prompt, không gửi context) và PII phải được che (BR-06)."""
    bid_id = create_bid(client)
    session = db.SessionLocal()
    try:
        session.add(
            Requirement(
                bid_id=bid_id,
                internal_code="REQ-001",
                content="Hệ thống phải hỗ trợ tra cứu khách hàng, liên hệ qua email support@example.com.",
                priority="mandatory",
                category="functional",
            )
        )
        session.add(
            Requirement(
                bid_id=bid_id,
                internal_code="REQ-002",
                content="Yêu cầu báo cáo theo tháng.",
                priority="optional",
                category="non_functional",
            )
        )
        session.commit()
        llm = RecordingClient()
        result = evaluate(session, bid_id, direction="rag", client=llm)
        assert result["total"] == 2
        assert llm.prompts, "evaluate phải gọi LLM"
        prompt = llm.prompts[0]
        assert "REQ-001" in prompt and "REQ-002" in prompt
        assert "tra cứu khách hàng" in prompt
        assert "báo cáo theo tháng" in prompt
        assert "support@example.com" not in prompt
        assert "[EMAIL]" in prompt
    finally:
        session.close()
