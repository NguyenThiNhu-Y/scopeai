from io import BytesIO
import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import Identity, get_db, get_identity
from app.api.errors import not_found
from app.models import Bid, Changelog
from app.schemas.api_schemas.settings import HistoryResponse, SettingsResponse, SettingUpdate, SettingUpdated
from app.services import case_study_service, settings_service

router = APIRouter(tags=["settings"])


@router.get("/eval/reports/latest")
def eval_report_latest():
    """Báo cáo đánh giá hệ thống mới nhất (thiet_ke_danh_gia.md §6.4).

    Đọc file JSON mới nhất trong ``docs/eval/reports/`` — chỉ hiển thị, không tính.
    Đường dẫn resolve từ vị trí file code (không theo CWD) — D-13-1 / Đợt 14 D3.
    """
    reports_dir = Path(__file__).resolve().parents[4] / "docs" / "eval" / "reports"
    files = sorted(reports_dir.glob("eval_*.json")) if reports_dir.is_dir() else []
    if not files:
        raise not_found("Chưa có báo cáo đánh giá hệ thống")
    return json.loads(files[-1].read_text(encoding="utf-8"))


@router.get("/settings", response_model=SettingsResponse)
def get_settings(session: Session = Depends(get_db)):
    return {"keys": settings_service.list_settings(session)}


@router.put("/settings/{key}", response_model=SettingUpdated)
def put_setting(key: str, body: SettingUpdate, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)):
    return settings_service.update_setting(session, key, body.yaml_content, identity.user)


@router.get("/settings/case_studies/template")
def case_studies_template(session: Session = Depends(get_db)):
    """Tải file Excel mẫu để nhập case study (thiet_ke_danh_gia.md §3.3)."""
    data = case_study_service.build_template_xlsx()
    return StreamingResponse(
        BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="case_studies_template.xlsx"'
        },
    )


@router.post("/settings/case_studies/import")
def case_studies_import(
    file: UploadFile = File(...),
    mode: str = Form(default="preview"),
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
):
    """Nhập case study từ .xlsx/.csv/.yaml — preview (lỗi theo dòng) hoặc save."""
    return case_study_service.import_cases(
        session, file.filename or "import.yaml", file.file.read(), mode, identity.user
    )


@router.post("/settings/case_studies/{case_id}/wbs")
def case_studies_upload_wbs(
    case_id: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
):
    """Tải file WBS Excel của dự án cũ lên theo case (thiet_ke_danh_gia.md §3.4)."""
    return case_study_service.upload_wbs(
        session, case_id, file.filename or "wbs.xlsx", file.file.read(), identity.user
    )


@router.get("/settings/case_studies/{case_id}/wbs")
def case_studies_download_wbs(case_id: str, session: Session = Depends(get_db)):
    """Tải file WBS của case về (file tải lên hoặc file mặc định trong reference)."""
    filename, data = case_study_service.download_wbs(session, case_id)
    return StreamingResponse(
        BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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
