from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class BidCriterion(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    label_vi: str = Field(..., min_length=1, max_length=200)
    weight: float = Field(..., ge=0, le=100)
    score: float | None = Field(default=None, ge=0, le=5)
    note_vi: str | None = Field(default=None, max_length=500)


class BidQualificationUpdate(BaseModel):
    criteria: list[BidCriterion] = Field(..., min_length=1)
    decision: Literal["bid", "no-bid"] | None = None
    confirmer: str | None = Field(default=None, min_length=1, max_length=100)


class BidQualificationOut(BidQualificationUpdate):
    bid_id: int
    suggestions: list[dict]
    confirmed_at: datetime | None = None
