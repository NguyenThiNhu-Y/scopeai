"""Bảng ``schedules`` — Master schedule (data_model.md §10, ADR-006)."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Schedule(Base):
    """Tham số + kết quả lịch do code tính (by_role/tasks_json/holidays_applied)."""

    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bid_id: Mapped[int] = mapped_column(
        ForeignKey("bids.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    buffer_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    go_no_go_gap_working_days: Mapped[int] = mapped_column(Integer, nullable=False, default=10, server_default=text("10"))
    go_no_go_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    go_no_go_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    gantt_break_interval: Mapped[str] = mapped_column(String(10), nullable=False, default="week", server_default=text("'week'"))
    earliest_mvp_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    earliest_production_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    working_calendar: Mapped[str] = mapped_column(
        String(10), nullable=False, default="vn", server_default=text("'vn'")
    )
    team_allocation: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Nullable keeps existing SQLite databases compatible; the API normalizes
    # a missing value to an empty mapping.
    phase_team_allocation: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    payment_milestones: Mapped[list | None] = mapped_column(JSON, nullable=True)
    by_role: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tasks_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    holidays_applied: Mapped[list | None] = mapped_column(JSON, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline_violation: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )
    computed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow
    )
