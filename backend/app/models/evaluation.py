from __future__ import annotations
from sqlalchemy import ForeignKey, Integer, String, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
class Evaluation(Base):
    __tablename__ = "evaluations"
    __table_args__ = (UniqueConstraint("bid_id", "requirement_id", name="uq_evaluation_bid_requirement"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id", ondelete="CASCADE"), index=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id", ondelete="CASCADE"))
    rating: Mapped[str] = mapped_column(String(3), nullable=False)
    needs_clarification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    note_vi: Mapped[str] = mapped_column(Text, default="", nullable=False)
    batch_no: Mapped[int] = mapped_column(Integer, nullable=False)
    solution_direction: Mapped[str | None] = mapped_column(String(30))
