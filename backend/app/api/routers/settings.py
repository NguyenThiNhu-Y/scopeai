from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import Identity, get_db, get_identity
from app.models import Bid, Changelog
from app.schemas.api_schemas.settings import HistoryResponse, SettingsResponse, SettingUpdate, SettingUpdated
from app.services import settings_service

router = APIRouter(tags=["settings"])


@router.get("/settings", response_model=SettingsResponse)
def get_settings(session: Session = Depends(get_db)):
    return {"keys": settings_service.list_settings(session)}


@router.put("/settings/{key}", response_model=SettingUpdated)
def put_setting(key: str, body: SettingUpdate, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)):
    return settings_service.update_setting(session, key, body.yaml_content, identity.user)


@router.get("/history", response_model=HistoryResponse)
def get_history(
    customer: str | None = None,
    status: str | None = None,
    bid_id: int | None = Query(default=None, ge=1),
    session: Session = Depends(get_db),
):
    stmt = select(Changelog, Bid).join(Bid, Bid.id == Changelog.bid_id)
    if customer:
        stmt = stmt.where(Bid.customer_name.ilike(f"%{customer.strip()}%"))
    if status:
        stmt = stmt.where(Bid.status == status)
    if bid_id is not None:
        stmt = stmt.where(Changelog.bid_id == bid_id)
    rows = session.execute(stmt.order_by(Changelog.created_at.desc(), Changelog.id.desc())).all()
    return {"items": [{"id": log.id, "bid_id": bid.id, "project_name": bid.project_name, "customer_name": bid.customer_name, "status": bid.status, "actor": log.actor, "action": log.action, "field_changed": log.field_changed, "note": log.note, "created_at": log.created_at} for log, bid in rows], "total": len(rows)}
