"""Router Schedule — contract api_contract.md §8.4/§8.4a (M4)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Identity, get_db, get_identity
from app.schemas.api_schemas.schedule import ScheduleOut, ScheduleUpdateIn
from app.services import schedule_service

router = APIRouter(prefix="/bids", tags=["schedule"])


@router.get("/{bid_id}/schedule", response_model=ScheduleOut)
def get_schedule(bid_id: int, session: Session = Depends(get_db)) -> ScheduleOut:
    """Master schedule — Gantt tasks[] do backend tính (FR-034, contract §8.4)."""
    return ScheduleOut(**schedule_service.get_schedule(session, bid_id))


@router.put("/{bid_id}/schedule", response_model=ScheduleOut)
def put_schedule(
    bid_id: int,
    body: ScheduleUpdateIn,
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
) -> ScheduleOut:
    """Cập nhật tham số lịch — code tính lại ngay, không gọi AI (§8.4a)."""
    return ScheduleOut(
        **schedule_service.update_schedule(session, bid_id, body, identity.user)
    )