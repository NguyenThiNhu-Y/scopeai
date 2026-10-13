from __future__ import annotations
from sqlalchemy import ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base
class Requirement(Base):
    __tablename__ = "requirements"
    __table_args__ = (UniqueConstraint("bid_id", "internal_code", name="uq_requirement_bid_code"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id", ondelete="CASCADE"), index=True)
    internal_code: Mapped[str] = mapped_column(String(30), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(255))
    source_sheet: Mapped[str | None] = mapped_column(String(255))
    source_row: Mapped[int | None] = mapped_column(Integer)
    source_cols: Mapped[dict | None] = mapped_column(JSON)
