from sqlalchemy import delete, select
from app.api.errors import not_found, pipeline_error, state_conflict
from app.models import Attachment, Requirement, Bid
from app.parsers.excel import read_sheets
from app.parsers.requirements import normalize
from app.parsers.sample_profile import profile
from app.parsers.text import extract_text
from app.parsers.pdf import extract_text as pdf_text
from app.parsers.docx import extract_text as docx_text
def parse(session,bid_id):
    bid=session.get(Bid,bid_id)
    if not bid: raise not_found()
    attachments=list(session.scalars(select(Attachment).where(Attachment.bid_id==bid_id)))
    session.execute(delete(Requirement).where(Requirement.bid_id==bid_id)); all_req=[]; prof=[]; used_codes=set()
    for a in attachments:
        try:
            data=open(a.original_path or a.path,"rb").read(); ext=a.filename.lower()
            if a.file_type=="requirement":
                sheets=read_sheets(data,a.filename); maps={m["sheet_name"]:m.get("col_map",{}) for m in (a.sheet_mappings or [])}; all_req += normalize(sheets,maps,used_codes)
            elif a.file_type=="sample_data":
                sheets=read_sheets(data,a.filename); prof += [profile(rows) for rows in sheets.values()]
            elif ext.endswith(".pdf"): pdf_text(data)
            elif ext.endswith(".docx"): docx_text(data)
            elif ext.endswith((".txt",".md")): extract_text(data)
            a.parse_status="ok"; a.parse_error=None
        except Exception as exc: a.parse_status="error"; a.parse_error=str(exc)
    for item in all_req: session.add(Requirement(bid_id=bid_id,**item))
    bid.no_requirement_file=not any(a.file_type=="requirement" and a.parse_status=="ok" for a in attachments)
    session.commit()
    if any(a.parse_status=="error" for a in attachments):
        # Partial parse is useful for review; only fail when every attachment failed.
        if attachments and all(a.parse_status=="error" for a in attachments): raise pipeline_error("Không đọc được file nào",{"attachments":[a.filename for a in attachments]})
    return {"requirements":{"count":len(all_req),"no_requirement_file":bid.no_requirement_file},"attachments":[{"id":a.id,"filename":a.filename,"status":a.parse_status,"error":a.parse_error} for a in attachments],"sample_profile":prof[0] if prof else None,"column_mapping_confirmed":bool(all_req)}
def confirm(session,bid_id,readiness,confirmed):
    bid=session.get(Bid,bid_id)
    if not bid: raise state_conflict("Không tìm thấy hồ sơ")
    if not confirmed: raise state_conflict("Phải xác nhận dữ liệu trước khi phân tích")
    attachments = list(session.scalars(select(Attachment).where(Attachment.bid_id == bid_id)))
    if attachments and any(a.parse_status != "ok" for a in attachments):
        raise state_conflict(
            "Cần đọc thành công tất cả file đính kèm trước khi xác nhận",
            {"required": "POST /api/bids/{id}/parse", "confirmed": False},
        )
    bid.data_readiness=readiness; session.commit(); return bid
