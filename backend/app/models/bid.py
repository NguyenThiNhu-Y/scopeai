"""Bảng ``bids`` — Hồ sơ dự thầu (data_model.md §2)."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Bid(Base):
    """Hồ sơ dự thầu — entity trung tâm của hệ thống."""

    __allow_unmapped__ = True
    latest_quotation: object | None = None

    __tablename__ = "bids"
    __table_args__ = (
        CheckConstraint(
            "customer_language IN ('vi','en','ja')",
            name="ck_bids_customer_language",
        ),
        CheckConstraint(
            "budget_currency IS NULL OR budget_currency IN ('VND','JPY','USD')",
            name="ck_bids_budget_currency",
        ),
        CheckConstraint(
            "status IN ('draft','waiting_clarification','analyzing',"
            "'waiting_tech_approval','waiting_price_approval','price_approved','rejected','error')",
            name="ck_bids_status",
        ),
        CheckConstraint(
            "data_readiness IS NULL OR data_readiness IN ('low','medium','high')",
            name="ck_bids_data_readiness",
        ),
        CheckConstraint(
            "display_currency IN ('VND','JPY','USD')",
            name="ck_bids_display_currency",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    deal_stage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    submission_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    customer_schedule_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    customer_schedule_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    customer_mvp_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    customer_production_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    customer_language: Mapped[str] = mapped_column(String(10), nullable=False)
    request_content: Mapped[str] = mapped_column(Text, nullable=False)
    budget_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="draft",
        server_default=text("'draft'"),
    )
    locked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
    )
    lock_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    no_requirement_file: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
    )
    data_readiness: Mapped[str | None] = mapped_column(String(10), nullable=True)
    display_currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="VND",
        server_default=text("'VND'"),
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )
