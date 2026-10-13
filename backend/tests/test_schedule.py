"""Tests ScheduleEngine — WBS × headcount, phase tuần tự, buffer, mốc thanh toán.

Mọi số do code tính (AGENTS.md rule 1); engine không gọi LLM (rule 3).
"""

from __future__ import annotations

from datetime import date

from app.services import schedule_engine, wbs_engine
from app.services.reference_service import load_holidays, load_payment
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


def _schedule(
    *,
    start_date: date = date(2026, 11, 1),
    buffer_days: int = 0,
    team_allocation: dict | None = None,
    working_calendar: str = "vn",
    payment_milestones: list | None = None,
    submission_deadline: date = date(2026, 12, 31),
) -> dict:
    return schedule_engine.compute_schedule(
        items=_enriched_good(),
        start_date=start_date,
        buffer_days=buffer_days,
        team_allocation=team_allocation or default_team_allocation(),
        working_calendar=working_calendar,
        payment_milestones=payment_milestones or load_payment()["milestones"],
        holidays=load_holidays(),
    )


def test_phases_run_sequentially():
    result = _schedule()
    phase_order = {"poc": 0, "mvp": 1, "production": 2}
    tasks = result["tasks"]
    last_phase_idx = -1
    for t in tasks:
        idx = phase_order[t["phase"]]
        assert idx >= last_phase_idx, "Phase phải chạy tuần tự poc → mvp → production"
        last_phase_idx = idx


def test_task_duration_uses_headcount():
    """duration = ceil(man_day ÷ headcount); backend headcount 2 → duration nửa."""
    result = _schedule()
    backend_tasks = [t for t in result["tasks"] if t["role"] == "backend"]
    assert backend_tasks
    for t in backend_tasks:
        expected = -(-t["man_day"] // 2)  # ceil(man_day / 2)
        assert (date.fromisoformat(t["end_date"]) - date.fromisoformat(t["start_date"])).days + 1 >= expected


def test_by_role_duration_days():
    import math

    result = _schedule()
    br = result["by_role"]["backend"]
    assert br["headcount"] == 2
    assert br["man_day"] > 0
    expected = sum(
        math.ceil(t["man_day"] / 2) for t in result["tasks"] if t["role"] == "backend"
    )
    assert br["duration_days"] == expected


def test_buffer_adds_working_days_at_end():
    no_buffer = _schedule(buffer_days=0)
    with_buffer = _schedule(buffer_days=5)
    assert with_buffer["end_date"] > no_buffer["end_date"]
    # 5 ngày làm việc buffer (cuối tuần không tính).
    delta = (with_buffer["end_date"] - no_buffer["end_date"]).days
    assert delta >= 5


def test_payment_milestone_due_date_from_start():
    from datetime import timedelta

    result = _schedule()
    milestones = result["payment_milestones"]
    assert milestones, "Phải có mốc thanh toán"
    for m in milestones:
        expected = date(2026, 11, 1) + timedelta(days=m["due_offset_days"])
        assert date.fromisoformat(m["due_date"]) == expected


def test_payment_total_percent_leq_100():
    result = _schedule()
    total = sum(m["percent"] for m in result["payment_milestones"])
    assert total <= 100


def test_first_task_starts_on_next_working_day():
    """start_date 2026-11-01 (CN) → task đầu tiên bắt đầu 2026-11-02 (T2)."""
    result = _schedule()
    assert result["tasks"][0]["start_date"] == "2026-11-02"
