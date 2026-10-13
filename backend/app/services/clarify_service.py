"""Service hỏi làm rõ — FR-010, FR-011 (contract api_contract.md §6)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.errors import validation_error
from app.models import Bid, Question
from app.services.bid_service import MAX_CLARIFY_ROUNDS, get_bid_or_404


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def count_rounds_used(session: Session, bid_id: int) -> int:
    """Số vòng hỏi đã dùng = số round_no khác nhau đã có câu hỏi."""
    return (
        session.scalar(
            select(func.count(func.distinct(Question.round_no))).where(
                Question.bid_id == bid_id
            )
        )
        or 0
    )


def count_unanswered(session: Session, bid_id: int) -> int:
    return (
        session.scalar(
            select(func.count(Question.id)).where(
                Question.bid_id == bid_id,
                Question.status == "awaiting_answer",
            )
        )
        or 0
    )


def save_questions_from_gap(
    session: Session, bid_id: int, round_no: int, questions: list[dict]
) -> list[Question]:
    """Lưu câu hỏi vòng mới và chuyển bid sang ``waiting_clarification`` (FR-010.3)."""
    bid = get_bid_or_404(session, bid_id)
    saved: list[Question] = []
    previous = {
        q.question.strip().casefold()
        for q in session.scalars(select(Question).where(Question.bid_id == bid_id)).all()
    }
    for item in questions:
        if item["question"].strip().casefold() in previous:
            continue
        q = Question(
            bid_id=bid_id,
            round_no=round_no,
            question=item["question"],
            reason_vi=item["reason_vi"],
            impact=item["impact"],
            related_req_codes=item.get("related_req_codes", []),
        )
        session.add(q)
        saved.append(q)
        previous.add(q.question.strip().casefold())
    bid.status = "waiting_clarification"
    session.commit()
    for q in saved:
        session.refresh(q)
    return saved


def list_questions(session: Session, bid_id: int, round_no: int | None = None) -> dict:
    """Danh sách câu hỏi + rounds_used/max_rounds (contract §6.1)."""
    get_bid_or_404(session, bid_id)
    stmt = select(Question).where(Question.bid_id == bid_id)
    if round_no is not None:
        stmt = stmt.where(Question.round_no == round_no)
    stmt = stmt.order_by(Question.round_no, Question.id)
    items = list(session.scalars(stmt).all())
    round_two_reason = None
    if any(q.round_no == 2 and q.status == "awaiting_answer" for q in items):
        round_two_reason = "Vòng 1 vẫn còn thông tin chặn cần xác nhận trước khi chốt giải pháp và lịch."
    return {
        "items": items,
        "rounds_used": count_rounds_used(session, bid_id),
        "max_rounds": MAX_CLARIFY_ROUNDS,
        "round_two_reason_vi": round_two_reason,
    }


def list_previous_answers(session: Session, bid_id: int, before_round: int) -> list[dict]:
    """Câu trả lời các vòng trước — đưa vào prompt B2 khi chạy vòng sau."""
    stmt = (
        select(Question)
        .where(
            Question.bid_id == bid_id,
            Question.round_no < before_round,
            Question.status == "answered",
        )
        .order_by(Question.id)
    )
    return [
        {
            "round_no": q.round_no,
            "question": q.question,
            "answer": q.answer,
            "is_assumption": q.is_assumption,
        }
        for q in session.scalars(stmt).all()
    ]


def submit_answers(
    session: Session,
    bid_id: int,
    round_no: int,
    answers: list[dict],
    answered_by: str = "anonymous",
) -> dict:
    """Trả lời câu hỏi vòng ``round_no`` (FR-011).

    - Chỉ cho phép khi hồ sơ đang ``waiting_clarification`` (máy trạng thái §18);
      nếu không → 400 VALIDATION_ERROR, KHÔNG đổi trạng thái hồ sơ.
    - Thiếu câu chưa trả lời → 400 VALIDATION_ERROR kèm ``details.missing_ids``.
    - Lưu answer/is_assumption/answered_by; chuyển bid ``analyzing``.
    """
    bid = get_bid_or_404(session, bid_id)

    if bid.status != "waiting_clarification":
        raise validation_error(
            "Hồ sơ không ở trạng thái chờ làm rõ — không thể trả lời câu hỏi",
            {"status": bid.status},
        )

    awaiting = list(
        session.scalars(
            select(Question).where(
                Question.bid_id == bid_id,
                Question.round_no == round_no,
                Question.status == "awaiting_answer",
            )
        ).all()
    )
    if not awaiting:
        raise validation_error(
            "Không có câu hỏi chờ trả lời ở vòng này",
            {"round_no": round_no},
        )
    awaiting_ids = {q.id for q in awaiting}
    submitted_ids = {a["question_id"] for a in answers}

    missing = sorted(awaiting_ids - submitted_ids)
    if missing:
        raise validation_error(
            "Còn câu hỏi chưa được trả lời — vui lòng trả lời đầy đủ",
            {"missing_ids": missing},
        )

    # Mọi câu trả lời phải thuộc vòng này và thuộc hồ sơ này.
    by_id: dict[int, Question] = {q.id: q for q in awaiting}
    for a in answers:
        q = by_id.get(a["question_id"])
        if q is None or q.bid_id != bid_id or q.round_no != round_no:
            raise validation_error(
                "Câu hỏi không thuộc vòng này",
                {"question_id": a["question_id"], "round_no": round_no},
            )

    for a in answers:
        q = by_id[a["question_id"]]
        q.answer = a["answer"]
        q.is_assumption = bool(a.get("is_assumption", False))
        q.answered_by = answered_by
        q.answered_at = _utcnow()
        q.status = "answered"

    bid.status = "analyzing"
    session.commit()
    return {"status": "analyzing", "pipeline_resumed_from": "gap"}
