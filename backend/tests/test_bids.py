"""Tests cho endpoints hồ sơ — contract api_contract.md §3 (M2, FR-001/FR-007)."""

from __future__ import annotations

from io import BytesIO

from sqlalchemy import select

from app.core import db
from app.models import Bid, Requirement
from tests.helpers import VALID_PAYLOAD, create_bid, step_status, wait_until


def _post(client, payload, headers=None):
    return client.post("/api/bids", json=payload, headers=headers or {"X-User": "Nhu"})


def test_create_bid_happy_path(client):
    resp = _post(client, VALID_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["project_name"] == VALID_PAYLOAD["project_name"]
    assert data["customer_name"] == VALID_PAYLOAD["customer_name"]
    assert data["customer_language"] == "ja"
    assert data["status"] == "draft"
    assert data["locked"] is False
    assert data["budget_amount"] == 50000000
    assert data["budget_currency"] == "JPY"
    assert data["created_by"] == "Nhu"
    assert data["created_at"] is not None


def test_sample_preview_returns_form_and_three_files_without_creating_bid(client):
    before = client.get("/api/bids").json()["total"]
    response = client.get("/api/bids/sample/preview", params={"sample_key": "ja_email"})

    assert response.status_code == 200
    data = response.json()
    assert data["sample_key"] == "ja_email"
    assert data["customer_language"] == "ja"
    assert len(data["files"]) == 3
    assert {item["filename"] for item in data["files"]} == {
        "ja_email.md",
        "ja_rfp.docx",
        "ja_requirements.xlsx",
    }
    assert client.get("/api/bids").json()["total"] == before


def test_sample_preview_rejects_unknown_sample(client):
    response = client.get("/api/bids/sample/preview", params={"sample_key": "unknown"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_bid_request_content_too_short(client):
    payload = {**VALID_PAYLOAD, "request_content": "ngắn quá"}
    resp = _post(client, payload)
    assert resp.status_code == 400
    body = resp.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    assert body["details"]["min_length"] == 30


def test_create_bid_missing_field(client):
    payload = {**VALID_PAYLOAD}
    del payload["project_name"]
    resp = _post(client, payload)
    assert resp.status_code == 400
    body = resp.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"]  # message tiếng Việt, hành động được


def test_create_bid_invalid_language(client):
    payload = {**VALID_PAYLOAD, "customer_language": "fr"}
    resp = _post(client, payload)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_bid_detail_with_pipeline_progress(client):
    bid_id = create_bid(client)
    resp = client.get(f"/api/bids/{bid_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["no_requirement_file"] is False
    assert data["data_readiness"] is None
    assert data["display_currency"] == "VND"

    progress = data["pipeline_progress"]
    keys = {s["step_key"] for s in progress["steps"]}
    assert keys == {"intake", "gap", "evaluate", "solution", "wbs", "proposal"}
    assert all(s["status"] in {"pending", "skipped"} for s in progress["steps"])
    assert progress["waiting_clarification"] is False
    assert progress["rounds_used"] == 0
    assert progress["max_rounds"] == 2


def test_get_bid_not_found(client):
    resp = client.get("/api/bids/9999")
    assert resp.status_code == 404
    body = resp.json()["error"]
    assert body["code"] == "NOT_FOUND"
    assert body["message"]


def test_list_bids_status_filter(client):
    bid_a = create_bid(client)
    bid_b = create_bid(client, project_name="Dự án thứ hai (giả lập)")

    # Đẩy bid_a sang analyzing trực tiếp qua DB (API không có endpoint đổi status).
    session = db.SessionLocal()
    try:
        bid = session.get(Bid, bid_a)
        assert bid is not None
        bid.status = "analyzing"
        session.commit()
    finally:
        session.close()

    resp = client.get("/api/bids", params={"status": "analyzing"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == bid_a

    resp = client.get("/api/bids", params={"status": "draft"})
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["id"] == bid_b


def test_list_bids_exposes_created_at_and_filters_deal_stage(client):
    bid_a = create_bid(client, project_name="Hồ sơ giai đoạn khám phá")
    bid_b = create_bid(client, project_name="Hồ sơ giai đoạn triển khai")
    session = db.SessionLocal()
    try:
        bid_a_row = session.get(Bid, bid_a)
        bid_b_row = session.get(Bid, bid_b)
        assert bid_a_row is not None
        assert bid_b_row is not None
        bid_a_row.deal_stage = "discovery"
        bid_b_row.deal_stage = "delivery"
        session.commit()
    finally:
        session.close()

    response = client.get("/api/bids", params={"deal_stage": "discovery"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == bid_a
    assert data["items"][0]["deal_stage"] == "discovery"
    assert data["items"][0]["created_at"]
    assert data["items"][0]["total_price"] is None
    assert data["items"][0]["total_price_currency"] is None


def test_bid_detail_is_available_to_the_single_mvp_user(client):
    bid_id = create_bid(client)
    response = client.get(f"/api/bids/{bid_id}", headers={"X-Actor": "another-user"})
    assert response.status_code == 200


def test_list_bids_q_search(client):
    create_bid(client, project_name="Hệ thống CRM khách hàng ABC")
    create_bid(client, project_name="Hệ thống quản lý kho", customer_name="Công ty Minh Phát (giả lập)")

    resp = client.get("/api/bids", params={"q": "CRM"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["project_name"] == "Hệ thống CRM khách hàng ABC"

    resp = client.get("/api/bids", params={"q": "Minh Phát"})
    assert resp.json()["total"] == 1

    resp = client.get("/api/bids", params={"q": "không tồn tại"})
    assert resp.json()["total"] == 0


def test_list_bids_pagination(client):
    for i in range(3):
        create_bid(client, project_name=f"Dự án số {i} (giả lập)")

    resp = client.get("/api/bids", params={"page": 1, "page_size": 2})
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2

    resp = client.get("/api/bids", params={"page": 2, "page_size": 2})
    assert len(resp.json()["items"]) == 1


def test_prompt_sent_to_llm_is_masked(client, mock_llm):
    """BR-06: prompt gửi mock đã che email/SĐT gốc (spec §5(c))."""
    from app.llm.mock_client import MockLLMClient

    client_llm = MockLLMClient()
    mock_llm["client"] = client_llm

    # Nạp mẫu tiếng Nhật — chứa tanaka.hanako@example.co.jp + 03-1234-5678.
    resp = client.post("/api/bids/sample", json={})
    assert resp.status_code == 201
    bid_id = resp.json()["id"]

    resp = client.post(f"/api/bids/{bid_id}/parse")
    assert resp.status_code == 200
    resp = client.put(
        f"/api/bids/{bid_id}/parse/confirm",
        json={"data_readiness": "medium", "confirmed": True},
    )
    assert resp.status_code == 200
    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202

    assert wait_until(lambda: step_status(client, bid_id, "intake") == "completed")
    intake_prompts = client_llm.prompts_by_schema.get("IntakeExtraction", [])
    assert intake_prompts, "Chưa có prompt intake nào được gửi"
    intake_prompt = intake_prompts[0]
    assert "tanaka.hanako@example.co.jp" not in intake_prompt
    assert "03-1234-5678" not in intake_prompt
    assert "[EMAIL]" in intake_prompt
    assert "[PHONE_JP]" in intake_prompt


def test_parse_two_requirement_files_generates_unique_internal_codes(client):
    """Regression: 2 file requirement cùng sinh mã dự phòng REQ-xxx.

    Trước đây mỗi file gọi normalize() riêng → mã REQ-001.. trùng nhau →
    vi phạm unique (bid_id, internal_code) → 500. Giờ mã phải duy nhất
    trên toàn bộ lượt parse.
    """
    bid_id = create_bid(client)

    def upload(name: str, content: str) -> None:
        resp = client.post(
            f"/api/bids/{bid_id}/attachments",
            params={"file_type": "requirement"},
            files={"file": (name, BytesIO(content.encode("utf-8")), "text/csv")},
        )
        assert resp.status_code == 201, resp.text

    # Không có cột mã → cả hai file đều cần mã dự phòng REQ-xxx.
    upload("req_a.csv", "nội dung\nyêu cầu A1\nyêu cầu A2\n")
    upload("req_b.csv", "nội dung\nyêu cầu B1\nyêu cầu B2\n")

    resp = client.post(f"/api/bids/{bid_id}/parse")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["requirements"]["count"] == 4
    assert all(a["status"] == "ok" for a in data["attachments"])

    session = db.SessionLocal()
    try:
        codes = [
            r.internal_code
            for r in session.scalars(select(Requirement).where(Requirement.bid_id == bid_id))
        ]
        assert len(codes) == 4
        assert len(codes) == len(set(codes)), codes
    finally:
        session.close()


def test_parse_unknown_bid_returns_404(client):
    resp = client.post("/api/bids/999999/parse")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"
