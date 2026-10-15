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


def _valid_ja_localized():
    # LLM dịch luôn khóa sections sang tiếng Nhật (lỗi thực tế B6 khi khách ja).
    return {
        "sections": {
            "はじめに": "…",
            "ご要件の理解": "…",
            "提案概要": "…",
            "進め方": "…",
            "スケジュール": "…",
            "体制": "…",
            "前提条件・対象外": "…",
            "リスク": "… {{QUOTATION}}",
        },
        "assumptions_phrased": [],
        "scope_out_phrased": [],
    }


def test_proposal_schema_accepts_localized_japanese_keys():
    parsed = ProposalOutput.model_validate(_valid_ja_localized())
    assert set(parsed.sections) == {
        "introduction", "requirements_understanding", "solution_overview",
        "approach", "schedule", "team", "assumptions_and_scope", "risks",
    }


def test_proposal_schema_accepts_vietnamese_localized_keys():
    value = _valid()
    value["sections"] = {
        "Giới thiệu": "…",
        "Hiểu yêu cầu": "…",
        "Tổng quan giải pháp": "…",
        "Cách tiếp cận": "…",
        "Lịch trình": "…",
        "Đội ngũ": "…",
        "Giả định và phạm vi": "…",
        "Rủi ro": "… {{QUOTATION}}",
    }
    parsed = ProposalOutput.model_validate(value)
    assert parsed.sections["introduction"]


def test_proposal_schema_accepts_english_title_case_keys():
    value = _valid()
    value["sections"] = {
        "Introduction": "…",
        "Requirements Understanding": "…",
        "Solution Overview": "…",
        "Approach": "…",
        "Schedule": "…",
        "Team": "…",
        "Assumptions and Scope": "…",
        "Risks": "… {{QUOTATION}}",
    }
    parsed = ProposalOutput.model_validate(value)
    assert parsed.sections["assumptions_and_scope"]


def test_proposal_schema_rejects_missing_section_with_localized_keys():
    value = _valid_ja_localized()
    del value["sections"]["リスク"]
    with pytest.raises(ValidationError):
        ProposalOutput.model_validate(value)


def test_proposal_schema_rejects_unknown_localized_key():
    value = _valid_ja_localized()
    value["sections"]["その他"] = "…"
    with pytest.raises(ValidationError):
        ProposalOutput.model_validate(value)
