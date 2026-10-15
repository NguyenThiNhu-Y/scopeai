"""Service độ tin cậy từng hồ sơ — gom dữ liệu từ DB rồi gọi confidence_engine.

Tầng này chỉ LOẠI BỎ dữ liệu đã có (intake, questions, evaluations, WBS check,
schedule, effort, case studies) và đưa vào hàm thuần ``compute_confidence``.
Không tính số ở đây; mọi ngưỡng/quy tắc nằm trong engine + confidence.yaml.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import ApiError
from app.models import Attachment, Bid, Evaluation, Question, Requirement
from app.services.bid_service import get_bid_or_404
from app.services import check_engine, wbs_engine
from app.services.confidence_engine import compute_confidence
from app.services.effort_engine import calculate_effort
from app.services.schedule_service import get_schedule
from app.services.settings_service import _repo_payload, list_settings
from app.services.solution_service import current_choice
from app.services.wbs_service import load_items, item_to_dict

# Rating chưa chắc chắn trong đánh giá đáp ứng (thiet_ke_danh_gia.md §5.2).
_UNCERTAIN_RATINGS = {"△", "×"}


def _settings_payload(session: Session, key: str):
    for item in list_settings(session):
        if item["key"] == key:
            return item["payload"], item["version"]
    payload = _repo_payload(key)
    version = payload.get("version", 1) if isinstance(payload, dict) else 1
    return payload, version


def _bid_input(bid: Bid, has_requirement_file: bool) -> dict:
    # Hồ sơ không lưu market riêng — suy ra từ ngôn ngữ khách cho điểm tương đồng
    # (thiet_ke_danh_gia.md §5.4): ja → jp, vi → vn, en → other.
    market = {"ja": "jp", "vi": "vn"}.get(bid.customer_language, "other")
    return {
        "market": market,
        "budget_amount": bid.budget_amount,
        "customer_schedule_start": (
            bid.customer_schedule_start.isoformat() if bid.customer_schedule_start else None
        ),
        "customer_mvp_start": (
            bid.customer_mvp_start.isoformat() if bid.customer_mvp_start else None
        ),
        "customer_production_start": (
            bid.customer_production_start.isoformat() if bid.customer_production_start else None
        ),
        "customer_schedule_end": (
            bid.customer_schedule_end.isoformat() if bid.customer_schedule_end else None
        ),
        "customer_language": bid.customer_language,
        # "Có file requirement" = có attachment loại requirement (ground truth),
        # không dựa vào cờ no_requirement_file (mặc định False cho bid không file).
        "has_requirement_file": has_requirement_file,
        "request_content": bid.request_content,
    }


def _requirements_data(session: Session, bid_id: int) -> dict:
    requirements = list(
        session.scalars(
            select(Requirement).where(Requirement.bid_id == bid_id).order_by(Requirement.id)
        )
    )
    codes = {r.internal_code for r in requirements}
    items = load_items(session, bid_id)
    enriched = wbs_engine.enrich_items([item_to_dict(i) for i in items])
    covered = {
        code
        for item in enriched
        if item.get("is_leaf")
        for code in (item.get("requirement_codes") or [])
    } & codes
    return {
        "total": len(codes),
        "covered": len(covered),
        "uncovered": sorted(codes - covered),
    }


def _evaluations_data(session: Session, bid_id: int) -> dict:
    rows = list(
        session.scalars(select(Evaluation).where(Evaluation.bid_id == bid_id))
    )
    uncertain = sum(
        1
        for row in rows
        if row.needs_clarification or row.rating in _UNCERTAIN_RATINGS
    )
    return {"uncertain": uncertain, "total": len(rows)}


def _questions_data(session: Session, bid_id: int) -> dict:
    blocking = (
        session.query(Question)
        .filter(
            Question.bid_id == bid_id,
            Question.status == "awaiting_answer",
            Question.blocking.is_(True),
        )
        .count()
    )
    return {"blocking_unanswered": blocking}


def get_confidence(session: Session, bid_id: int) -> dict:
    """GET /bids/{id}/confidence — trả dict khớp ``ConfidenceOut`` §5.1."""
    bid = get_bid_or_404(session, bid_id)
    choice = current_choice(session, bid_id)
    direction = choice.direction if choice else None

    has_requirement_file = (
        session.query(Attachment).filter_by(bid_id=bid_id, file_type="requirement").count() > 0
    )
    data: dict = {
        "bid": _bid_input(bid, has_requirement_file),
        "direction": direction,
        "questions": _questions_data(session, bid_id),
        "requirements": _requirements_data(session, bid_id),
        "evaluations": _evaluations_data(session, bid_id),
        "case_studies": _settings_payload(session, "case_studies")[0],
    }

    items = load_items(session, bid_id)
    if items and direction:
        # Truyền session để factor many_requirements được tính — cùng midpoint
        # với effort engine (Đợt 14 C1).
        effort = calculate_effort(bid, direction, session)
        enriched = wbs_engine.enrich_items([item_to_dict(i) for i in items])
        data["wbs_check"] = check_engine.check_wbs(
            enriched, effort["midpoint_total"], effort["by_phase"]
        )
        data["wbs_total"] = round(
            sum(i.get("man_day") or 0.0 for i in enriched if i.get("is_leaf")), 1
        )
        data["effort"] = effort

    sched = None
    try:
        sched = get_schedule(session, bid_id)
    except ApiError as exc:
        if exc.code != "STATE_CONFLICT":
            raise
        # Chưa có lịch → tín hiệu schedule_checks sẽ là na.
        sched = None
    if sched is not None:
        data["schedule"] = {
            "earliest_mvp_start": (
                sched["earliest_mvp_start"].isoformat()
                if sched.get("earliest_mvp_start")
                else None
            ),
            "earliest_production_start": (
                sched["earliest_production_start"].isoformat()
                if sched.get("earliest_production_start")
                else None
            ),
            "go_no_go_end": (
                sched["go_no_go_end"].isoformat() if sched.get("go_no_go_end") else None
            ),
            "end_date": sched["end_date"].isoformat() if sched.get("end_date") else None,
            "warning": sched.get("warning"),
        }

    thresholds, thresholds_version = _settings_payload(session, "confidence")
    _, case_studies_version = _settings_payload(session, "case_studies")

    result = compute_confidence(data, thresholds)
    result["thresholds_version"] = thresholds_version
    result["case_studies_version"] = case_studies_version
    return result