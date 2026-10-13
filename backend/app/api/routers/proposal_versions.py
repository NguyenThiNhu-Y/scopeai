from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_identity
from app.models import Bid, ProposalVersion, Changelog
from app.api.errors import not_found
from app.schemas.api_schemas.proposal import ProposalVersionCreateIn, ProposalVersionOut, ProposalVersionSentIn
from app.services.proposal_service import to_out

router = APIRouter(prefix="/bids", tags=["proposal-versions"])

@router.get("/{bid_id}/proposal/versions", response_model=list[ProposalVersionOut])
def list_versions(bid_id: int, session: Session = Depends(get_db)):
    if not session.get(Bid, bid_id): raise not_found()
    return session.scalars(select(ProposalVersion).where(ProposalVersion.bid_id == bid_id).order_by(ProposalVersion.id)).all()

@router.post("/{bid_id}/proposal/versions", response_model=ProposalVersionOut, status_code=201)
def create_version(bid_id: int, body: ProposalVersionCreateIn, session: Session = Depends(get_db), identity=Depends(get_identity)):
    bid = session.get(Bid, bid_id)
    if not bid: raise not_found()
    draft = to_out(session, bid_id)
    existing = session.scalars(select(ProposalVersion).where(ProposalVersion.bid_id == bid_id).order_by(ProposalVersion.id)).all()
    if not existing:
        version = "1.0"
    elif len(existing) == 1:
        version = "1.1"
    else:
        major = int(existing[-1].version.split(".")[0]) + 1
        version = f"{major}.0"
    row = ProposalVersion(bid_id=bid_id, version=version, customer_language=body.language or bid.customer_language, sections=draft["sections"], created_by=body.by or identity.user)
    session.add(row); session.commit(); session.refresh(row)
    return row

@router.put("/{bid_id}/proposal/versions/{version_id}/sent", response_model=ProposalVersionOut)
def mark_sent(bid_id: int, version_id: int, body: ProposalVersionSentIn | None = None, session: Session = Depends(get_db), identity=Depends(get_identity)):
    row = session.get(ProposalVersion, version_id)
    if not row or row.bid_id != bid_id: raise not_found()
    row.sent = True; row.sent_at = datetime.now(timezone.utc); row.sent_note = body.note if body else None
    note = body.note if body and body.note else f"Đã đánh dấu phiên bản {row.version} gửi khách"
    session.add(Changelog(bid_id=bid_id, actor=identity.user, action="send_proposal", field_changed="version", new_value=row.version, note=note))
    session.commit(); session.refresh(row)
    return row
