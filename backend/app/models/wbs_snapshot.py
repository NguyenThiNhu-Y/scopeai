"""Bảng ``wbs_snapshots`` — Snapshot WBS (data_model.md §9, FR-041.2)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WbsSnapshot(Base):
    """Toàn bộ WBS tại một thời điểm + diff_summary so với snapshot trước."""

    __tablename__ = "wbs_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bid_id: Mapped[int] = mapped_column(
        ForeignKey("bids.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    wbs_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    diff_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow
    )