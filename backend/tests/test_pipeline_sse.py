"""Tests cho SSE tiến độ pipeline — FR-023/NFR-001 (contract §5.2, BR-09).

Lưu ý môi trường: TestClient (starlette+httpx) và httpx.ASGITransport đều BUFFER
toàn bộ response body nên không thể stream SSE qua HTTP trong test. Các test này
kiểm tra trực tiếp ``SSEManager`` + orchestrator + endpoint wiring trên cùng một
event loop — phủ đúng logic SSE (replay, event order, heartbeat, cleanup).
"""

from __future__ import annotations

import asyncio
import json
import time

from fastapi.responses import StreamingResponse

from app.core import db
from app.llm.mock_client import MockLLMClient
from app.models import Bid
from app.pipeline.orchestrator import orchestrator
from app.pipeline.sse import sse_manager
from app.schemas.api_schemas.bid import BidCreate
from app.services import bid_service
from tests.helpers import VALID_PAYLOAD


class SlowMockClient(MockLLMClient):
    """Client chậm — đủ thời gian quan sát từng sự kiện step."""

    def __init__(self, delay: float = 0.2, **kwargs):
        super().__init__(**kwargs)
        self.delay = delay

    def complete(self, **kwargs):
        time.sleep(self.delay)
        return super().complete(**kwargs)


def _create_bid_sync() -> int:
    session = db.SessionLocal()
    try:
        bid = bid_service.create_bid(
            session, BidCreate(**VALID_PAYLOAD), created_by="Nhu"
        )
        return bid.id
    finally:
        session.close()


def _parse_sse(message: str) -> tuple[str, dict | None]:
    event = ""
    data = None
    for line in message.splitlines():
        if line.startswith("event: "):
            event = line[len("event: ") :]
        elif line.startswith("data: "):
            data = json.loads(line[len("data: ") :])
    return event, data


async def _collect(subscription, target: set[str], max_events: int | None = None, timeout: float = 6.0):
    events: list[tuple[str, dict | None]] = []
    deadline = time.time() + timeout
    try:
        async for message in subscription:
            parsed = _parse_sse(message)
            events.append(parsed)
            if parsed[0] in target:
                break
            if max_events and len(events) >= max_events:
                break
            if time.time() > deadline:
                break
    finally:
        await subscription.aclose()
    return events


def test_sse_endpoint_wiring():
    """Endpoint trả StreamingResponse media_type text/event-stream (contract §5.2)."""

    async def scenario():
        bid_id = _create_bid_sync()
        from app.api.routers.pipeline import pipeline_events

        response = await pipeline_events(bid_id)
        assert isinstance(response, StreamingResponse)
        assert response.media_type == "text/event-stream"

    asyncio.run(scenario())


def test_sse_event_order(mock_llm):
    """Thứ tự sự kiện: intake:running → completed → gap:running → clarify/done."""

    async def scenario():
        mock_llm["client"] = SlowMockClient(delay=0.2)
        bid_id = _create_bid_sync()

        session = db.SessionLocal()
        try:
            orchestrator.start(session, bid_id)
        finally:
            session.close()

        events = await _collect(sse_manager.subscribe(bid_id), {"clarify", "done"})

        steps = [(d["step"], d["status"]) for e, d in events if e == "step" and d]
        seq = [f"{s}:{st}" for s, st in steps]

        assert "intake:running" in seq
        assert "intake:completed" in seq
        assert "gap:running" in seq
        assert (
            seq.index("intake:running")
            < seq.index("intake:completed")
            < seq.index("gap:running")
        )
        terminal = [e for e, _ in events if e in ("clarify", "done")]
        assert terminal, "Thiếu sự kiện clarify/done"

    asyncio.run(scenario())


def test_sse_done_event_when_no_clarification(mock_llm):
    """needs_clarification=false → sự kiện done với status waiting_tech_approval."""

    async def scenario():
        mock_llm["client"] = SlowMockClient(
            delay=0.1, fixture_modes={"GapQuestions": "no_questions"}
        )
        bid_id = _create_bid_sync()

        session = db.SessionLocal()
        try:
            orchestrator.start(session, bid_id)
        finally:
            session.close()

        events = await _collect(sse_manager.subscribe(bid_id), {"done"})
        done = [d for e, d in events if e == "done" and d]
        assert done
        assert done[0]["status"] == "waiting_tech_approval"
        assert done[0]["bid_id"] == bid_id

    asyncio.run(scenario())


def test_sse_clarify_event_contains_questions(mock_llm):
    """needs_clarification=true → sự kiện clarify kèm câu hỏi (id, question, reason_vi, impact)."""

    async def scenario():
        mock_llm["client"] = SlowMockClient(delay=0.1)
        bid_id = _create_bid_sync()

        session = db.SessionLocal()
        try:
            orchestrator.start(session, bid_id)
        finally:
            session.close()

        events = await _collect(sse_manager.subscribe(bid_id), {"clarify"})
        clarify = [d for e, d in events if e == "clarify" and d]
        assert clarify
        data = clarify[0]
        assert data["bid_id"] == bid_id
        assert data["round"] == 1
        assert data["questions"]
        first = data["questions"][0]
        assert {"id", "question", "reason_vi", "impact", "related_req_codes"} <= set(first)

    asyncio.run(scenario())


def test_sse_heartbeat():
    """Server gửi event heartbeat định kỳ (mặc định 15s — test rút ngắn)."""

    async def scenario():
        bid_id = _create_bid_sync()
        old_interval = sse_manager.heartbeat_interval
        sse_manager.heartbeat_interval = 0.2
        try:
            events = await _collect(sse_manager.subscribe(bid_id), {"heartbeat"})
            assert any(e == "heartbeat" for e, _ in events)
        finally:
            sse_manager.heartbeat_interval = old_interval

    asyncio.run(scenario())


def test_sse_stream_auto_closes_after_done(mock_llm):
    """Luồng TỰ ĐÓNG sau sự kiện done — không cần aclose thủ công, không heartbeat vô hạn."""

    async def scenario():
        mock_llm["client"] = MockLLMClient(fixture_modes={"GapQuestions": "no_questions"})
        bid_id = _create_bid_sync()

        session = db.SessionLocal()
        try:
            orchestrator.start(session, bid_id)
        finally:
            session.close()

        events: list[tuple[str, dict | None]] = []
        async for message in sse_manager.subscribe(bid_id):
            events.append(_parse_sse(message))

        # Nếu luồng không tự đóng, async-for sẽ chờ heartbeat vô hạn → pytest-timeout.
        assert any(e == "done" for e, _ in events)
        assert any(e == "heartbeat" for e, _ in events) is False

    asyncio.run(scenario())


def test_sse_stream_auto_closes_after_clarify(mock_llm):
    """Luồng TỰ ĐÓNG sau sự kiện clarify (pipeline dừng ở waiting_clarification)."""

    async def scenario():
        mock_llm["client"] = SlowMockClient(delay=0.1)
        bid_id = _create_bid_sync()

        session = db.SessionLocal()
        try:
            orchestrator.start(session, bid_id)
        finally:
            session.close()

        events: list[tuple[str, dict | None]] = []
        async for message in sse_manager.subscribe(bid_id):
            events.append(_parse_sse(message))

        assert any(e == "clarify" for e, _ in events)

    asyncio.run(scenario())


def test_sse_stream_auto_closes_after_error(mock_llm):
    """Luồng TỰ ĐÓNG sau sự kiện error (bước failed)."""

    async def scenario():
        mock_llm["client"] = MockLLMClient(fixture_modes={"GapQuestions": "bad_schema"})
        bid_id = _create_bid_sync()

        session = db.SessionLocal()
        try:
            orchestrator.start(session, bid_id)
        finally:
            session.close()

        events: list[tuple[str, dict | None]] = []
        async for message in sse_manager.subscribe(bid_id):
            events.append(_parse_sse(message))

        assert any(e == "error" for e, _ in events)

    asyncio.run(scenario())


def test_sse_reconnect_replays_current_state(mock_llm):
    """Reconnect: replay trạng thái hiện tại của các bước pipeline."""

    async def scenario():
        mock_llm["client"] = MockLLMClient(fixture_modes={"GapQuestions": "no_questions"})
        bid_id = _create_bid_sync()

        session = db.SessionLocal()
        try:
            orchestrator.start(session, bid_id)
        finally:
            session.close()

        # Chờ pipeline xong.
        for _ in range(100):
            session = db.SessionLocal()
            try:
                bid = session.get(Bid, bid_id)
                done = bid is not None and bid.status == "waiting_tech_approval"
            finally:
                session.close()
            if done:
                break
            await asyncio.sleep(0.05)
        else:
            raise AssertionError("Pipeline không hoàn tất")

        events: list[tuple[str, dict | None]] = []
        async for message in sse_manager.subscribe(bid_id):
            events.append(_parse_sse(message))
        step_events = [(e, d) for e, d in events if e == "step" and d]
        assert len(step_events) == 6
        by_step = {d["step"]: d["status"] for _, d in step_events}
        assert by_step["intake"] == "completed"
        assert by_step["gap"] == "completed"
        # B6 proposal chạy sau WBS; ja_check không phải bước thật nên không phát event.
        assert by_step["solution"] == "completed"
        assert by_step["wbs"] == "completed"
        assert by_step["proposal"] == "completed"
        # Hồ sơ đã ở trạng thái cuối → luồng đóng ngay sau replay (không heartbeat).
        assert any(e == "heartbeat" for e, _ in events) is False

    asyncio.run(scenario())
