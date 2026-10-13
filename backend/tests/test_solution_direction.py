import pytest
from pydantic import ValidationError

from app.llm import complete_with_retry
from app.llm.mock_client import MockLLMClient
from app.schemas.llm_schemas.solution_proposal import SolutionProposal


def test_solution_direction_enum_is_fixed():
    for direction in ("none", "traditional_ml", "rag", "agent", "fine_tune"):
        proposal = SolutionProposal.model_validate(
            {
                "direction": direction,
                "reason_vi": "Lý do hợp lệ",
                "risks_vi": [],
                "architecture_notes_vi": "Ghi chú hợp lệ",
            }
        )
        assert proposal.direction.value == direction


def test_invalid_solution_direction_is_rejected():
    with pytest.raises(ValidationError):
        SolutionProposal.model_validate(
            {
                "direction": "invalid",
                "reason_vi": "Lý do hợp lệ",
                "risks_vi": [],
                "architecture_notes_vi": "Ghi chú hợp lệ",
            }
        )


def test_bad_schema_retries_twice_then_fails():
    client = MockLLMClient(fixture_mode="bad_schema")

    with pytest.raises(Exception):
        complete_with_retry(client, SolutionProposal, "prompt", max_retries=2)

    assert client.call_count == 3


def test_forbidden_number_field_is_not_persistable():
    with pytest.raises(ValidationError):
        SolutionProposal.model_validate(
            {
                "direction": "rag",
                "reason_vi": "Lý do",
                "risks_vi": [],
                "architecture_notes_vi": "Ghi chú",
                "man_day": 8,
            }
        )
