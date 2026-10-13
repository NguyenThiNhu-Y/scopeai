from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ReferenceSetting(Base):
    """Validated runtime override for a reference table."""

    __tablename__ = "reference_settings"

    key: Mapped[str] = mapped_column(String(30), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[object] = mapped_column(JSON, nullable=False)
    updated_by: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
