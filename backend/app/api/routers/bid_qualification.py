from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_identity
from app.schemas.api_schemas.bid_qualification import BidQualificationOut, BidQualificationUpdate
from app.services import bid_qualification_service

router = APIRouter(prefix="/bids", tags=["bid-qualification"])


@router.get("/{bid_id}/bid-qualification", response_model=BidQualificationOut)
def get_qualification(bid_id: int, session: Session = Depends(get_db)):
    return bid_qualification_service.to_out(session, bid_id)


@router.put("/{bid_id}/bid-qualification", response_model=BidQualificationOut)
def put_qualification(bid_id: int, body: BidQualificationUpdate, session: Session = Depends(get_db), identity=Depends(get_identity)):
    return bid_qualification_service.update(session, bid_id, body, identity.user)
