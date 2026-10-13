"""Tests snapshot WBS + diff_summary (FR-041.2, contract §8.3) và rerun từ wbs.

Rerun từ bước wbs: tự snapshot WBS cũ, giữ evaluate/solution completed.
"""

from __future__ import annotations

from app.core import db
from app.llm.mock_client import MockLLMClient
from app.models import PipelineStep, WbsSnapshot
from tests.helpers import (
    bid_status,
    create_bid,
    put_schedule,
    setup_wbs_bid,
    step_status,
    wait_until,
)


def _snapshot(client, bid_id: int, reason: str = "Chụp để đối chiếu") -> dict:
    resp = client.post(
        f"/api/bids/{bid_id}/wbs/snapshot",
        json={"reason": reason, "by": "ai_developer"},
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_first_snapshot_has_null_diff(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    snap = _snapshot(client, bid_id)
    assert snap["snapshot_id"] >= 1
    assert snap["diff_summary"] is None


def test_snapshot_diff_shows_added_removed_modified(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    _snapshot(client, bid_id, "Trạng thái ban đầu")

    # Sửa WBS: thêm lá, xóa 1 lá, đổi man_day 1 lá.
    resp = client.put(
        f"/api/bids/{bid_id}/wbs",
        json={
            "changes": [
                {"op": "add", "task": {
                    "task_code": "WBS-002-01-05", "name_vi": "Task mới",
                    "phase": "mvp", "parent_code": "WBS-002-01",
                    "role": "qa", "man_day": 3.0, "depends_on": []}},
                {"op": "remove", "task_code": "WBS-001-02-04"},
                {"op": "update", "task_code": "WBS-001-01-01", "fields": {"man_day": 5.0}},
            ],
            "by": "ai_developer",
            "note": "Sửa để test diff",
        },
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 200, resp.text

    snap = _snapshot(client, bid_id, "Sau khi sửa")
    diff = snap["diff_summary"]
    assert diff is not None
    assert "WBS-002-01-05" in diff["added"]
    assert "WBS-001-02-04" in diff["removed"]
    modified = {m["task_code"]: m for m in diff["modified"]}
    assert "WBS-001-01-01" in modified
    assert modified["WBS-001-01-01"]["field"] == "man_day"
    assert modified["WBS-001-01-01"]["new"] == 5.0
    assert modified["WBS-001-01-01"]["old"] != 5.0


def test_snapshot_diff_includes_parent_and_depends_on(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    _snapshot(client, bid_id, "Ban đầu")

    resp = client.put(
        f"/api/bids/{bid_id}/wbs",
        json={
            "changes": [
                {"op": "update", "task_code": "WBS-002-01-04",
                 "fields": {"depends_on": ["WBS-002-01-01"]}},
            ],
            "by": "ai_developer",
            "note": "Đổi phụ thuộc",
        },
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 200, resp.text

    snap = _snapshot(client, bid_id, "Sau khi đổi depends_on")
    diff = snap["diff_summary"]
    modified = {m["task_code"]: m for m in diff["modified"]}
    assert "WBS-002-01-04" in modified
    fields = {m["field"] for m in diff["modified"] if m["task_code"] == "WBS-002-01-04"}
    assert "depends_on" in fields


def test_rerun_from_wbs_snapshots_and_keeps_evaluate_solution(client, mock_llm):
    """Rerun from_step=wbs: snapshot WBS cũ, giữ evaluate/solution, tạo WBS mới."""
    mock_llm["client"] = MockLLMClient(fixture_modes={"GapQuestions": "no_questions"})
    bid_id = create_bid(client)
    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")
    assert step_status(client, bid_id, "wbs") == "completed"

    llm = mock_llm["client"]
    solution_calls = llm.call_counts.get("SolutionProposal", 0)
    wbs_calls_before = llm.call_counts.get("WbsStructure", 0)
    assert solution_calls == 1

    # Tạo lịch trước khi rerun → bị xóa (dữ liệu cũ).
    put_schedule(client, bid_id)

    resp = client.post(
        f"/api/bids/{bid_id}/rerun",
        json={"from_step": "wbs", "reason": "Góp ý: tách task infra", "by": "ai_developer"},
    )
    assert resp.status_code == 202, resp.text
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")

    # Giữ solution (không chạy lại); evaluate chưa triển khai ở M4 → giữ pending;
    # wbs chạy lại lần 2.
    assert step_status(client, bid_id, "evaluate") == "pending"
    assert step_status(client, bid_id, "solution") == "completed"
    assert step_status(client, bid_id, "wbs") == "completed"
    assert llm.call_counts.get("SolutionProposal", 0) == solution_calls
    assert llm.call_counts.get("WbsStructure", 0) == wbs_calls_before + 1

    session = db.SessionLocal()
    try:
        snaps = session.query(WbsSnapshot).filter_by(bid_id=bid_id).all()
        assert len(snaps) >= 1  # auto-snapshot WBS cũ (FR-041.2)
        step = session.query(PipelineStep).filter_by(bid_id=bid_id, step_key="wbs").one()
        assert step.attempts == 2
        # D2-05: WBS tự tạo lại master schedule mặc định.
    finally:
        session.close()

    resp = client.get(f"/api/bids/{bid_id}/schedule")
    assert resp.status_code == 200
    assert resp.json()["tasks"]


def test_snapshot_requires_existing_wbs(client):
    from tests.helpers import create_bid

    bid_id = create_bid(client)
    resp = client.post(
        f"/api/bids/{bid_id}/wbs/snapshot",
        json={"reason": "Không có WBS"},
        headers={"X-User": "ai_developer"},
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "STATE_CONFLICT"
