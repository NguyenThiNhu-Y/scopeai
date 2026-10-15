"""Test truy vết requirement → WBS (thiet_ke_danh_gia.md §4).

- Mock B5 gán requirement_codes cho task lá theo category (FR → backend/frontend,
  NFR → infra/qa, vòng tròn); KHÔNG gán requirement "cần làm rõ".
- Pipeline B5 bỏ mã không tồn tại và lưu requirement_codes vào wbs_items.
- WbsTaskIn / PUT /wbs sửa được requirement_codes (chỉ task lá, tối đa 8).
- test_llm_schema_no_numbers vẫn pass (requirement_codes không phải con số).
"""

from __future__ import annotations

from app.core import db
from app.llm.mock_client import MockLLMClient, _content_fixture
from app.models import Requirement, WbsItem
from tests.helpers import bid_status, create_bid, setup_wbs_bid, step_status, wait_until


def _ja_requirements() -> list[dict]:
    """36 requirement giống mẫu ja_email: FR-001..FR-027, NFR-001..NFR-009.

    FR-019/FR-020 nói về tích hợp hệ thống ngoài chưa xác định giao diện
    (会計システム / 販売管理システム) → mock coi là "cần làm rõ".
    """
    requirements = []
    for index in range(1, 28):
        content = f"Yêu cầu chức năng {index} (giả lập)"
        if index == 19:
            content = "会計システムへ連携するためのインタフェースを提供できること。"
        if index == 20:
            content = "販売管理システムから商品・受注情報を取り込めること。"
        requirements.append(
            {"req_code": f"FR-{index:03d}", "content": content, "category": "functional"}
        )
    for index in range(1, 10):
        requirements.append(
            {
                "req_code": f"NFR-{index:03d}",
                "content": f"Yêu cầu phi chức năng {index} (giả lập)",
                "category": "non-functional",
            }
        )
    return requirements


# ---------------------------------------------------------------- mock B5

def test_mock_b5_assigns_codes_by_category_and_skips_unclear():
    result = _content_fixture(
        "WbsStructure",
        {"direction": "rag", "requirements_data": _ja_requirements()},
    )
    assigned: set[str] = set()
    for task in result["tasks"]:
        codes = task.get("requirement_codes") or []
        assert len(codes) <= 8
        if task.get("role") is None:
            # Task nhóm không được truy vết requirement.
            assert not codes
            continue
        for code in codes:
            assigned.add(code)
            if code.startswith("FR"):
                assert task["role"] in ("backend", "frontend")
            else:
                assert task["role"] in ("infra", "qa")
    assert len(assigned) == 34
    uncovered = [r["req_code"] for r in _ja_requirements() if r["req_code"] not in assigned]
    assert set(uncovered) == {"FR-019", "FR-020"}


def test_mock_b5_does_not_assign_unclear_flagged_requirement():
    requirements = [
        {"req_code": "FR-001", "content": "Chức năng bình thường", "category": "functional"},
        {"req_code": "FR-002", "content": "Yêu cầu đang 要相談", "category": "functional"},
        {"req_code": "NFR-001", "content": "Hạ tầng chuẩn", "category": "non-functional"},
    ]
    result = _content_fixture(
        "WbsStructure",
        {"direction": "rag", "requirements_data": requirements},
    )
    assigned = {
        code
        for task in result["tasks"]
        for code in (task.get("requirement_codes") or [])
    }
    assert "FR-001" in assigned
    assert "FR-002" not in assigned
    assert "NFR-001" in assigned


# ---------------------------------------------------------------- pipeline B5

def test_pipeline_persists_requirement_codes(client, mock_llm):
    mock_llm["client"] = MockLLMClient(fixture_modes={"GapQuestions": "no_questions"})
    bid_id = create_bid(client, customer_language="ja")
    session = db.SessionLocal()
    try:
        for req in _ja_requirements():
            session.add(
                Requirement(
                    bid_id=bid_id,
                    internal_code=req["req_code"],
                    content=req["content"],
                    priority="Must",
                    category=req["category"],
                    source_sheet="CSV",
                    source_row=2,
                )
            )
        session.commit()
    finally:
        session.close()

    resp = client.post(
        f"/api/bids/{bid_id}/solution",
        json={"direction": "rag", "reason_vi": "Lý do giả lập", "by": "ai_developer"},
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 200

    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")
    assert step_status(client, bid_id, "wbs") == "completed"

    session = db.SessionLocal()
    try:
        items = session.query(WbsItem).filter_by(bid_id=bid_id).all()
        assert items
        assigned: set[str] = set()
        for item in items:
            if item.requirement_codes:
                assert item.role is not None  # chỉ task lá
                assigned.update(item.requirement_codes)
        assert len(assigned) == 34
        assert "FR-019" not in assigned
        assert "FR-020" not in assigned
    finally:
        session.close()


def test_pipeline_drops_nonexistent_requirement_codes(client, mock_llm):
    """B5 bỏ mã không tồn tại (LLM bịa mã) và ghi chú vào notes_vi."""
    mock_llm["client"] = MockLLMClient(fixture_modes={"GapQuestions": "no_questions"})
    bid_id = create_bid(client, customer_language="ja")
    session = db.SessionLocal()
    try:
        session.add(
            Requirement(
                bid_id=bid_id,
                internal_code="FR-001",
                content="Yêu cầu giả lập",
                priority="Must",
                category="functional",
                source_sheet="CSV",
                source_row=2,
            )
        )
        session.commit()
    finally:
        session.close()

    resp = client.post(
        f"/api/bids/{bid_id}/solution",
        json={"direction": "rag", "reason_vi": "Lý do giả lập", "by": "ai_developer"},
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 200
    resp = client.post(f"/api/bids/{bid_id}/pipeline/start")
    assert resp.status_code == 202
    assert wait_until(lambda: bid_status(client, bid_id) == "waiting_tech_approval")

    session = db.SessionLocal()
    try:
        items = session.query(WbsItem).filter_by(bid_id=bid_id).all()
        assigned = {
            code
            for item in items
            for code in (item.requirement_codes or [])
        }
        assert assigned <= {"FR-001"}
        # Mã không tồn tại không được lưu.
        assert not any(code.startswith("XX-") for code in assigned)
    finally:
        session.close()


# ---------------------------------------------------------------- sửa tay

def test_wbs_edit_updates_requirement_codes(client):
    session = db.SessionLocal()
    try:
        bid_id = setup_wbs_bid(client, session, direction="rag")
    finally:
        session.close()
    resp = client.put(
        f"/api/bids/{bid_id}/wbs",
        json={
            "changes": [
                {
                    "op": "update",
                    "task_code": "WBS-001-01-01",
                    "fields": {"requirement_codes": ["FR-001", "NFR-002"]},
                }
            ],
            "by": "tester",
            "note": "Gán requirement cho task",
        },
        headers={"X-User": "tester", "X-Role": "presales"},
    )
    assert resp.status_code == 200, resp.text
    items = {item["task_code"]: item for item in resp.json()["items"]}
    assert items["WBS-001-01-01"]["requirement_codes"] == ["FR-001", "NFR-002"]


def test_wbs_edit_rejects_requirement_codes_on_group_task(client):
    session = db.SessionLocal()
    try:
        bid_id = setup_wbs_bid(client, session, direction="rag")
    finally:
        session.close()
    resp = client.put(
        f"/api/bids/{bid_id}/wbs",
        json={
            "changes": [
                {
                    "op": "update",
                    "task_code": "WBS-001",
                    "fields": {"requirement_codes": ["FR-001"]},
                }
            ],
            "by": "tester",
            "note": "test",
        },
        headers={"X-User": "tester", "X-Role": "presales"},
    )
    assert resp.status_code == 400
    assert "requirement_codes" in resp.json()["error"]["message"]


def test_wbs_add_task_with_requirement_codes(client):
    session = db.SessionLocal()
    try:
        bid_id = setup_wbs_bid(client, session, direction="rag")
    finally:
        session.close()
    resp = client.put(
        f"/api/bids/{bid_id}/wbs",
        json={
            "changes": [
                {
                    "op": "add",
                    "task": {
                        "task_code": "WBS-001-01-99",
                        "name_vi": "Task test truy vết",
                        "phase": "poc",
                        "parent_code": "WBS-001-01",
                        "role": "backend",
                        "man_day": 5,
                        "requirement_codes": ["FR-002"],
                    },
                }
            ],
            "by": "tester",
            "note": "test",
        },
        headers={"X-User": "tester", "X-Role": "presales"},
    )
    assert resp.status_code == 200, resp.text
    items = {item["task_code"]: item for item in resp.json()["items"]}
    assert items["WBS-001-01-99"]["requirement_codes"] == ["FR-002"]