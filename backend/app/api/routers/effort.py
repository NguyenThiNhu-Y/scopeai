from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.api_schemas.effort import EffortOut
from app.services.solution_service import get_effort

router = APIRouter(prefix="/bids", tags=["effort"])


@router.get("/{bid_id}/effort", response_model=EffortOut)
def effort(bid_id: int, session: Session = Depends(get_db)) -> EffortOut:
    return EffortOut(**get_effort(session, bid_id))
