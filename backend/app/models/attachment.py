from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class Attachment(Base):
    __tablename__ = "attachments"
    __table_args__ = (UniqueConstraint("bid_id", "filename", name="uq_attachment_bid_filename"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(30), nullable=False)
    detected_type: Mapped[str] = mapped_column(String(30), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    original_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    parse_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    parse_error: Mapped[str | None] = mapped_column(Text)
    sheet_mappings: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
