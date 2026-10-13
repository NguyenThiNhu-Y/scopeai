"""SSE in-process — asyncio pub/sub, không WebSocket/broker (BR-09).

- ``subscribe(bid_id)``: async generator — replay trạng thái hiện tại từ
  ``pipeline_steps`` rồi stream sự kiện live; heartbeat mỗi 15s; xóa subscriber
  khi disconnect.
- ``publish(bid_id, event, data)``: đẩy sự kiện tới mọi subscriber của bid.
- **Auto-close (FR-023/NFR-001):** luồng TỰ ĐÓNG sau sự kiện cuối — ``done``,
  ``clarify`` (pipeline dừng ở waiting_clarification) hoặc ``error`` (bước lỗi).
  Khi reconnect tới một hồ sơ đã ở trạng thái cuối, luồng đóng ngay sau replay.
  Điều này ngăn client/test giữ kết nối vô hạn chờ sự kiện không bao giờ tới.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from collections import defaultdict
from typing import Any, AsyncIterator

from app.core import db
from app.models import PipelineStep

logger = logging.getLogger(__name__)

_DEFAULT_HEARTBEAT_S = float(os.getenv("SSE_HEARTBEAT_SECONDS", "15"))

# Sự kiện cuối: sau khi phát, không còn sự kiện nào nữa → đóng luồng.
_TERMINAL_EVENTS = frozenset({"done", "clarify", "error"})


def _format_sse(event: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


def _event_name(message: str) -> str | None:
    """Tên event từ một message SSE đã format (None nếu không có dòng event)."""
    for line in message.splitlines():
        if line.startswith("event: "):
            return line[len("event: ") :]
    return None


class SSEManager:
    """Quản lý subscriber theo bid_id — mỗi subscriber một asyncio.Queue."""

    def __init__(self, heartbeat_interval: float = _DEFAULT_HEARTBEAT_S) -> None:
        self.heartbeat_interval = heartbeat_interval
        self._subscribers: dict[int, set[asyncio.Queue]] = defaultdict(set)

    def publish(self, bid_id: int, event: str, data: dict[str, Any]) -> None:
        """Đẩy sự kiện tới mọi subscriber của bid (drop nếu queue đầy)."""
        message = _format_sse(event, data)
        for queue in list(self._subscribers.get(bid_id, ())):
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                logger.warning("Subscriber của bid %s chậm — bỏ qua sự kiện", bid_id)

    def _replay(self, bid_id: int) -> tuple[list[str], bool]:
        """Replay trạng thái hiện tại của các bước pipeline (khi mới connect).

        Returns:
            (messages, terminal) — ``terminal=True`` nếu hồ sơ đã ở trạng thái
            cuối (bước failed / gap waiting_clarification / intake+gap completed)
            → subscriber nên đóng luồng ngay sau replay.
        """
        messages: list[str] = []
        terminal = False
        try:
            session = db.SessionLocal()
            try:
                steps = (
                    session.query(PipelineStep)
                    .filter(PipelineStep.bid_id == bid_id)
                    .order_by(PipelineStep.id)
                    .all()
                )
                status_by_key: dict[str, str] = {}
                for step in steps:
                    status_by_key[step.step_key] = step.status
                    messages.append(
                        _format_sse(
                            "step",
                            {
                                "bid_id": bid_id,
                                "step": step.step_key,
                                "status": step.status,
                                "attempt": step.attempts,
                            },
                        )
                    )
                # run_error: có bước failed.
                if any(status == "failed" for status in status_by_key.values()):
                    terminal = True
                # waiting_clarification: gap dừng chờ trả lời.
                if status_by_key.get("gap") == "waiting_clarification":
                    terminal = True
                # done (M2): intake + gap đều completed.
                if (
                    status_by_key.get("intake") == "completed"
                    and status_by_key.get("gap") == "completed"
                ):
                    terminal = True
            finally:
                session.close()
        except Exception:  # noqa: BLE001 — replay lỗi không được làm sập stream
            logger.exception("SSE replay lỗi cho bid %s", bid_id)
        return messages, terminal

    async def subscribe(self, bid_id: int) -> AsyncIterator[str]:
        """Async generator: replay → live events + heartbeat → cleanup khi disconnect.

        Luồng tự đóng sau sự kiện cuối (done/clarify/error) hoặc ngay sau replay
        nếu hồ sơ đã ở trạng thái cuối — client không cần chờ vô hạn.
        """
        queue: asyncio.Queue = asyncio.Queue(maxsize=256)
        self._subscribers[bid_id].add(queue)
        try:
            messages, terminal = self._replay(bid_id)
            for message in messages:
                yield message
            if terminal:
                return

            while True:
                try:
                    message = await asyncio.wait_for(
                        queue.get(), timeout=self.heartbeat_interval
                    )
                    yield message
                    if _event_name(message) in _TERMINAL_EVENTS:
                        return
                except asyncio.TimeoutError:
                    yield _format_sse(
                        "heartbeat", {"bid_id": bid_id, "ts": _now_iso()}
                    )
        finally:
            self._subscribers[bid_id].discard(queue)
            if not self._subscribers[bid_id]:
                self._subscribers.pop(bid_id, None)
            logger.info("SSE subscriber đóng — bid %s", bid_id)


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


sse_manager = SSEManager()