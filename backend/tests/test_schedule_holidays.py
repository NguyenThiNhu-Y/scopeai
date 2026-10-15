"""Tests ScheduleEngine với nghỉ lễ — 2026-11-03, 2026-11-23 (Nhật) bị trừ.

holidays.yaml là dữ liệu cấu hình (FR-060 ở M8); test dùng mẫu nghỉ lễ Nhật
thật để chứng minh code trừ đúng ngày làm việc.
"""

from __future__ import annotations

from datetime import date

from app.services import schedule_engine, wbs_engine
from app.services.reference_service import load_holidays
from tests.helpers import default_team_allocation

BY_PHASE = {
    "poc": {"min": 8, "max": 12},
    "mvp": {"min": 20, "max": 30},
    "production": {"min": 10, "max": 16},
}


def _enriched_good() -> list[dict]:
    from app.llm.mock_client import get_fixture
    from app.schemas.llm_schemas.wbs_structure import WbsStructure

    raw = get_fixture(WbsStructure, "good")
    tasks = WbsStructure.model_validate(raw).model_dump(mode="json")["tasks"]
    tasks = wbs_engine.assign_man_days(tasks, BY_PHASE)
    return wbs_engine.enrich_items(tasks)


def _schedule_jp() -> dict:
    return schedule_engine.compute_schedule(
        items=_enriched_good(),
        start_date=date(2026, 11, 1),
        buffer_days=0,
        team_allocation=default_team_allocation(),
        working_calendar="jp",
        payment_milestones=[],
        holidays=load_holidays(),
        submission_deadline=date(2026, 12, 31),
    )


def test_jp_holidays_included_in_yaml():
    holidays = load_holidays()
    assert "2026-11-03" in holidays["jp"]  # 文化の日
    assert "2026-11-23" in holidays["jp"]  # 勤労感謝の日


def test_holidays_excluded_from_working_days():
    """Ngày 11-03 (nghỉ lễ Nhật) không được dùng làm ngày bắt đầu/kết thúc task."""
    result = _schedule_jp()
    assert result["tasks"][0]["start_date"] == "2026-11-02"
    starts = {t["start_date"] for t in result["tasks"]}
    ends = {t["end_date"] for t in result["tasks"]}
    assert "2026-11-03" not in starts, "Task không được bắt đầu vào ngày nghỉ lễ"
    assert "2026-11-03" not in ends, "Task không được kết thúc vào ngày nghỉ lễ"
    # Task kế tiếp (sau nghỉ lễ) bắt đầu 11-04 — ngày nghỉ bị trừ khỏi lịch.
    assert "2026-11-04" in starts


def test_add_working_days_skips_holiday():
    """Unit: 3 ngày làm việc từ 02-11 (nghỉ 03-11) → kết thúc 05-11."""
    holidays = {date(2026, 11, 3)}
    end = schedule_engine.add_working_days(date(2026, 11, 2), 3, holidays)
    assert end == date(2026, 11, 5)


def test_holidays_applied_reported():
    result = _schedule_jp()
    assert "2026-11-03" in result["holidays_applied"]
    assert "2026-11-23" in result["holidays_applied"]


def test_vn_calendar_does_not_apply_jp_holidays():
    result = schedule_engine.compute_schedule(
        items=_enriched_good(),
        start_date=date(2026, 11, 1),
        buffer_days=0,
        team_allocation=default_team_allocation(),
        working_calendar="vn",
        payment_milestones=[],
        holidays=load_holidays(),
        submission_deadline=date(2026, 12, 31),
    )
    assert "2026-11-03" not in result["holidays_applied"]


def test_weekend_always_off():
    """Cuối tuần + nghỉ lễ không được tính vào duration — số ngày làm việc == duration."""
    from datetime import timedelta

    allocation = default_team_allocation()
    holidays = {date.fromisoformat(d) for d in load_holidays()["jp"]}
    result = _schedule_jp()
    for t in result["tasks"]:
        start = date.fromisoformat(t["start_date"])
        end = date.fromisoformat(t["end_date"])
        working = sum(
            1
            for i in range((end - start).days + 1)
            if (start + timedelta(days=i)).weekday() < 5
            and (start + timedelta(days=i)) not in holidays
        )
        expected = -(-t["man_day"] // allocation[t["role"]])  # ceil(md / headcount)
        assert working == expected, (
            f"{t['task_code']}: span {start}..{end} có {working} ngày làm việc, "
            f"cần {expected}"
        )