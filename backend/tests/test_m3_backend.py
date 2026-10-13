from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.llm import complete_with_retry
from app.llm.mock_client import MockLLMClient
from app.schemas.llm_schemas.solution_proposal import SolutionProposal
from app.services.effort_engine import calculate_effort


def _bid(**overrides):
    values = {
        "customer_language": "ja",
        "data_readiness": "low",
        "no_requirement_file": True,
        "request_content": "requirement dữ liệu lớn",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_solution_schema_rejects_forbidden_number_fields():
    with pytest.raises(ValidationError):
        SolutionProposal.model_validate({
            "direction": "rag", "reason_vi": "Lý do", "risks_vi": [],
            "architecture_notes_vi": "Ghi chú", "man_day": 8,
        })


def test_solution_mock_is_structured_and_retries_are_bounded():
    client = MockLLMClient(fixture_mode="bad_schema")
    with pytest.raises(Exception):
        complete_with_retry(client, SolutionProposal, "prompt", max_retries=2)
    assert client.call_count == 3


def test_solution_feasibility_is_qualitative():
    proposal = SolutionProposal.model_validate({
        "direction": "none",
        "reason_vi": "CRM có dữ liệu có cấu trúc",
        "risks_vi": [],
        "architecture_notes_vi": "Thiết kế nghiệp vụ truyền thống",
        "feasibility": {"technical": "khả thi với dữ liệu đã chuẩn hóa"},
    })
    assert proposal.feasibility["technical"].startswith("khả thi")
    with pytest.raises(ValidationError):
        SolutionProposal.model_validate({
            "direction": "none",
            "reason_vi": "CRM có dữ liệu có cấu trúc",
            "risks_vi": [],
            "architecture_notes_vi": "Thiết kế nghiệp vụ truyền thống",
            "feasibility": {"technical": 4},
        })


def test_solution_mock_returns_structured_risks_and_feasibility_score():
    client = MockLLMClient()
    result = complete_with_retry(
        client,
        SolutionProposal,
        "prompt",
        context={"customer_language": "ja"},
    )
    assert 4 <= len(result["risks"]) <= 6
    assert all(1 <= risk["level"] <= 5 for risk in result["risks"])
    assert {"type_vi", "level", "description_vi", "mitigation_vi"} <= set(result["risks"][0])
    assert 1 <= result["feasibility_score"]["score"] <= 5
    assert result["feasibility_score"]["reason_vi"]


def test_effort_is_deterministic_and_factor_is_capped():
    result = calculate_effort(_bid(), "rag")
    assert result["factor_product"] <= result["cap"]
    assert result["trace"]["raw_factor_product"] > result["trace"]["capped_factor_product"]
    assert set(result["by_phase"]) == {"poc", "mvp", "production"}


def test_effort_changes_by_direction_without_llm():
    bid = _bid()
    assert calculate_effort(bid, "rag")["midpoint_total"] != calculate_effort(bid, "none")["midpoint_total"]
