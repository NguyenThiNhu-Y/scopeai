"""Tests PUT /schedule — đổi headcount → lịch tính lại; missing_roles → 400;
locked → 409 (contract §8.4a). Không gọi AI (rule 3)."""

from __future__ import annotations

from app.core import db
from app.llm.mock_client import MockLLMClient
from app.models import Bid, Changelog
from tests.helpers import default_team_allocation, put_schedule, setup_wbs_bid


def test_headcount_change_recalculates_duration(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    sched = put_schedule(client, bid_id)
    backend_days_before = sched["by_role"]["backend"]["duration_days"]
    end_before = sched["end_date"]

    llm = MockLLMClient()
    calls_before = llm.call_count

    allocation = default_team_allocation()
    allocation["backend"] = 1  # 2 → 1
    sched2 = put_schedule(client, bid_id, team_allocation=allocation)

    assert sched2["by_role"]["backend"]["duration_days"] > backend_days_before
    assert sched2["end_date"] > end_before
    assert llm.call_count == calls_before  # không gọi AI


def test_phase_headcount_change_recalculates_only_selected_phase(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    allocation = default_team_allocation()
    before = put_schedule(client, bid_id, team_allocation=allocation)
    phase_allocation = {"mvp": dict(allocation)}
    phase_allocation["mvp"]["backend"] = 1
    after = put_schedule(client, bid_id, team_allocation=allocation, phase_team_allocation=phase_allocation)
    assert after["phase_team_allocation"]["mvp"]["backend"] == 1
    assert after["end_date"] > before["end_date"]


def test_missing_role_returns_400_with_details(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    allocation = default_team_allocation()
    del allocation["infra"]  # WBS có role infra → thiếu headcount
    resp = client.put(
        f"/api/bids/{bid_id}/schedule",
        json={
            "start_date": "2026-11-01",
            "buffer_days": 0,
            "working_calendar": "vn",
            "team_allocation": allocation,
            "by": "ai_developer",
        },
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 400
    body = resp.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    assert body["details"]["missing_roles"] == ["infra"]


def test_negative_headcount_rejected(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    allocation = default_team_allocation()
    allocation["pm"] = -1
    resp = client.put(
        f"/api/bids/{bid_id}/schedule",
        json={
            "start_date": "2026-11-01",
            "buffer_days": 0,
            "working_calendar": "vn",
            "team_allocation": allocation,
            "by": "ai_developer",
        },
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_payment_milestones_default_from_yaml(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    sched = put_schedule(client, bid_id)  # không gửi payment_milestones
    assert sched["payment_milestones"]
    total = sum(m["percent"] for m in sched["payment_milestones"])
    assert total <= 100
    for m in sched["payment_milestones"]:
        assert m["due_date"]  # code tính due_date = start + offset


def test_payment_milestones_over_100_rejected(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    resp = client.put(
        f"/api/bids/{bid_id}/schedule",
        json={
            "start_date": "2026-11-01",
            "buffer_days": 0,
            "working_calendar": "vn",
            "team_allocation": default_team_allocation(),
            "payment_milestones": [
                {"name": "A", "percent": 60, "due_offset_days": 0},
                {"name": "B", "percent": 60, "due_offset_days": 30},
            ],
            "by": "ai_developer",
        },
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_working_calendar_defaults_from_customer_language(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), customer_language="ja")
    resp = client.put(
        f"/api/bids/{bid_id}/schedule",
        json={
            "start_date": "2026-11-01",
            "buffer_days": 0,
            "team_allocation": default_team_allocation(),
            "by": "ai_developer",
        },
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["working_calendar"] == "jp"


def test_put_schedule_writes_changelog(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    put_schedule(client, bid_id)
    session = db.SessionLocal()
    try:
        rows = session.query(Changelog).filter_by(bid_id=bid_id, action="edit_schedule").all()
        assert rows
        assert rows[-1].actor == "ai_developer"
    finally:
        session.close()


def test_locked_bid_returns_409(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    session = db.SessionLocal()
    try:
        bid = session.get(Bid, bid_id)
        assert bid is not None
        bid.locked = True
        session.commit()
    finally:
        session.close()

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
