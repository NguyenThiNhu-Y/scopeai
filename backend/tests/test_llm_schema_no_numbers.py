"""BR-01: schema output LLM không chứa trường man-day/giá/ngày.

Quét MỌI schema trong ``app.schemas.llm_schemas`` (không chỉ RfpSummary)
để giữ kỷ luật khi M3+ thêm schema mới.

Lưu ý M2: ``IntakeExtraction`` có ``budget_mentioned``/``budget_note_vi`` và
``deadline_mentioned``/``deadline_note_vi`` — ngân sách/thời hạn chỉ là GHI CHÚ
VĂN BẢN + cờ boolean, KHÔNG phải trường số/ngày (llm_pipeline.md §2). Vì vậy
token "budget"/"deadline"/"date" không nằm trong danh sách cấm; thay vào đó có
assert riêng: trường chứa budget/deadline/date phải là ``_mentioned`` (bool)
hoặc ``_note_vi`` (text).
"""

from __future__ import annotations

import pydantic
import pytest

from app.schemas import llm_schemas
from app.schemas.llm_schemas import (
    GapQuestions,
    IntakeExtraction,
    RfpSummary,
    WbsStructure,
)

# Token cấm trong tên trường — LLM không được xuất con số (BR-01).
FORBIDDEN_TOKENS = (
    "man_day",
    "manday",
    "man-days",
    "effort",
    "price",
    "cost",
    "amount",
    "rate",
    "total",
    "percent",
    "yen",
    "vnd",
    "jpy",
    "usd",
    "currency",
    "quotation",
    "quote",
    "manhour",
)


def _collect_schemas() -> list[tuple[str, type[pydantic.BaseModel]]]:
    schemas = []
    for name, obj in vars(llm_schemas).items():
        if (
            isinstance(obj, type)
            and issubclass(obj, pydantic.BaseModel)
            and obj is not pydantic.BaseModel
        ):
            schemas.append((name, obj))
    return schemas


def test_every_llm_schema_has_no_number_fields():
    collected = _collect_schemas()
    assert collected, "Không tìm thấy schema nào trong app.schemas.llm_schemas"

    for name, schema in collected:
        for field_name in schema.model_fields:
            lowered = field_name.lower()
            for token in FORBIDDEN_TOKENS:
                assert token not in lowered, (
                    f"Schema {name} chứa trường '{field_name}' — vi phạm BR-01 "
                    f"(LLM không được xuất man-day/giá/ngày)"
                )


def test_budget_deadline_only_as_flags_or_text_notes():
    """Budget/deadline/date chỉ xuất hiện dạng ``_mentioned`` (bool) hoặc ``_note_vi`` (text)."""
    for name, schema in _collect_schemas():
        for field_name, field_info in schema.model_fields.items():
            lowered = field_name.lower()
            if any(token in lowered for token in ("budget", "deadline", "date")):
                assert lowered.endswith("_mentioned") or lowered.endswith("_note_vi"), (
                    f"Schema {name} chứa trường '{field_name}' — budget/deadline/date "
                    f"chỉ được là cờ boolean (_mentioned) hoặc ghi chú văn bản (_note_vi)"
                )


def test_rfp_summary_rejects_extra_number_field():
    """Payload chứa man_day bị từ chối ngay ở lớp schema (extra=forbid)."""
    with pytest.raises(pydantic.ValidationError):
        RfpSummary.model_validate(
            {
                "summary_vi": "Tóm tắt (giả lập).",
                "keywords": ["a"],
                "notes": ["b"],
                "man_day": 8,
            }
        )


def test_intake_extraction_rejects_extra_number_field():
    """BR-01: IntakeExtraction chặn trường man_day (extra=forbid)."""
    payload = {
        "objectives_vi": "Mục tiêu (giả lập).",
        "users_vi": "Người dùng (giả lập).",
        "data_vi": "Dữ liệu (giả lập).",
        "constraints_vi": [],
        "budget_mentioned": False,
        "budget_note_vi": "",
        "deadline_mentioned": False,
        "deadline_note_vi": "",
        "customer_language_detected": "ja",
        "summary_vi": "Tóm tắt (giả lập).",
        "keywords": [],
        "notes": [],
        "man_day": 8,
    }
    with pytest.raises(pydantic.ValidationError):
        IntakeExtraction.model_validate(payload)


def test_intake_extraction_requires_note_when_mentioned():
    """budget_note_vi bắt buộc khi budget_mentioned=true (llm_pipeline.md §2)."""
    payload = {
        "objectives_vi": "Mục tiêu (giả lập).",
        "users_vi": "Người dùng (giả lập).",
        "data_vi": "Dữ liệu (giả lập).",
        "constraints_vi": [],
        "budget_mentioned": True,
        "budget_note_vi": "",
        "deadline_mentioned": False,
        "deadline_note_vi": "",
        "customer_language_detected": "ja",
        "summary_vi": "Tóm tắt (giả lập).",
        "keywords": [],
        "notes": [],
    }
    with pytest.raises(pydantic.ValidationError):
        IntakeExtraction.model_validate(payload)


def test_gap_questions_consistency_rules():
    """needs_clarification=false → questions rỗng; true → có câu hỏi (llm_pipeline.md §3)."""
    with pytest.raises(pydantic.ValidationError):
        GapQuestions.model_validate(
            {"needs_clarification": False, "questions": [{"question": "?", "reason_vi": "vì sao", "impact": "effort"}]}
        )
    with pytest.raises(pydantic.ValidationError):
        GapQuestions.model_validate({"needs_clarification": True, "questions": []})


def test_wbs_structure_rejects_man_day_field():
    """BR-01 (M4): fixture with_man_day bị chặn ngay ở lớp schema (extra=forbid)."""
    from app.llm.mock_client import get_fixture

    payload = get_fixture(WbsStructure, "with_man_day")
    with pytest.raises(pydantic.ValidationError):
        WbsStructure.model_validate(payload)


def test_wbs_structure_rejects_any_forbidden_number_field():
    """BR-01 (M4): mọi field số/ngày (effort/price/date/...) bị chặn."""
    base = {
        "task_code": "WBS-001",
        "name_vi": "PoC",
        "phase": "poc",
        "parent_code": None,
        "role": "pm",
        "weight": 20,
        "depends_on": [],
    }
    for forbidden in ("effort", "price", "cost", "amount", "date", "schedule", "midpoint", "min", "max"):
        payload = {"tasks": [{**base, forbidden: 1}], "notes_vi": []}
        with pytest.raises(pydantic.ValidationError):
            WbsStructure.model_validate(payload)


def test_wbs_structure_good_fixture_validates():
    """Fixture good (M4) hợp lệ — không chứa man_day trong payload LLM."""
    from app.llm.mock_client import get_fixture

    payload = get_fixture(WbsStructure, "good")
    obj = WbsStructure.model_validate(payload)
    for task in obj.tasks:
        assert "man_day" not in task.model_dump()
    assert obj.tasks  # có task