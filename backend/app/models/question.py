"""Bảng ``questions`` — Câu hỏi làm rõ & trả lời (data_model.md §6)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Question(Base):
    """Câu hỏi làm rõ (FR-010) — tối đa 2 vòng, mỗi vòng ≤ 7 câu (kiểm tra service)."""

    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint("round_no IN (1,2)", name="ck_questions_round_no"),
        CheckConstraint(
            "impact IN ('solution','effort','price')",
            name="ck_questions_impact",
        ),
        CheckConstraint(
            "status IN ('awaiting_answer','answered','skipped')",
            name="ck_questions_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bid_id: Mapped[int] = mapped_column(
        ForeignKey("bids.id", ondelete="CASCADE"), nullable=False, index=True
    )
    round_no: Mapped[int] = mapped_column(Integer, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    reason_vi: Mapped[str] = mapped_column(Text, nullable=False)
    impact: Mapped[str] = mapped_column(String(20), nullable=False)
    related_req_codes: Mapped[list | None] = mapped_column(JSON, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_assumption: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )
    answered_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="awaiting_answer",
        server_default=text("'awaiting_answer'"),
    )

    topic: Mapped[str | None] = mapped_column(String(100), nullable=True)
    blocking: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("0"))
