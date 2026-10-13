"""Bảng ``pipeline_steps`` — Persist/resume pipeline (data_model.md §13)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
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


class PipelineStep(Base):
    """Một bước trong pipeline 7 bước — persist ngay khi trạng thái đổi (FR-023)."""

    __tablename__ = "pipeline_steps"
    __table_args__ = (
        CheckConstraint(
            "step_key IN ('intake','gap','evaluate','solution','wbs','proposal','ja_check')",
            name="ck_pipeline_steps_step_key",
        ),
        CheckConstraint(
            "status IN ('pending','running','completed','failed',"
            "'waiting_clarification','skipped')",
            name="ck_pipeline_steps_status",
        ),
        UniqueConstraint("bid_id", "step_key", name="uq_pipeline_steps_bid_step"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bid_id: Mapped[int] = mapped_column(
        ForeignKey("bids.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_key: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )
    attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    output_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)