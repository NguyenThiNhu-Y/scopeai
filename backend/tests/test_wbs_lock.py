"""Tests lock guard — PUT /wbs, PUT /schedule, POST /wbs/snapshot trên hồ sơ
``locked=true`` → 409 STATE_CONFLICT (FR-042.4, M3-REV-002)."""

from __future__ import annotations

from app.core import db
from app.models import Bid
from tests.helpers import default_team_allocation, setup_wbs_bid


def _lock(bid_id: int) -> None:
    session = db.SessionLocal()
    try:
        bid = session.get(Bid, bid_id)
        assert bid is not None
        bid.locked = True
        session.commit()
    finally:
        session.close()


def test_put_wbs_locked_returns_409(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    _lock(bid_id)
    resp = client.put(
        f"/api/bids/{bid_id}/wbs",
        json={
            "changes": [
                {"op": "add", "task": {
                    "task_code": "WBS-002-01-05", "name_vi": "Task",
                    "phase": "mvp", "parent_code": "WBS-002-01",
                    "role": "qa", "man_day": 2.0, "depends_on": []}},
            ],
            "by": "ai_developer",
        },
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 409
    body = resp.json()["error"]
    assert body["code"] == "STATE_CONFLICT"
    assert "khóa" in body["message"].lower()


def test_put_schedule_locked_returns_409(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    _lock(bid_id)
    resp = client.put(
        f"/api/bids/{bid_id}/schedule",
        json={
            "start_date": "2026-11-01",
            "buffer_days": 0,
            "working_calendar": "vn",
            "team_allocation": default_team_allocation(),
            "by": "ai_developer",
        },
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "STATE_CONFLICT"


def test_snapshot_locked_returns_409(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    _lock(bid_id)
    resp = client.post(
        f"/api/bids/{bid_id}/wbs/snapshot",
        json={"reason": "Test khóa", "by": "ai_developer"},
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "STATE_CONFLICT"


def test_get_wbs_still_available_when_locked(client):
    """Xem WBS vẫn cho phép trên hồ sơ khóa (contract §1.7)."""
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    _lock(bid_id)
    resp = client.get(f"/api/bids/{bid_id}/wbs")
    assert resp.status_code == 200