"""Router WBS — contract api_contract.md §8.1/§8.2/§8.3 (M4)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Identity, get_db, get_identity
from app.schemas.api_schemas.wbs import (
    WbsEditIn,
    WbsEditOut,
    WbsOut,
    WbsSnapshotIn,
    WbsSnapshotOut,
)
from app.services import wbs_service

router = APIRouter(prefix="/bids", tags=["wbs"])


@router.get("/{bid_id}/wbs", response_model=WbsOut)
def get_wbs(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)) -> WbsOut:
    """Xem WBS 3 cấp (FR-032, FR-041) — contract §8.1."""
    return WbsOut(**wbs_service.get_wbs(session, bid_id))


@router.put("/{bid_id}/wbs", response_model=WbsEditOut)
def put_wbs(
    bid_id: int,
    body: WbsEditIn,
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
) -> WbsEditOut:
    """Sửa WBS — code tính lại tổng + check + lịch, không gọi AI (contract §8.2)."""
    return WbsEditOut(
        **wbs_service.apply_changes(
            session, bid_id, body.changes, body.note, identity.user
        )
    )


@router.post(
    "/{bid_id}/wbs/snapshot", response_model=WbsSnapshotOut, status_code=201
)
def post_snapshot(
    bid_id: int,
    body: WbsSnapshotIn,
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
) -> WbsSnapshotOut:
    """Chụp snapshot WBS + diff_summary (FR-041.2) — contract §8.3."""
    return WbsSnapshotOut(
        **wbs_service.snapshot_wbs(session, bid_id, body.reason, identity.user)
    )
