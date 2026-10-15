"""Service layer — nghiệp vụ hồ sơ dự thầu (FR-001, FR-007)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.errors import not_found
from app.models import Bid, PipelineStep, Question, Quotation
from app.schemas.api_schemas.bid import BidCreate

# 7 bước pipeline theo thứ tự (llm_pipeline.md §1).
STEP_KEYS = ["intake", "gap", "solution", "evaluate", "wbs", "proposal"]

MAX_CLARIFY_ROUNDS = 2


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def get_bid_or_404(session: Session, bid_id: int) -> Bid:
    bid = session.get(Bid, bid_id)
    if bid is None:
        raise not_found()
    return bid


def create_bid(session: Session, data: BidCreate, created_by: str = "anonymous") -> Bid:
    """Tạo hồ sơ mới ở trạng thái ``draft`` (FR-001)."""
    bid = Bid(
        project_name=data.project_name.strip(),
        customer_name=data.customer_name.strip(),
        deal_stage=data.deal_stage.strip() if data.deal_stage else None,
        submission_deadline=data.submission_deadline,
        customer_schedule_start=data.customer_schedule_start,
        customer_schedule_end=data.customer_schedule_end,
        customer_poc_end=data.customer_poc_end,
        customer_mvp_start=data.customer_mvp_start,
        customer_production_start=data.customer_production_start,
        customer_language=data.customer_language,
        request_content=data.request_content,
        budget_amount=data.budget_amount,
        budget_currency=data.budget_currency,
        budget_scope=data.budget_scope,
        display_currency=data.display_currency or "VND",
        created_by=created_by,
    )
    session.add(bid)
    session.commit()
    session.refresh(bid)
    return bid


def list_bids(
    session: Session,
    status: str | None = None,
    q: str | None = None,
    deal_stage: str | None = None,
    page: int = 1,
    page_size: int = 20,
    owner: str | None = None,
) -> tuple[list[Bid], int]:
    """Danh sách hồ sơ: lọc status, tìm q (ILIKE tên dự án/khách hàng), phân trang."""
    stmt = select(Bid)
    count_stmt = select(func.count(Bid.id))

    if status:
        stmt = stmt.where(Bid.status == status)
        count_stmt = count_stmt.where(Bid.status == status)
    if q:
        pattern = f"%{q.strip()}%"
        cond = or_(Bid.project_name.ilike(pattern), Bid.customer_name.ilike(pattern))
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    if deal_stage:
        stmt = stmt.where(Bid.deal_stage == deal_stage.strip())
        count_stmt = count_stmt.where(Bid.deal_stage == deal_stage.strip())
    if owner is not None:
        stmt = stmt.where(Bid.created_by == owner)
        count_stmt = count_stmt.where(Bid.created_by == owner)

    total = session.scalar(count_stmt) or 0
    stmt = stmt.order_by(Bid.updated_at.desc(), Bid.id.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    items = list(session.scalars(stmt).all())
    quotation_by_bid = {}
    if items:
        for quotation in session.scalars(
            select(Quotation)
            .where(Quotation.bid_id.in_([bid.id for bid in items]))
            .order_by(Quotation.id.desc())
        ).all():
            quotation_by_bid.setdefault(quotation.bid_id, quotation)
    for bid in items:
        bid.latest_quotation = quotation_by_bid.get(bid.id)
    return items, total


def _step_status_map(session: Session, bid_id: int) -> dict[str, dict]:
    rows = session.execute(
        select(
            PipelineStep.step_key,
            PipelineStep.status,
            PipelineStep.output_json,
            PipelineStep.error_message,
        ).where(PipelineStep.bid_id == bid_id)
    ).all()
    return {
        key: {"status": status, "output_json": output_json, "error_message": error_message}
        for key, status, output_json, error_message in rows
    }


def pipeline_progress(session: Session, bid_id: int) -> dict:
    """Tóm tắt tiến độ pipeline; bước không có dữ liệu được đánh dấu skipped."""
    status_map = _step_status_map(session, bid_id)
    steps: list[dict] = []
    for key in STEP_KEYS:
        info = status_map.get(key)
        step: dict = {"step_key": key, "status": info["status"] if info else "skipped"}
        if info:
            if info["output_json"] is not None:
                step["output_json"] = info["output_json"]
            if info["error_message"] is not None:
                step["error_message"] = info["error_message"]
        steps.append(step)
    bid = session.get(Bid, bid_id)
    rounds_used = _count_rounds_used(session, bid_id)
    return {
        "steps": steps,
        "waiting_clarification": bid.status == "waiting_clarification" if bid else False,
        "rounds_used": rounds_used,
        "max_rounds": MAX_CLARIFY_ROUNDS,
    }


def _count_rounds_used(session: Session, bid_id: int) -> int:
    return (
        session.scalar(
            select(func.count(func.distinct(Question.round_no))).where(
                Question.bid_id == bid_id
            )
        )
        or 0
    )


def get_bid(session: Session, bid_id: int) -> Bid:
    """Chi tiết hồ sơ — kèm pipeline_progress để UI khôi phục màn hình."""
    return get_bid_or_404(session, bid_id)


def get_authorized_bid(session: Session, bid_id: int, identity) -> Bid:
    """Giữ tên hàm tương thích; MVP không thực hiện authorization."""
    return get_bid_or_404(session, bid_id)
