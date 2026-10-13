from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class BidQualification(Base):
    """Weighted Bid/No-bid checklist and human confirmation."""

    __tablename__ = "bid_qualifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id", ondelete="CASCADE"), unique=True, nullable=False)
    decision: Mapped[str | None] = mapped_column(String(10))
    criteria: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    suggestions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    confirmer: Mapped[str | None] = mapped_column(String(100))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
