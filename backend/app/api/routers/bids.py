"""Router hồ sơ dự thầu — contract api_contract.md §3 (M2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import Identity, get_db, get_identity
from app.schemas.api_schemas.bid import (
    BidCreate,
    BidDetailOut,
    BidListItem,
    BidListOut,
    BidOut,
    PipelineProgressSummary,
)
from app.schemas.api_schemas.sample import SampleIn
from app.schemas.api_schemas.proposal import DealStageUpdateIn
from app.schemas.api_schemas.confidence import ConfidenceOut
from app.models import Changelog
from app.services import bid_service, sample_service
from app.services.confidence_service import get_confidence

router = APIRouter(prefix="/bids", tags=["bids"])


def _to_bid_out(bid) -> BidOut:
    return BidOut(
        id=bid.id,
        project_name=bid.project_name,
        customer_name=bid.customer_name,
        submission_deadline=bid.submission_deadline,
        customer_schedule_start=bid.customer_schedule_start,
        customer_schedule_end=bid.customer_schedule_end,
        customer_poc_end=bid.customer_poc_end,
        customer_mvp_start=bid.customer_mvp_start,
        customer_production_start=bid.customer_production_start,
        customer_language=bid.customer_language,
        status=bid.status,
        locked=bid.locked,
        budget_amount=bid.budget_amount,
        budget_currency=bid.budget_currency,
        budget_scope=bid.budget_scope,
        created_by=bid.created_by,
        created_at=bid.created_at,
        display_currency=bid.display_currency,
    )


def _to_list_item(bid) -> BidListItem:
    quotation = getattr(bid, "latest_quotation", None)
    totals = quotation.totals if quotation else {}
    return BidListItem(
        id=bid.id,
        project_name=bid.project_name,
        customer_name=bid.customer_name,
        deal_stage=bid.deal_stage,
        created_at=bid.created_at,
        total_price=totals.get("grand_total"),
        total_price_currency=bid.display_currency if quotation else None,
        status=bid.status,
        submission_deadline=bid.submission_deadline,
        customer_language=bid.customer_language,
        locked=bid.locked,
        updated_at=bid.updated_at,
    )


@router.post("/sample", response_model=BidOut, status_code=201)
def create_sample(
    body: SampleIn | None = None,
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
) -> BidOut:
    """Nạp hồ sơ mẫu giả lập (FR-006, §3.7) — mặc định ``ja_email``."""
    sample_key = (body.sample_key if body else None) or "ja_email"
    bid = sample_service.load_sample(session, sample_key, created_by=identity.user)
    return _to_bid_out(bid)


@router.get("/sample/preview")
def preview_sample(
    sample_key: str = Query(default="ja_email"),
    identity: Identity = Depends(get_identity),
):
    """Xem bộ mẫu trước khi người dùng quyết định tạo hồ sơ."""
    return sample_service.sample_preview(sample_key)


@router.post("", response_model=BidOut, status_code=201)
def create_bid(
    body: BidCreate,
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
) -> BidOut:
    """Tạo hồ sơ mới (FR-001) — request_content ≥ 30 ký tự."""
    bid = bid_service.create_bid(session, body, created_by=identity.user)
    return _to_bid_out(bid)


@router.get("", response_model=BidListOut)
def list_bids(
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    deal_stage: str | None = Query(default=None, min_length=1, max_length=50),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
) -> BidListOut:
    """Danh sách hồ sơ (FR-007, §3.2) — lọc status, tìm q, phân trang."""
    items, total = bid_service.list_bids(
        session, status=status, q=q, deal_stage=deal_stage, page=page, page_size=page_size, owner=None
    )
    return BidListOut(items=[_to_list_item(b) for b in items], total=total)


@router.get("/{bid_id}", response_model=BidDetailOut)
def get_bid_detail(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)) -> BidDetailOut:
    """Chi tiết hồ sơ + pipeline_progress (FR-007, §3.3)."""
    bid = bid_service.get_authorized_bid(session, bid_id, identity)
    progress = bid_service.pipeline_progress(session, bid_id)
    return BidDetailOut(
        **_to_bid_out(bid).model_dump(),
            request_content=bid.request_content,
            no_requirement_file=bid.no_requirement_file,
            data_readiness=bid.data_readiness,
            pipeline_progress=PipelineProgressSummary(**progress),
    )

@router.put("/{bid_id}/deal-stage")
def update_deal_stage(bid_id: int, body: DealStageUpdateIn, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)):
    bid = bid_service.get_authorized_bid(session, bid_id, identity)
    old_stage = bid.deal_stage
    bid.deal_stage = body.deal_stage
    session.add(Changelog(bid_id=bid_id, actor=identity.user, action="update_deal_stage", field_changed="deal_stage", old_value=old_stage, new_value=body.deal_stage, note=body.note))
    session.commit()
    return {"bid_id": bid_id, "deal_stage": bid.deal_stage}


@router.get("/{bid_id}/confidence", response_model=ConfidenceOut)
def get_bid_confidence(
    bid_id: int,
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
) -> ConfidenceOut:
    """Độ tin cậy ước lượng từng hồ sơ (thiet_ke_danh_gia.md §5.1)."""
    return ConfidenceOut(**get_confidence(session, bid_id))
