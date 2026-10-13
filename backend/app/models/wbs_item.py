"""Bảng ``wbs_items`` — WBS task 3 cấp (data_model.md §8, ADR-006)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WbsItem(Base):
    """Một task trong WBS — ``role``/``weight``/``man_day`` chỉ trên task lá."""

    __tablename__ = "wbs_items"
    __table_args__ = (
        CheckConstraint(
            "phase IN ('poc','mvp','production')",
            name="ck_wbs_items_phase",
        ),
        CheckConstraint(
            "role IS NULL OR role IN ('pm','ba','brse','ai_engineer',"
            "'backend','frontend','qa','infra')",
            name="ck_wbs_items_role",
        ),
        UniqueConstraint("bid_id", "task_code", name="uq_wbs_items_bid_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bid_id: Mapped[int] = mapped_column(
        ForeignKey("bids.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_code: Mapped[str] = mapped_column(String(50), nullable=False)
    name_vi: Mapped[str] = mapped_column(String(300), nullable=False)
    phase: Mapped[str] = mapped_column(String(20), nullable=False)
    parent_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    depends_on: Mapped[list | None] = mapped_column(JSON, nullable=True)
    role: Mapped[str | None] = mapped_column(String(30), nullable=True)
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True)
    man_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow
    )
    updated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)