"""API schemas cho hồ sơ mẫu giả lập — contract api_contract.md §3.7 (M2)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class SampleIn(BaseModel):
    """Body ``POST /api/bids/sample`` — thiếu ``sample_key`` → mặc định ``ja_email``."""

    sample_key: Literal["ja_email", "vi_email"] | None = None