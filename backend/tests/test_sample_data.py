"""Tests cho hồ sơ mẫu giả lập — contract api_contract.md §3.7 (FR-006, BR-06)."""

from __future__ import annotations


def test_load_ja_sample_default(client):
    resp = client.post("/api/bids/sample", json={})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "draft"
    assert data["customer_language"] == "ja"
    # Dữ liệu 100% hư cấu (BR-06).
    assert "架空" in data["customer_name"] or "仮名" in data["customer_name"]
    assert data["created_by"] == "anonymous"
    assert data["budget_amount"] == 15000000
    assert data["budget_currency"] == "JPY"
    assert data["customer_schedule_start"] == "2027-01-01"
    assert data["customer_schedule_end"] == "2027-09-30"


def test_load_vi_sample(client):
    key = "vi_email"
    resp = client.post("/api/bids/sample", json={"sample_key": key})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "draft"
    assert data["customer_language"] == "vi"
    assert "giả lập" in data["customer_name"]


def test_sample_content_has_fake_note_and_pii(client):
    """Nội dung mẫu có ghi chú 'DỮ LIỆU GIẢ LẬP' + email/SĐT (để minh chứng mask)."""
    resp = client.post("/api/bids/sample", json={})
    assert resp.status_code == 201
    bid_id = resp.json()["id"]

    from app.core import db
    from app.models import Bid

    session = db.SessionLocal()
    try:
        bid = session.get(Bid, bid_id)
        assert bid is not None
        assert "DỮ LIỆU GIẢ LẬP" in bid.request_content
        assert "tanaka.hanako@example.co.jp" in bid.request_content
        assert "03-1234-5678" in bid.request_content
    finally:
        session.close()


def test_sample_unknown_key(client):
    key = "unknown_key"
    resp = client.post("/api/bids/sample", json={"sample_key": key})
    assert resp.status_code == 400
    body = resp.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    fields = {err["field"] for err in body["details"]["errors"]}
    assert "sample_key" in fields


def test_sample_no_body_defaults_ja(client):
    resp = client.post("/api/bids/sample")
    assert resp.status_code == 201
    assert resp.json()["customer_language"] == "ja"
