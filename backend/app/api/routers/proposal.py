from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_identity
from app.schemas.api_schemas.proposal import ProposalOut, ProposalUpdateIn, ProposalTranslateIn
from app.services import proposal_service
router = APIRouter(prefix="/bids", tags=["proposal"])
@router.get("/{bid_id}/proposal", response_model=ProposalOut)
def get_proposal(bid_id: int, session: Session = Depends(get_db)): return proposal_service.to_out(session, bid_id)
@router.put("/{bid_id}/proposal", response_model=ProposalOut)
def put_proposal(bid_id: int, body: ProposalUpdateIn, session: Session = Depends(get_db), identity=Depends(get_identity)):
    return proposal_service.update(session, bid_id, body, identity.user)

@router.post("/{bid_id}/proposal/translate", response_model=ProposalOut)
def translate_proposal(bid_id: int, body: ProposalTranslateIn, session: Session = Depends(get_db), identity=Depends(get_identity)):
    return proposal_service.translate(session, bid_id, body, identity.user)
