from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


SettingKey = Literal["effort", "rate_card", "factors", "company", "templates", "standard_content", "case_studies", "bid_no_bid", "confidence"]


class SettingSummary(BaseModel):
    key: SettingKey
    source: Literal["repo", "db"]
    version: int
    updated_by: str | None = None
    updated_at: datetime | None = None
    yaml_preview: str
    payload: Any = Field(default_factory=dict)


class SettingsResponse(BaseModel):
    keys: list[SettingSummary]


class SettingUpdate(BaseModel):
    yaml_content: str = Field(..., min_length=1)
    by: str = Field(..., min_length=1, max_length=100)


class SettingUpdated(BaseModel):
    key: SettingKey
    version: int
    source: Literal["db"]


class HistoryItem(BaseModel):
    id: int
    bid_id: int
    project_name: str
    customer_name: str
    status: str
    actor: str
    action: str
    field_changed: str | None = None
    note: str | None = None
    created_at: datetime


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
