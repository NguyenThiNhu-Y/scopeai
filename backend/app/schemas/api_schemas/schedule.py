"""API schemas Module F — Master schedule (contract api_contract.md §8.4/§8.4a)."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field


class PaymentMilestoneOut(BaseModel):
    name: str
    percent: float
    due_offset_days: int
    due_date: date | None = None


class PaymentMilestoneIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    percent: float = Field(..., gt=0, le=100)
    due_offset_days: int = Field(..., ge=0)


class RoleDurationOut(BaseModel):
    man_day: float
    headcount: int
    duration_days: int


class TaskDateOut(BaseModel):
    task_code: str
    phase: str
    role: str
    man_day: float
    start_date: date | None = None
    end_date: date


class ScheduleTraceOut(BaseModel):
    formula: str


class ScheduleOut(BaseModel):
    start_date: date
    buffer_days: int
    working_calendar: str
    team_allocation: dict[str, int]
    phase_team_allocation: dict[str, dict[str, int]] = Field(default_factory=dict)
    payment_milestones: list[PaymentMilestoneOut]
    by_role: dict[str, RoleDurationOut]
    tasks: list[TaskDateOut]
    holidays_applied: list[str]
    end_date: date | None
    deadline_violation: bool
    warning: str | None
    trace: ScheduleTraceOut
    work_breakdown: dict[str, dict[str, float]] = Field(default_factory=dict)
    go_no_go_gap_working_days: int = 10
    go_no_go_start: date | None = None
    go_no_go_end: date | None = None
    earliest_mvp_start: date | None = None
    earliest_production_start: date | None = None
    customer_mvp_start: date | None = None
    customer_production_start: date | None = None
    gantt_break_interval: str = "week"


class ScheduleUpdateIn(BaseModel):
    """PUT /schedule — code tính lại ngay, không gọi AI (contract §8.4a)."""

    start_date: date
    buffer_days: int = Field(default=0, ge=0, le=365)
    go_no_go_gap_working_days: int = Field(default=10, ge=0, le=365)
    gantt_break_interval: Literal["day", "week", "month"] = "week"
    working_calendar: Literal["vn", "jp", "both"] | None = None
    team_allocation: dict[str, int]
    phase_team_allocation: dict[str, dict[str, int]] = Field(default_factory=dict)
    payment_milestones: list[PaymentMilestoneIn] | None = None
    by: str | None = None
