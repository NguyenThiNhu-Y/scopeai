"""Tests WbsEngine — gán man-day lá từ midpoint, tổng phase, cân bằng làm tròn.

AGENTS.md rule 1 (No invented numbers): man-day lá do CODE gán từ midpoint
bảng chuẩn (≤ 10); schema WbsStructure không có field số/ngày (BR-01).
"""

from __future__ import annotations

from app.llm.mock_client import get_fixture
from app.schemas.llm_schemas.wbs_structure import WbsStructure
from app.services import wbs_engine

# Dải effort rag × factor 1.0 (không hệ số) — midpoint: poc 10, mvp 25, prod 13.
BY_PHASE = {
    "poc": {"min": 8, "max": 12},
    "mvp": {"min": 20, "max": 30},
    "production": {"min": 10, "max": 16},
}
MIDPOINT_TOTAL = 48.0


def _tasks(mode: str = "good") -> list[dict]:
    raw = get_fixture(WbsStructure, mode)
    return WbsStructure.model_validate(raw).model_dump(mode="json")["tasks"]


def _enriched(mode: str = "good") -> list[dict]:
    tasks = wbs_engine.assign_man_days(_tasks(mode), BY_PHASE)
    return wbs_engine.enrich_items(tasks)


def test_leaf_man_day_assigned_by_code_and_leq_10():
    """Mọi task lá man_day ≤ 10 và do code gán (không có trong payload LLM)."""
    enriched = _enriched("good")
    leaves = [i for i in enriched if i["is_leaf"]]
    assert leaves, "Phải có task lá"
    for leaf in leaves:
        assert leaf["man_day"] is not None
        assert leaf["man_day"] <= 10, f"Lá {leaf['task_code']} vượt 10 man-day"
    # Payload LLM gốc KHÔNG chứa man_day (BR-01).
    raw_tasks = _tasks("good")
    assert all("man_day" not in t for t in raw_tasks)


def test_phase_totals_match_midpoint():
    """Tổng man-day mỗi phase khớp midpoint phase (sai số làm tròn ≤ 0.2)."""
    enriched = _enriched("good")
    leaves = [i for i in enriched if i["is_leaf"]]
    for phase, target in (("poc", 10.0), ("mvp", 25.0), ("production", 13.0)):
        total = round(sum(i["man_day"] for i in leaves if i["phase"] == phase), 1)
        assert abs(total - target) <= 0.2, f"Phase {phase}: {total} vs {target}"


def test_total_equals_midpoint_total():
    enriched = _enriched("good")
    leaves = [i for i in enriched if i["is_leaf"]]
    total = round(sum(i["man_day"] for i in leaves), 1)
    assert abs(total - MIDPOINT_TOTAL) <= 0.2


def test_depth_max_three_levels():
    enriched = _enriched("good")
    levels = {i["level"] for i in enriched}
    assert levels <= {1, 2, 3}
    assert 3 in levels  # fixture good có đủ 3 cấp


def test_parent_man_day_equals_sum_of_children():
    enriched = _enriched("good")
    by_code = {i["task_code"]: i for i in enriched}
    for item in enriched:
        if not item["is_leaf"]:
            children = [i for i in enriched if i["parent_code"] == item["task_code"]]
            expected = round(sum(i["man_day"] or 0 for i in children), 1)
            assert item["man_day"] == expected, item["task_code"]


def test_rounding_balance_keeps_phase_sum_exact():
    """Cân bằng sai số làm tròn vào lá lớn nhất → tổng phase khớp target."""
    tasks = _tasks("good")
    tasks = wbs_engine.assign_man_days(tasks, BY_PHASE)
    enriched = wbs_engine.enrich_items(tasks)
    leaves = [i for i in enriched if i["is_leaf"]]
    for phase, target in (("poc", 10.0), ("mvp", 25.0), ("production", 13.0)):
        total = round(sum(i["man_day"] for i in leaves if i["phase"] == phase), 1)
        assert abs(total - target) <= 0.2


def test_flat_ok_two_levels_valid():
    """Fixture good/flat_ok: WBS 2 cấp hợp lệ — lá ≤ 10, đủ PM/QA."""
    enriched = _enriched("flat_ok")
    leaves = [i for i in enriched if i["is_leaf"]]
    assert all(i["level"] <= 2 for i in enriched)
    assert all(i["man_day"] <= 10 for i in leaves)
    assert {i["role"] for i in leaves if i["phase"] == "poc"} >= {"pm", "qa"}


def test_leaf_too_heavy_fixture_produces_over_10():
    """Fixture leaf_too_heavy: trọng số khiến lá > 10 → engine KHÔNG tự cắt
    (check_engine sẽ cảnh báo — retry ≤ 2)."""
    enriched = _enriched("leaf_too_heavy")
    leaves = [i for i in enriched if i["is_leaf"]]
    assert any(i["man_day"] > 10 for i in leaves)