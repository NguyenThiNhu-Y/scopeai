import json
from urllib.parse import quote

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import Identity, get_db, get_identity
from app.api.errors import not_found
from app.exporters.bundle import make_bundle
from app.exporters.filename import content_disposition, export_filename
from app.exporters.requirements_xlsx import render_requirement_workbook
from app.llm.gateway import get_llm_client
from app.models import Bid
from app.services.export_service import BUNDLE_KINDS, artifacts, log_export

router = APIRouter(prefix="/bids", tags=["exports"])

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PPTX_MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def _response(session: Session, bid_id: int, kind: str, actor: str, content_type: str) -> Response:
    kinds = BUNDLE_KINDS if kind == "bundle" else (kind,)
    bid, approved, ja, files, export_date = artifacts(session, bid_id, get_llm_client(), kinds)
    if kind == "bundle":
        body = make_bundle([files[x] for x in BUNDLE_KINDS])
        filename = export_filename(bid.customer_name, bid.project_name, "bundle", export_date=export_date, ext="zip")
    else:
        filename, body = files[kind]
    log_export(session, bid, "bundle_zip" if kind == "bundle" else kind, actor, approved, ja)
    headers = {"Content-Disposition": content_disposition(filename)}
    if bid.customer_language == "ja":
        headers["X-Ja-Check-Result"] = quote(json.dumps(ja, ensure_ascii=False))
    return Response(body, media_type=content_type, headers=headers)


@router.get("/{bid_id}/exports/proposal.docx")
def proposal_docx(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)):
    return _response(session, bid_id, "docx", identity.user, DOCX_MIME)


@router.get("/{bid_id}/exports/estimate.xlsx")
def estimate_xlsx(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)):
    return _response(session, bid_id, "xlsx", identity.user, XLSX_MIME)


@router.get("/{bid_id}/exports/proposal.pdf")
def proposal_pdf(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)):
    return _response(session, bid_id, "pdf", identity.user, "application/pdf")


@router.get("/{bid_id}/exports/proposal.pptx")
def proposal_pptx(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)):
    return _response(session, bid_id, "pptx", identity.user, PPTX_MIME)


@router.get("/{bid_id}/exports/bundle.zip")
def bundle_zip(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)):
    return _response(session, bid_id, "bundle", identity.user, "application/zip")


@router.get("/{bid_id}/exports/requirements.xlsx")
def requirements_xlsx(
    bid_id: int,
    note_language: str | None = Query(default=None, pattern="^(vi|en|ja)$"),
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
):
    bid = session.get(Bid, bid_id)
    if bid is None:
        raise not_found()
    filename, body = render_requirement_workbook(session, bid_id, bid.customer_language, note_language)
    return Response(body, media_type=XLSX_MIME, headers={"Content-Disposition": content_disposition(filename)})


@router.get("/{bid_id}/exports/requirements.xlsx")
def requirements_xlsx(
    bid_id: int,
    note_language: str | None = Query(default=None, pattern="^(vi|en|ja)$"),
    session: Session = Depends(get_db),
    identity: Identity = Depends(get_identity),
):
    bid = session.get(Bid, bid_id)
    if bid is None:
        from app.api.errors import not_found
        raise not_found()
    filename, body = render_requirement_workbook(session, bid_id, bid.customer_language, note_language)
    return Response(body, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{filename}"'})
