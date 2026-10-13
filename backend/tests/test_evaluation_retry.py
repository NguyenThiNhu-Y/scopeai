import pytest

from app.llm.gateway import LLMSchemaError, complete_with_retry
from app.schemas.llm_schemas.evaluation import EvaluationBatch


class BadSchemaClient:
    def __init__(self):
        self.calls = 0

    def complete(self, *, schema, prompt, context=None):
        self.calls += 1
        return {"batch": [{"req_code": "REQ-001", "rating": "invalid"}]}


def test_bad_evaluation_schema_retries_at_most_two_times():
    client = BadSchemaClient()
    with pytest.raises(LLMSchemaError):
        complete_with_retry(client, EvaluationBatch, "Đánh giá giả lập", max_retries=2)
    assert client.calls == 3
