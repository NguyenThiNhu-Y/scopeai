"""Dependencies dùng chung cho router (DB session và actor audit)."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from fastapi import Header
from sqlalchemy.orm import Session

from app.core import db


@dataclass(frozen=True)
class Identity:
    """Actor do client cung cấp, chỉ dùng để ghi audit log trong MVP."""

    user: str


def get_actor(identity: Identity) -> str:
    """Trả actor cho service layer và audit log."""
    return identity.user


def get_db() -> Iterator[Session]:
    """Yield một session SQLAlchemy — đóng sau request."""
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_identity(
    x_actor: str | None = Header(default=None, alias="X-Actor"),
    x_user: str | None = Header(default=None, alias="X-User"),
) -> Identity:
    """Đọc actor từ ``X-Actor``; ``X-User`` chỉ giữ tương thích test cũ."""
    user = (x_actor or x_user or "anonymous").strip() or "anonymous"
    return Identity(user=user)
