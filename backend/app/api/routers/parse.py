from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.api_schemas.attachment import ParseOut,ParseConfirmIn
from app.services.parse_service import parse,confirm
router=APIRouter(prefix="/bids",tags=["parse"])
@router.post("/{bid_id}/parse",response_model=ParseOut)
def parse_files(bid_id:int,session:Session=Depends(get_db)): return parse(session,bid_id)
@router.put("/{bid_id}/parse/confirm")
def confirm_parse(bid_id:int,body:ParseConfirmIn,session:Session=Depends(get_db)): return {"id":confirm(session,bid_id,body.data_readiness,body.confirmed).id,"status":"draft","data_readiness":body.data_readiness}
