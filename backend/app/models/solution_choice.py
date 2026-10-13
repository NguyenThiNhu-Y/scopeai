from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SolutionChoice(Base):
    __tablename__ = "solution_choices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id", ondelete="CASCADE"), index=True)
    direction: Mapped[str] = mapped_column(String(30), nullable=False)
    reason_vi: Mapped[str] = mapped_column(Text, nullable=False)
    risks_vi: Mapped[list] = mapped_column(JSON, default=list)
    architecture_notes_vi: Mapped[str | None] = mapped_column(Text)
    reliability_vi: Mapped[str | None] = mapped_column(Text)
    assumptions_vi: Mapped[list] = mapped_column(JSON, default=list, server_default=text("'[]'"))
    excluded_directions: Mapped[list] = mapped_column(JSON, default=list, server_default=text("'[]'"))
    feasibility: Mapped[dict] = mapped_column(JSON, default=dict, server_default=text("'{}'"))
    feasibility_score: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    chosen_by: Mapped[str | None] = mapped_column(String(100))
    chosen_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime)
