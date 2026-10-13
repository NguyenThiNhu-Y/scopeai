from datetime import date, datetime, timezone
from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class Quotation(Base):
    __tablename__ = "quotations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id", ondelete="CASCADE"), index=True, nullable=False)
    contract_model: Mapped[str] = mapped_column(String(30), nullable=False)
    contingency_percent: Mapped[float] = mapped_column(Float, nullable=False)
    onsite_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_to_win_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0, server_default="0")
    tm_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    odc_fte: Mapped[float | None] = mapped_column(Float, nullable=True)
    odc_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fx_rate_value: Mapped[float] = mapped_column(Float, nullable=False)
    fx_rate_date: Mapped[date] = mapped_column(Date, nullable=False)
    totals: Mapped[dict] = mapped_column(JSON, nullable=False)
    valid_until: Mapped[date | None] = mapped_column(Date)
    tax_mode: Mapped[str] = mapped_column(String(20), default="tax_excluded", nullable=False)
    rounding_note: Mapped[str | None] = mapped_column(String(200))
    reference_snapshot_id: Mapped[int] = mapped_column(ForeignKey("reference_snapshots.id"), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    computed_by: Mapped[str | None] = mapped_column(String(100))
