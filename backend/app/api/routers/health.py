"""GET /api/health — contract đóng băng api_contract.md §3.0.

Luôn trả HTTP 200; trạng thái lỗi thể hiện qua ``status``/``database``.
KHÔNG bao giờ trả LLM_API_KEY / LLM_BASE_URL (BR-06, NFR-005).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter

from app import __version__
from app.core import db
from app.core.config import settings
from app.schemas.api_schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

_APP_NAME = "presales-bidding-assistant"
_DB_ERROR_VI = "error: Không kết nối được cơ sở dữ liệu"


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        db.check_db()
        db_status = "ok"
        status = "ok"
    except Exception:  # noqa: BLE001 — DB lỗi không được làm sập endpoint
        logger.exception("Health check: lỗi kết nối cơ sở dữ liệu")
        db_status = _DB_ERROR_VI
        status = "degraded"

    return HealthResponse(
        status=status,
        app=_APP_NAME,
        version=__version__,
        llm_provider=settings.llm_provider,
        database=db_status,
        time=datetime.now(timezone.utc),
    )