"""HealthResponse — contract đóng băng §2.1/§2.3 (api_contract.md)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response của ``GET /api/health`` — luôn HTTP 200."""

    status: Literal["ok", "degraded"]
    app: str
    version: str
    llm_provider: Literal["mock", "openai_compat"]
    database: str
    time: datetime