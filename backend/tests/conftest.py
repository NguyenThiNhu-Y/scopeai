"""Cấu hình pytest chung — ép LLM_PROVIDER=mock (BR-03), DB test tạm.

QUAN TRỌNG: phải set env TRƯỚC khi import app để ``Settings`` đọc đúng.
"""

from __future__ import annotations

import os

# BR-03: test/CI không bao giờ gọi LLM thật.
os.environ["LLM_PROVIDER"] = "mock"
os.environ.setdefault("LLM_MAX_RETRIES", "2")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core import db  # noqa: E402
from app.llm.mock_client import MockLLMClient  # noqa: E402


@pytest.fixture(autouse=True)
def _tmp_db(tmp_path, monkeypatch):
    """Mỗi test dùng một SQLite tạm riêng — không đụng data/bidding.db thật."""
    url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(db, "SessionLocal", session_local)
    db.Base.metadata.create_all(engine)
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_pipeline_state():
    """Dọn registry runner + subscriber SSE giữa các test (tránh nhiễu bid_id lặp)."""
    yield
    from app.pipeline import runner
    from app.pipeline.sse import sse_manager

    runner._running.clear()
    sse_manager._subscribers.clear()


@pytest.fixture()
def client(_tmp_db):
    """TestClient — lifespan chạy init_db() trên DB tạm."""
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def mock_llm(monkeypatch):
    """Cho phép test kiểm soát MockLLMClient dùng trong pipeline (BR-03).

    Test gán ``mock_llm["client"]`` trước khi start pipeline; orchestrator gọi
    ``get_llm_client()`` mỗi lần chạy → đọc client hiện tại từ holder.
    """
    import sys

    orchestrator_module = sys.modules["app.pipeline.orchestrator"]

    holder: dict = {"client": MockLLMClient()}
    monkeypatch.setattr(orchestrator_module, "get_llm_client", lambda: holder["client"])
    return holder