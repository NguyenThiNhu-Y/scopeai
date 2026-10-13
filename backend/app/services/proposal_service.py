from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.errors import not_found, validation_error
from app.models import Bid, ProposalDraft
from app.models import Quotation
from app.services.quotation_engine import quotation_to_out
from app.schemas.api_schemas.proposal import SECTION_NAMES, ProposalSections, ProposalUpdateIn, ProposalTranslateIn

PLACEHOLDER = "[Đang chờ proposal]"
DEFAULT_SECTIONS = {key: PLACEHOLDER for key in SECTION_NAMES}


def _normalize_sections(raw) -> dict[str, str]:
    """Đưa sections về đúng 8 mục chuẩn (BR-09: fix ở lớp đọc, không migrate DB).

    Dữ liệu cũ (bid 80..110) lưu schema 5 mục: thiếu
    ``requirements_understanding``/``schedule``/``team``/``assumptions_and_scope``
    và thừa ``conclusion``. Key thiếu → điền placeholder; key thừa → loại bỏ;
    giá trị rỗng → placeholder (tránh 500 do ``ProposalSections`` min_length=1).
    """
    if not isinstance(raw, dict):
        raw = {}
    out: dict[str, str] = {}
    for key in SECTION_NAMES:
        value = raw.get(key)
        if value is None or not str(value).strip():
            out[key] = PLACEHOLDER
        else:
            out[key] = str(value)
    return out


def _normalize_translations(raw) -> dict[str, dict]:
    """Normalize từng bản dịch trong ``translations`` (cùng rủi ro schema cũ)."""
    if not isinstance(raw, dict):
        return {}
    return {lang: _normalize_sections(sections) for lang, sections in raw.items()}


def get_or_create(session: Session, bid_id: int) -> ProposalDraft:
    bid = session.get(Bid, bid_id)
    if not bid: raise not_found()
    row = session.execute(select(ProposalDraft).where(ProposalDraft.bid_id == bid_id)).scalar_one_or_none()
    if row is None:
        row = ProposalDraft(bid_id=bid_id, sections=DEFAULT_SECTIONS, assumptions_phrased=[], scope_out_phrased=[], customer_language=bid.customer_language, translations={})
        session.add(row); session.commit(); session.refresh(row)
    return row
def to_out(session, bid_id):
    row = get_or_create(session, bid_id); bid = session.get(Bid, bid_id)
    quotation_markdown = "[Presales điền]"
    if bid.locked:
        quotation = session.execute(select(Quotation).where(Quotation.bid_id == bid_id).order_by(Quotation.id.desc())).scalars().first()
        if quotation:
            output = quotation_to_out(quotation, bid)
            currency = output.get("currency", "VND")
            quotation_markdown = "\n".join([
                "### Quotation",
                f"- Currency: {currency}",
                f"- Grand total: {output['totals']['grand_total']}",
                f"- Valid until: {output['valid_until']}",
            ])
    sections = {key: value.replace("{{QUOTATION}}", quotation_markdown) for key, value in _normalize_sections(row.sections).items()}
    return {"bid_id": bid_id, "sections": sections, "assumptions_phrased": row.assumptions_phrased, "scope_out_phrased": row.scope_out_phrased, "price_gate": "approved" if bid.locked else "placeholder", "editable": True, "updated_at": row.updated_at, "quotation_markdown": quotation_markdown, "customer_language": row.customer_language, "translations": _normalize_translations(row.translations or {}), "document": {"page_size": "A4", "cover": True, "table_of_contents": list(sections), "printable": True}}
def update(session, bid_id, data: ProposalUpdateIn, by: str):
    row = get_or_create(session, bid_id)
    text = " ".join(data.sections.model_dump().values())
    if __import__("re").search(r"(?:[$¥₫]\s*\d|\d\s*[$¥₫]|\b(?:man-day|person-day|MD)\b\s*\d*)", text, __import__("re").I):
        raise validation_error("Nội dung proposal không được chứa tiền hoặc man-day")
    row.sections = data.sections.model_dump(); row.edited_by = by
    if data.customer_language:
        row.customer_language = data.customer_language
    session.commit(); session.refresh(row)
    return to_out(session, bid_id)

def translate(session: Session, bid_id: int, data: ProposalTranslateIn, by: str):
    row = get_or_create(session, bid_id)
    sections = (data.sections or ProposalSections.model_validate(_normalize_sections(row.sections))).model_dump()
    row.translations = {**(row.translations or {}), data.language: sections}
    row.edited_by = by
    session.commit(); session.refresh(row)
    return to_out(session, bid_id)
