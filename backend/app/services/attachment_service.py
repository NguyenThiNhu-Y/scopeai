from __future__ import annotations
from pathlib import Path
import re
from app.api.errors import ApiError, not_found, state_conflict
from app.models import Attachment, Bid
from app.parsers.detect import detect_type
MAX_SIZE=20*1024*1024; MAX_FILES=10
ALLOWED_FILE_TYPES = {"rfp", "requirement", "sample_data"}


def add(session, bid_id, filename, data, file_type=None):
    bid=session.get(Bid,bid_id)
    if not bid: raise not_found()
    if session.query(Attachment).filter_by(bid_id=bid_id).count() >= MAX_FILES: raise ApiError(400,"TOO_MANY_FILES","Hồ sơ đã có tối đa 10 file")
    if len(data)>MAX_SIZE: raise ApiError(400,"FILE_TOO_LARGE","File vượt quá giới hạn 20 MB",{"max_bytes":MAX_SIZE})
    if not filename or Path(filename).name != filename or "\\" in filename:
        raise ApiError(400,"INVALID_FILE_TYPE","Tên file không hợp lệ")
    if file_type is not None and file_type not in ALLOWED_FILE_TYPES:
        raise ApiError(400,"INVALID_FILE_TYPE","Loại file không được hỗ trợ")
    try: detected=detect_type(filename,data)
    except ValueError as exc: raise ApiError(400,"INVALID_FILE_TYPE",str(exc)) from exc
    root=Path("data/uploads")/str(bid_id); root.mkdir(parents=True,exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename).name)
    path=(root/(f"{len(data)}_{safe_name}")).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ApiError(400,"INVALID_FILE_TYPE","Tên file không hợp lệ")
    path.write_bytes(data)
    obj=Attachment(bid_id=bid_id,filename=filename,file_type=file_type or detected,detected_type=detected,size_bytes=len(data),path=str(path),original_path=str(path))
    session.add(obj); session.commit(); session.refresh(obj); return obj
def update(session,bid_id,attachment_id,body):
    obj=session.get(Attachment,attachment_id)
    if not obj or obj.bid_id!=bid_id: raise not_found("Không tìm thấy file đính kèm")
    bid=session.get(Bid,bid_id)
    if bid.locked: raise state_conflict("Hồ sơ đã khóa, không thể đổi mapping")
    changed=body.file_type is not None or body.sheet_mappings is not None
    if body.file_type: obj.file_type=body.file_type
    if body.sheet_mappings is not None: obj.sheet_mappings=[x.model_dump() for x in body.sheet_mappings]
    if changed: obj.parse_status="pending"; obj.parse_error=None
    session.commit(); session.refresh(obj); return obj
