"""Tests PUT /wbs — sửa WBS → tổng + lịch tính lại, KHÔNG gọi AI (FR-041.1).

AGENTS.md rule 3: PUT /wbs không gọi LLM — assert mock.call_count không tăng.
Rule 4: override ngoài ±20% thiếu note → 400 (BR-12).
"""

from __future__ import annotations

from app.core import db
from app.llm.mock_client import MockLLMClient
from app.models import Changelog
from tests.helpers import put_schedule, setup_wbs_bid


def _put_wbs(client, bid_id: int, changes: list, note: str | None = None):
    body = {"changes": changes, "by": "ai_developer"}
    if note is not None:
        body["note"] = note
    return client.put(
        f"/api/bids/{bid_id}/wbs",
        json=body,
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )


def test_add_leaf_recalcs_total_and_schedule_without_llm(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    before = client.get(f"/api/bids/{bid_id}/wbs").json()
    total_before = before["totals"]["man_day"]
    put_schedule(client, bid_id)
    end_before = client.get(f"/api/bids/{bid_id}/schedule").json()["end_date"]

    llm = MockLLMClient()
    calls_before = llm.call_count

    # Đợt 14 (C2): mock WBS nghiêng về backend (nút thắt lịch) — thêm task
    # BACKEND 5 man-day để end_date thực sự trễ hơn (task QA có dư năng lực).
    resp = _put_wbs(client, bid_id, [
        {"op": "add", "task": {
            "task_code": "WBS-002-01-05", "name_vi": "Task thêm 5 man-day",
            "phase": "mvp", "parent_code": "WBS-002-01",
            "role": "backend", "man_day": 5.0, "depends_on": []}},
    ])
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["totals"]["man_day"] == round(total_before + 5.0, 1)
    assert body["recalculated"]["schedule"] is not None
    assert body["recalculated"]["quotation"] is None  # M5 bổ sung

    # Lịch đổi (nhiều việc hơn → end_date trễ hơn) và KHÔNG gọi AI.
    sched = client.get(f"/api/bids/{bid_id}/schedule").json()
    assert sched["end_date"] > end_before
    assert llm.call_count == calls_before  # không tăng


def test_remove_subtree_decreases_total_and_cleans_depends_on(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    before = client.get(f"/api/bids/{bid_id}/wbs").json()
    total_before = before["totals"]["man_day"]
    # Xóa nhóm WBS-001 (PoC) → toàn bộ sub-tree biến mất; thiếu PM/QA phase poc
    # → bắt buộc note override (BR-12).
    resp = _put_wbs(client, bid_id, [
        {"op": "remove", "task_code": "WBS-001"},
    ], note="Khách cắt phạm vi PoC")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    codes = {i["task_code"] for i in body["items"]}
    assert not any(c.startswith("WBS-001") for c in codes)
    assert body["totals"]["man_day"] < total_before

    # depends_on trỏ tới item đã xóa phải được dọn.
    for item in body["items"]:
        assert not any(d.startswith("WBS-001") for d in item["depends_on"])


def test_update_man_day_recalcs_and_writes_changelog_from_header(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    put_schedule(client, bid_id)
    before = client.get(f"/api/bids/{bid_id}/wbs").json()
    old_md = next(i for i in before["items"] if i["task_code"] == "WBS-001-01-01")["man_day"]

    resp = _put_wbs(client, bid_id, [
        {"op": "update", "task_code": "WBS-001-01-01", "fields": {"man_day": 5.0}},
    ])
    assert resp.status_code == 200, resp.text
    body = resp.json()
    new_md = next(i for i in body["items"] if i["task_code"] == "WBS-001-01-01")["man_day"]
    assert new_md == 5.0
    assert body["totals"]["man_day"] == round(before["totals"]["man_day"] - old_md + 5.0, 1)

    # Changelog ghi actor từ header X-User (M3-REV-001), action edit_wbs.
    session = db.SessionLocal()
    try:
        rows = session.query(Changelog).filter_by(bid_id=bid_id, action="edit_wbs").all()
        assert rows
        assert rows[-1].actor == "ai_developer"
    finally:
        session.close()


def test_override_outside_20pct_requires_note(client):
    """Thêm 20 man-day → tổng lệch > 20% so midpoint 90 → thiếu note → 400."""
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    before = client.get(f"/api/bids/{bid_id}/wbs").json()
    assert before["check"]["within_20pct"] is True

    resp = _put_wbs(client, bid_id, [
        {"op": "add", "task": {
            "task_code": "WBS-002-01-05", "name_vi": "Task nặng",
            "phase": "mvp", "parent_code": "WBS-002-01",
            "role": "qa", "man_day": 10.0, "depends_on": []}},
        {"op": "add", "task": {
            "task_code": "WBS-002-01-06", "name_vi": "Task nặng khác",
            "phase": "mvp", "parent_code": "WBS-002-01",
            "role": "qa", "man_day": 10.0, "depends_on": []}},
    ])
    assert resp.status_code == 200, resp.text
    body = resp.json()
    # Đợt 14 (C2): mock WBS đã tách task để mọi lá ≤ 10 man-day — thêm task
    # 10.0 man-day không còn làm lá vượt ngưỡng (trước đây fixture cũ có lá 20+).
    assert body["check"]["leaf_within_limit"] is True

    # Có note → chấp nhận (override BR-12).
    resp = _put_wbs(client, bid_id, [
        {"op": "update", "task_code": "WBS-002-01-05", "fields": {"man_day": 12.0}},
        {"op": "update", "task_code": "WBS-002-01-06", "fields": {"man_day": 12.0}},
    ], note="Khách yêu cầu thêm QA kiểm thử chuyên sâu")
    assert resp.status_code == 200, resp.text
    assert resp.json()["check"]["within_20pct"] is True


def test_leaf_man_day_over_10_rejected(client):
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    resp = _put_wbs(client, bid_id, [
        {"op": "add", "task": {
            "task_code": "WBS-002-01-05", "name_vi": "Quá nặng",
            "phase": "mvp", "parent_code": "WBS-002-01",
            "role": "qa", "man_day": 11.0, "depends_on": []}},
    ])
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_cycle_edit_rejected(client):
    """Tạo phụ thuộc vòng qua PUT /wbs → 400 VALIDATION_ERROR (message Việt)."""
    bid_id = setup_wbs_bid(client, db.SessionLocal())
    resp = _put_wbs(client, bid_id, [
        {"op": "update", "task_code": "WBS-002-01-04", "fields": {"depends_on": ["WBS-002-01-02"]}},
        {"op": "update", "task_code": "WBS-002-01-02", "fields": {"depends_on": ["WBS-002-01-04"]}},
    ])
    assert resp.status_code == 400
    body = resp.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    assert "vòng" in body["message"].lower()
