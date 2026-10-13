from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class ProposalVersion(Base):
    """Phiên bản proposal gửi khách; nội dung số vẫn render từ server."""

    __tablename__ = "proposal_versions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    customer_language: Mapped[str] = mapped_column(String(10), nullable=False)
    sections: Mapped[dict] = mapped_column(JSON, nullable=False)
    sent: Mapped[bool] = mapped_column(default=False, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sent_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
