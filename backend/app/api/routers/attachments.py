from fastapi import APIRouter, Depends, File, UploadFile, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import Identity, get_db, get_identity
from app.schemas.api_schemas.attachment import AttachmentOut, AttachmentListOut, AttachmentUpdate
from app.models import Attachment
from app.services import attachment_service
router=APIRouter(prefix="/bids",tags=["attachments"])
MAX_UPLOAD_SIZE = attachment_service.MAX_SIZE

async def _read_upload_bounded(file: UploadFile) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(min(1024 * 1024, MAX_UPLOAD_SIZE + 1 - total))
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > MAX_UPLOAD_SIZE:
            break
    return b"".join(chunks)

def out(a): return AttachmentOut.model_validate(a,from_attributes=True)
@router.post("/{bid_id}/attachments",response_model=AttachmentOut,status_code=201)
async def upload(bid_id:int,file:UploadFile=File(...),file_type:str|None=Query(None),session:Session=Depends(get_db),identity:Identity=Depends(get_identity)):
    return out(attachment_service.add(session,bid_id,file.filename or "",await _read_upload_bounded(file),file_type))
@router.get("/{bid_id}/attachments",response_model=AttachmentListOut)
def list_files(bid_id:int,session:Session=Depends(get_db),identity:Identity=Depends(get_identity)):
    return {"items":[out(a) for a in session.scalars(select(Attachment).where(Attachment.bid_id==bid_id))]}
@router.put("/{bid_id}/attachments/{attachment_id}",response_model=AttachmentOut)
def update(bid_id:int,attachment_id:int,body:AttachmentUpdate,session:Session=Depends(get_db),identity:Identity=Depends(get_identity)):
    return out(attachment_service.update(session,bid_id,attachment_id,body))
