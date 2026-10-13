"""Bảng ``changelog`` — Audit log (data_model.md §17, NFR-009)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Changelog(Base):
    """Một dòng audit — mọi thay đổi quan trọng ghi từ service layer."""

    __tablename__ = "changelog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bid_id: Mapped[int] = mapped_column(
        ForeignKey("bids.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    field_changed: Mapped[str | None] = mapped_column(String(100), nullable=True)
    old_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    new_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow
    )