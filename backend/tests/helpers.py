"""Helpers dùng chung cho test backend M2."""

from __future__ import annotations

import json
import time

VALID_PAYLOAD = {
    "project_name": "Hệ thống CRM khách hàng ABC",
    "customer_name": "Công ty XYZ (giả lập)",
    "submission_deadline": "2026-12-15",
    "customer_language": "ja",
    "request_content": (
        "Yêu cầu xây dựng hệ thống CRM quản lý khách hàng, tích hợp dữ liệu "
        "hiện có, giao diện tiếng Nhật, phục vụ bộ phận kinh doanh và CSKH."
    ),
    "budget_amount": 50000000,
    "budget_currency": "JPY",
}

# Request trung tính → factor_product = 1.0 (số dễ kiểm soát trong test M4).
NEUTRAL_REQUEST = (
    "Xây dựng hệ thống nội bộ cho khách hàng, phạm vi cơ bản, "
    "không phát sinh đặc biệt."
)


def wait_until(predicate, timeout: float = 10.0, interval: float = 0.05) -> bool:
    """Poll tới khi predicate() True — dùng chờ pipeline chạy nền (asyncio task).

    Timeout mặc định 10s: môi trường chạy nhiều agent song song có thể làm
    pipeline chậm hơn bình thường (CPU contention).
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


def create_bid(client, **overrides) -> int:
    """Tạo hồ sơ qua API, trả về id."""
    payload = {**VALID_PAYLOAD, **overrides}
    resp = client.post("/api/bids", json=payload, headers={"X-User": "Nhu"})
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def bid_status(client, bid_id: int) -> str:
    resp = client.get(f"/api/bids/{bid_id}")
    assert resp.status_code == 200, resp.text
    return resp.json()["status"]


def step_status(client, bid_id: int, step: str) -> str:
    resp = client.get(f"/api/bids/{bid_id}")
    assert resp.status_code == 200, resp.text
    for s in resp.json()["pipeline_progress"]["steps"]:
        if s["step_key"] == step:
            return s["status"]
    raise AssertionError(f"Không thấy bước {step}")


# ---------------------------------------------------------------- M4 helpers

def setup_wbs_bid(
    client,
    session,
    *,
    direction: str = "rag",
    customer_language: str = "vi",
    submission_deadline: str = "2026-12-15",
    fixture_mode: str = "good",
) -> int:
    """Tạo bid + chọn hướng + persist WBS (fixture mock, man-day do code gán).

    Factor mặc định = 1.0 (vi + request trung tính) → midpoint rag = 48.
    Trả về bid_id.
    """
    from app.models import Bid
    from app.schemas.llm_schemas.wbs_structure import WbsStructure
    from app.services import wbs_engine
    from app.services.effort_engine import calculate_effort
    from app.services.wbs_service import persist_wbs_items
    from app.llm.mock_client import get_fixture

    bid_id = create_bid(
        client,
        customer_language=customer_language,
        submission_deadline=submission_deadline,
        request_content=NEUTRAL_REQUEST,
    )
    resp = client.post(
        f"/api/bids/{bid_id}/solution",
        json={"direction": direction, "reason_vi": "Lý do giả lập", "by": "ai_developer"},
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 200, resp.text

    raw = get_fixture(WbsStructure, fixture_mode)
    tasks = WbsStructure.model_validate(raw).model_dump(mode="json")["tasks"]
    bid = session.get(Bid, bid_id)
    effort = calculate_effort(bid, direction)
    tasks = wbs_engine.assign_man_days(tasks, effort["by_phase"])
    persist_wbs_items(session, bid_id, tasks, by="test")
    session.commit()
    return bid_id


def default_team_allocation() -> dict:
    return {
        "pm": 1, "ba": 1, "brse": 1, "ai_engineer": 1,
        "backend": 2, "frontend": 1, "qa": 1, "infra": 1,
    }


def put_schedule(client, bid_id: int, **overrides) -> dict:
    """PUT /schedule với tham số mặc định (start 2026-11-01, vn, đủ headcount)."""
    payload = {
        "start_date": "2026-11-01",
        "buffer_days": 0,
        "working_calendar": "vn",
        "team_allocation": default_team_allocation(),
        "by": "ai_developer",
    }
    payload.update(overrides)
    resp = client.put(
        f"/api/bids/{bid_id}/schedule",
        json=payload,
        headers={"X-User": "ai_developer", "X-Role": "ai_developer"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()