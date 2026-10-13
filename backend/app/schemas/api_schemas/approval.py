from typing import Literal
from pydantic import BaseModel, Field
class TechApprovalIn(BaseModel):
    decision: Literal["approved", "rejected", "skip"]
    by: str | None = None
    comment: str | None = None
    skip_with_reason: str | None = None
class PriceApprovalIn(BaseModel):
    decision: Literal["approved", "rejected"]
    by: str | None = None
    contract_model: Literal["fixed_price", "tm", "odc"] = "fixed_price"
    contingency_percent: float = Field(default=20, ge=0, le=100)
    currency: Literal["VND", "JPY", "USD"] | None = None
    onsite_percent: float | None = Field(default=None, ge=0, le=1)
    price_to_win_percent: float = Field(default=0, ge=-50, le=200)
    tm_months: int | None = Field(default=None, ge=1, le=240)
    odc_fte: float | None = Field(default=None, gt=0, le=10000)
    odc_months: int | None = Field(default=None, ge=1, le=240)
    comment: str | None = None
class UnlockIn(BaseModel):
    reason: str = Field(..., min_length=1)
    by: str | None = None
