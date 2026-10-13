from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class ProposalDraft(Base):
    __tablename__ = "proposal_drafts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id", ondelete="CASCADE"), unique=True, nullable=False)
    sections: Mapped[dict] = mapped_column(JSON, nullable=False)
    assumptions_phrased: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    scope_out_phrased: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    edited_by: Mapped[str | None] = mapped_column(String(100))
    customer_language: Mapped[str] = mapped_column(String(10), default="vi", nullable=True)
    translations: Mapped[dict] = mapped_column(JSON, default=dict, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
