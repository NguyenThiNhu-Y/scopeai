from urllib.parse import quote
import unicodedata
import re
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.api.deps import Identity, get_db, get_identity
from app.services.export_service import artifacts, log_export
from app.exporters.filename import export_filename
from app.llm.gateway import get_llm_client
from app.exporters.requirements_xlsx import render_requirement_workbook
from app.models import Bid

router = APIRouter(prefix="/bids", tags=["exports"])


def _response(session, bid_id, kind, actor, content_type):
    bid, approved, ja, files = artifacts(session, bid_id, actor, get_llm_client())
    if kind == "bundle":
        from app.exporters.bundle import make_bundle
        body = make_bundle([files[x] for x in ("docx", "xlsx", "pdf")]); filename = export_filename(bid.customer_name, bid.project_name, "bundle", ext="zip")
    else:
        filename, body = files[kind]
    log_export(session, bid, "bundle_zip" if kind == "bundle" else kind, actor, approved, ja)
    ascii_filename = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")
    ascii_filename = re.sub(r"\s+", "-", ascii_filename) or "export"
    headers = {
        "Content-Disposition": (
            f'attachment; filename="{ascii_filename}"; '
            f"filename*=UTF-8''{quote(filename)}"
        )
    }
    if bid.customer_language == "ja": headers["X-Ja-Check-Result"] = quote(__import__("json").dumps(ja, ensure_ascii=False))
    return Response(body, media_type=content_type, headers=headers)


@router.get("/{bid_id}/exports/proposal.docx")
def proposal_docx(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)): return _response(session, bid_id, "docx", identity.user, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@router.get("/{bid_id}/exports/estimate.xlsx")
def estimate_xlsx(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)): return _response(session, bid_id, "xlsx", identity.user, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@router.get("/{bid_id}/exports/proposal.pdf")
def proposal_pdf(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)): return _response(session, bid_id, "pdf", identity.user, "application/pdf")

@router.get("/{bid_id}/exports/bundle.zip")
def bundle_zip(bid_id: int, session: Session = Depends(get_db), identity: Identity = Depends(get_identity)): return _response(session, bid_id, "bundle", identity.user, "application/zip")


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
