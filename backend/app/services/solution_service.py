from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.errors import not_found, state_conflict, validation_error
from app.models import Bid, SolutionChoice
from app.schemas.llm_schemas.solution_proposal import SolutionDirection
from app.services.bid_service import get_bid_or_404
from app.services.clarify_service import count_unanswered
from app.services.effort_engine import calculate_effort


def current_choice(session: Session, bid_id: int) -> SolutionChoice | None:
    return session.execute(select(SolutionChoice).where(SolutionChoice.bid_id == bid_id, SolutionChoice.superseded_at.is_(None)).order_by(SolutionChoice.id.desc())).scalars().first()


def choose_solution(session: Session, bid_id: int, direction: str, reason_vi: str, by: str, *, risks=None, notes=None, reliability="", assumptions=None, excluded_directions=None, feasibility=None, feasibility_score=None) -> dict:
    bid = get_bid_or_404(session, bid_id)
    if count_unanswered(session, bid_id) > 0:
        raise state_conflict("Còn câu hỏi làm rõ chưa được trả lời — hãy trả lời trước khi chọn hướng")
    if not reason_vi.strip():
        raise validation_error("Lý do chọn hướng không được để trống")
    old = current_choice(session, bid_id)
    if old:
        old.superseded_at = datetime.now(timezone.utc)
    choice = SolutionChoice(bid_id=bid_id, direction=direction, reason_vi=reason_vi.strip(), risks_vi=risks or [], architecture_notes_vi=notes, reliability_vi=reliability or "", assumptions_vi=assumptions or [], excluded_directions=[getattr(x, "value", x) for x in (excluded_directions or [])], feasibility=feasibility or {}, feasibility_score=feasibility_score, chosen_by=by)
    session.add(choice)
    session.commit()
    return {"direction": direction, "effort_recalculated": True, "warnings": ["Đánh giá requirement đang theo hướng cũ"] if old else []}


def get_effort(session: Session, bid_id: int) -> dict:
    bid = get_bid_or_404(session, bid_id)
    choice = current_choice(session, bid_id)
    if choice is None:
        raise state_conflict("Chưa chọn hướng giải pháp để tính effort")
    return calculate_effort(bid, choice.direction, session)
