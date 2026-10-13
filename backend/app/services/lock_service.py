"""LockService — guard hồ sơ khóa (FR-042.4, M3-REV-002).

Mọi mutation M4 (PUT /wbs, PUT /schedule, POST /wbs/snapshot, rerun) phải gọi
``ensure_unlocked(bid)`` trước khi sửa đổi → hồ sơ ``locked=true`` → 409.
"""

from __future__ import annotations

from app.api.errors import state_conflict
from app.models import Bid, Changelog


def ensure_unlocked(bid: Bid) -> None:
    """Ném 409 STATE_CONFLICT nếu hồ sơ đã khóa sau duyệt giá."""
    if bid.locked:
        raise state_conflict(
            "Hồ sơ đã bị khóa sau khi duyệt giá — không thể sửa đổi WBS/lịch"
        )

def unlock_bid(session, bid_id: int, identity, reason: str) -> dict:
    bid = session.get(Bid, bid_id)
    if bid is None:
        from app.api.errors import not_found
        raise not_found()
    if not reason.strip():
        from app.api.errors import validation_error
        raise validation_error("Lý do mở khóa không được rỗng")
    bid.locked = False; bid.status = "waiting_price_approval"; bid.lock_reason = reason
    session.add(Changelog(bid_id=bid_id, actor=identity.user, action="unlock_bid", note=reason)); session.commit()
    return {"locked": False, "status": "waiting_price_approval"}
