from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_identity
from app.schemas.api_schemas.approval import TechApprovalIn, PriceApprovalIn, UnlockIn
from app.services.approval_service import tech, price
from app.services.lock_service import unlock_bid
router=APIRouter(prefix="/bids",tags=["approvals"])
@router.post("/{bid_id}/approvals/tech")
def approve_tech(bid_id:int, body:TechApprovalIn, session:Session=Depends(get_db), identity=Depends(get_identity)):
    return tech(session,bid_id,body.decision,identity.user,body.comment,body.skip_with_reason)
@router.post("/{bid_id}/approvals/price")
def approve_price(bid_id:int, body:PriceApprovalIn, session:Session=Depends(get_db), identity=Depends(get_identity)):
    return price(session,bid_id,body,identity.user)
@router.post("/{bid_id}/unlock")
def unlock(bid_id:int, body:UnlockIn, session:Session=Depends(get_db), identity=Depends(get_identity)): return unlock_bid(session,bid_id,identity,body.reason)
