from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import not_found, validation_error
from app.models import Bid, BidQualification, Changelog, ReferenceSetting
from app.schemas.api_schemas.bid_qualification import BidQualificationUpdate
from app.services.settings_service import OPTIONAL_DEFAULTS


def _default_criteria(session: Session) -> list[dict]:
    """Tiêu chí mặc định từ Cài đặt (bảng reference_setting key 'bid_no_bid')."""
    row = session.get(ReferenceSetting, "bid_no_bid")
    payload = row.payload if row else OPTIONAL_DEFAULTS["bid_no_bid"]
    return [dict(item) for item in (payload or {}).get("criteria", [])]


def get_or_create(session: Session, bid_id: int) -> BidQualification:
    if not session.get(Bid, bid_id):
        raise not_found()
    row = session.scalar(select(BidQualification).where(BidQualification.bid_id == bid_id))
    if row is None:
        row = BidQualification(bid_id=bid_id, criteria=_default_criteria(session), suggestions=[])
        session.add(row)
        session.commit()
        session.refresh(row)
    elif not row.criteria:
        # Hồ sơ cũ chưa có tiêu chí → trả tiêu chí mặc định từ Cài đặt (không 500).
        row.criteria = _default_criteria(session)
        session.commit()
        session.refresh(row)
    return row


def to_out(session: Session, bid_id: int) -> dict:
    row = get_or_create(session, bid_id)
    return {"bid_id": bid_id, "criteria": row.criteria, "decision": row.decision, "confirmer": row.confirmer, "suggestions": row.suggestions, "confirmed_at": row.confirmed_at}


def update(session: Session, bid_id: int, data: BidQualificationUpdate, actor: str) -> dict:
    if abs(sum(item.weight for item in data.criteria) - 100) > 0.001:
        raise validation_error("Tổng trọng số Bid/No-bid phải bằng 100")
    row = get_or_create(session, bid_id)
    row.criteria = [item.model_dump() for item in data.criteria]
    row.suggestions = [{"criterion_id": item.id, "source": "analysis", "status": "review", "note_vi": "Gợi ý cần người xác nhận từ kết quả phân tích"} for item in data.criteria]
    row.decision = data.decision
    row.confirmer = data.confirmer or (actor if data.decision else None)
    row.confirmed_at = datetime.now(timezone.utc) if data.decision and row.confirmer else None
    session.add(Changelog(bid_id=bid_id, actor=actor, action="confirm_bid_no_bid" if data.decision else "update_bid_no_bid", note=data.decision or "Cập nhật checklist Bid/No-bid"))
    session.commit()
    session.refresh(row)
    return to_out(session, bid_id)
