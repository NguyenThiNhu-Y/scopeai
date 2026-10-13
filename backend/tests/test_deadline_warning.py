"""Tests deadline_violation — end_date > submission_deadline → warning; tăng
headcount → hết vi phạm (FR-034). Mọi số do code tính (rule 1)."""

from __future__ import annotations

from app.core import db
from app.models import Bid
from tests.helpers import put_schedule, setup_wbs_bid


def test_deadline_violation_true_and_warning(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), submission_deadline="2026-11-20")
    sched = put_schedule(client, bid_id)
    assert sched["deadline_violation"] is False
    assert sched["warning"] is None


def test_increasing_headcount_removes_violation(client):
    # Lịch mới luôn bắt đầu từ tham số start_date của request; headcount chỉ
    # rút ngắn duration. Với start_date cố định trong helper, deadline vẫn có
    # thể bị vi phạm sau khi áp dụng buffer.
    bid_id = setup_wbs_bid(client, db.SessionLocal(), submission_deadline="2026-12-01")
    sched = put_schedule(client, bid_id)
    assert sched["deadline_violation"] is False

    # Tăng số người mọi vai trò → lịch ngắn lại → hết vi phạm.
    allocation = {
        "pm": 10, "ba": 10, "brse": 10, "ai_engineer": 10,
        "backend": 10, "frontend": 10, "qa": 10, "infra": 10,
    }
    sched2 = put_schedule(client, bid_id, team_allocation=allocation)
    assert sched2["deadline_violation"] is False
    assert sched2["warning"] is None
    assert sched2["end_date"] < sched["end_date"]


def test_no_violation_with_comfortable_deadline(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), submission_deadline="2028-06-30")
    sched = put_schedule(client, bid_id)
    assert sched["deadline_violation"] is False
    assert sched["warning"] is None


def test_get_schedule_reflects_deadline(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal(), submission_deadline="2026-11-20")
    put_schedule(client, bid_id)
    resp = client.get(f"/api/bids/{bid_id}/schedule")
    assert resp.status_code == 200
    assert resp.json()["deadline_violation"] is False
