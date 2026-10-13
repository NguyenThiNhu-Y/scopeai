"""Tests cho GET /api/health (contract api_contract.md §3.0)."""

from __future__ import annotations

from datetime import datetime

EXPECTED_FIELDS = {"status", "app", "version", "llm_provider", "database", "time"}


def test_health_ok_shape(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()

    assert set(data.keys()) == EXPECTED_FIELDS
    assert data["status"] == "ok"
    assert data["app"] == "presales-bidding-assistant"
    assert data["version"] == "0.1.0"
    assert data["llm_provider"] == "mock"
    assert data["database"] == "ok"

    # time: UTC ISO 8601, parse được và có timezone.
    dt = datetime.fromisoformat(data["time"].replace("Z", "+00:00"))
    assert dt.tzinfo is not None


def test_health_never_leaks_secrets(client):
    """BR-06: response không chứa LLM_API_KEY / LLM_BASE_URL."""
    resp = client.get("/api/health")
    body = resp.text
    assert "LLM_API_KEY" not in body
    assert "LLM_BASE_URL" not in body
    assert "sk-" not in body


def test_health_degraded_when_db_down(client, monkeypatch):
    """DB lỗi → status=degraded, database=error..., vẫn HTTP 200."""
    from app.core import db as db_module

    def _boom() -> bool:
        raise RuntimeError("hỏng kết nối")

    monkeypatch.setattr(db_module, "check_db", _boom)

    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "degraded"
    assert data["database"].startswith("error")