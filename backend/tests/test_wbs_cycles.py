"""Tests phát hiện vòng phụ thuộc (DFS), tự tham chiếu, depends_on mã lạ.

- Vòng phụ thuộc → lỗi NGỮ NGHĨA (check_engine) → retry ≤ 2 → cảnh báo.
- Tự tham chiếu / mã lạ → lỗi SCHEMA (WbsStructure) → fail rõ.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.llm_schemas.wbs_structure import WbsStructure
from app.services import check_engine, wbs_engine

BY_PHASE = {
    "poc": {"min": 8, "max": 12},
    "mvp": {"min": 20, "max": 30},
    "production": {"min": 10, "max": 16},
}


def _enriched(mode: str) -> list[dict]:
    from app.llm.mock_client import get_fixture

    raw = get_fixture(WbsStructure, mode)
    tasks = WbsStructure.model_validate(raw).model_dump(mode="json")["tasks"]
    tasks = wbs_engine.assign_man_days(tasks, BY_PHASE)
    return wbs_engine.enrich_items(tasks)


def test_cycle_detected_by_check_engine():
    """A depends B, B depends A → cycle_free=false + warning."""
    check = check_engine.check_wbs(_enriched("cycle"), 48.0, BY_PHASE)
    assert check["cycle_free"] is False
    assert check["warning"] and "vòng" in check["warning"].lower()


def test_no_cycle_in_good_wbs():
    check = check_engine.check_wbs(_enriched("good"), 48.0, BY_PHASE)
    assert check["cycle_free"] is True


def test_self_reference_rejected_by_schema():
    """Task phụ thuộc chính nó → ValidationError (schema)."""
    payload = {
        "tasks": [
            {"task_code": "WBS-001", "name_vi": "PoC", "phase": "poc",
             "parent_code": None, "role": None, "weight": None, "depends_on": []},
            {"task_code": "WBS-001-01", "name_vi": "Lá", "phase": "poc",
             "parent_code": "WBS-001", "role": "pm", "weight": 20,
             "depends_on": ["WBS-001-01"]},
        ],
        "notes_vi": [],
    }
    with pytest.raises(ValidationError):
        WbsStructure.model_validate(payload)


def test_unknown_dependency_rejected_by_schema():
    """depends_on trỏ mã không tồn tại → ValidationError (schema)."""
    payload = {
        "tasks": [
            {"task_code": "WBS-001", "name_vi": "PoC", "phase": "poc",
             "parent_code": None, "role": None, "weight": None, "depends_on": []},
            {"task_code": "WBS-001-01", "name_vi": "Lá", "phase": "poc",
             "parent_code": "WBS-001", "role": "pm", "weight": 20,
             "depends_on": ["WBS-999"]},
        ],
        "notes_vi": [],
    }
    with pytest.raises(ValidationError):
        WbsStructure.model_validate(payload)


def test_duplicate_task_code_rejected():
    payload = {
        "tasks": [
            {"task_code": "WBS-001", "name_vi": "A", "phase": "poc",
             "parent_code": None, "role": None, "weight": None, "depends_on": []},
            {"task_code": "WBS-001", "name_vi": "B", "phase": "poc",
             "parent_code": None, "role": None, "weight": None, "depends_on": []},
        ],
        "notes_vi": [],
    }
    with pytest.raises(ValidationError):
        WbsStructure.model_validate(payload)


def test_depth_over_three_rejected():
    payload = {
        "tasks": [
            {"task_code": "WBS-001", "name_vi": "C1", "phase": "poc",
             "parent_code": None, "role": None, "weight": None, "depends_on": []},
            {"task_code": "WBS-001-01", "name_vi": "C2", "phase": "poc",
             "parent_code": "WBS-001", "role": None, "weight": None, "depends_on": []},
            {"task_code": "WBS-001-01-01", "name_vi": "C3", "phase": "poc",
             "parent_code": "WBS-001-01", "role": None, "weight": None, "depends_on": []},
            {"task_code": "WBS-001-01-01-01", "name_vi": "C4", "phase": "poc",
             "parent_code": "WBS-001-01-01", "role": "pm", "weight": 20, "depends_on": []},
        ],
        "notes_vi": [],
    }
    with pytest.raises(ValidationError):
        WbsStructure.model_validate(payload)