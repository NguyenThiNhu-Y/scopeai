"""Regression F-01: proposal legacy data (schema cũ 5 mục) → GET trả đủ 8 mục.

DB còn 14 hồ sơ (bid 80..110) lưu ``proposal_drafts.sections`` theo schema cũ:
thiếu ``requirements_understanding``/``schedule``/``team``/``assumptions_and_scope``,
thừa ``conclusion``. Fix ở lớp đọc (BR-09): normalize khi đọc, không migrate DB.
Yêu cầu: GET /api/bids/{id}/proposal trả 200 đủ 8 mục, không crash, không 500.
"""

from sqlalchemy import select

from app.models import ProposalDraft
from app.schemas.api_schemas.proposal import SECTION_NAMES
from app.core import db
from tests.helpers import create_bid

PLACEHOLDER = "[Đang chờ proposal]"

# Đúng schema cũ đang tồn tại trong data/bidding.db (bid 80..110).
LEGACY_SECTIONS = {
    "introduction": "Giới thiệu cũ",
    "solution_overview": "Tổng quan cũ",
    "approach": "Cách làm cũ",
    "risks": "Rủi ro cũ",
    "conclusion": "Kết luận cũ (key thừa)",
}


def _seed_legacy_row(client, sections: dict | None = None) -> int:
    bid_id = create_bid(client)
    row = ProposalDraft(
        bid_id=bid_id,
        sections=sections if sections is not None else LEGACY_SECTIONS,
        assumptions_phrased=[],
        scope_out_phrased=[],
        customer_language="vi",
        translations={},
    )
    session = db.SessionLocal()
    try:
        session.add(row)
        session.commit()
    finally:
        session.close()
    return bid_id


def _draft_row(bid_id: int) -> ProposalDraft:
    session = db.SessionLocal()
    try:
        return session.scalars(select(ProposalDraft).where(ProposalDraft.bid_id == bid_id)).one()
    finally:
        session.close()


def test_legacy_5_sections_get_returns_8(client):
    bid_id = _seed_legacy_row(client)
    resp = client.get(f"/api/bids/{bid_id}/proposal")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert set(body["sections"]) == set(SECTION_NAMES)
    assert "conclusion" not in body["sections"]
    for key in SECTION_NAMES:
        assert body["sections"][key], f"sections[{key!r}] rỗng"
    # Key cũ giữ giá trị gốc; key thiếu điền placeholder.
    assert body["sections"]["introduction"] == "Giới thiệu cũ"
    assert body["sections"]["requirements_understanding"] == PLACEHOLDER
    assert body["sections"]["schedule"] == PLACEHOLDER
    assert body["sections"]["team"] == PLACEHOLDER
    assert body["sections"]["assumptions_and_scope"] == PLACEHOLDER
    # Mục lục document cũng đủ 8 mục (FE render headings từ đây).
    assert body["document"]["table_of_contents"] == list(SECTION_NAMES)


def test_legacy_empty_values_filled_with_placeholder(client):
    sections = {**LEGACY_SECTIONS, "introduction": "", "risks": "   "}
    bid_id = _seed_legacy_row(client, sections)
    resp = client.get(f"/api/bids/{bid_id}/proposal")
    assert resp.status_code == 200, resp.text
    body = resp.json()["sections"]
    assert body["introduction"] == PLACEHOLDER
    assert body["risks"] == PLACEHOLDER


def test_legacy_translate_does_not_500(client):
    bid_id = _seed_legacy_row(client)
    resp = client.post(
        f"/api/bids/{bid_id}/proposal/translate",
        json={"language": "en", "by": "Nhu"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert set(body["sections"]) == set(SECTION_NAMES)
    assert set(body["translations"]["en"]) == set(SECTION_NAMES)


def test_update_persists_8_sections_and_db_is_fixed(client):
    bid_id = _seed_legacy_row(client)
    sections = {key: f"Nội dung {key}" for key in SECTION_NAMES}
    resp = client.put(f"/api/bids/{bid_id}/proposal", json={"sections": sections, "by": "Nhu"})
    assert resp.status_code == 200, resp.text
    assert set(resp.json()["sections"]) == set(SECTION_NAMES)
    # Sau PUT, DB được ghi lại đủ 8 mục (không còn key thừa).
    row = _draft_row(bid_id)
    assert set(row.sections) == set(SECTION_NAMES)
    assert "conclusion" not in row.sections