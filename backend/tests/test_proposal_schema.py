import pytest
from pydantic import ValidationError

from app.schemas.llm_schemas.proposal import ProposalOutput


def _valid():
    return {"sections": {"introduction": "Giới thiệu", "requirements_understanding": "Hiểu yêu cầu", "solution_overview": "Giải pháp", "approach": "Cách làm", "schedule": "Lịch", "team": "Đội ngũ", "assumptions_and_scope": "Tiền đề và ngoài phạm vi", "risks": "Rủi ro {{QUOTATION}}"}, "assumptions_phrased": [], "scope_out_phrased": []}


def test_proposal_schema_accepts_clean_output():
    assert ProposalOutput.model_validate(_valid()).sections["introduction"]


def test_proposal_schema_rejects_extra_field():
    value = _valid()
    value["money"] = 100
    with pytest.raises(ValidationError):
        ProposalOutput.model_validate(value)
