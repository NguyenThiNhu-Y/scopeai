from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class ReferenceSnapshot(Base):
    __tablename__ = "reference_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int | None] = mapped_column(ForeignKey("bids.id", ondelete="SET NULL"), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
