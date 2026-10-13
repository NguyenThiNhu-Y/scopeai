from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

Currency = Literal["VND", "JPY", "USD"]
ContractModel = Literal["fixed_price", "tm", "odc"]


class QuotationSettingsIn(BaseModel):
    contract_model: ContractModel | None = None
    currency: Currency | None = None
    contingency_percent: float | None = Field(default=None, ge=0, le=100)
    onsite_percent: float | None = Field(default=None, ge=0, le=1)
    price_to_win_percent: float | None = Field(default=None, ge=-50, le=200)
    tm_months: int | None = Field(default=None, ge=1, le=240)
    odc_fte: float | None = Field(default=None, gt=0, le=10000)
    odc_months: int | None = Field(default=None, ge=1, le=240)

class QuotationOut(BaseModel):
    contract_model: str
    contingency_percent: float
    currency: str = "VND"
    fx_rate: dict
    valid_until: date | None
    tax_mode: str
    totals: dict
    budget: dict | None
    payment_milestones: list[dict] = Field(default_factory=list)
    price_to_win_percent: float = 0
    trace: dict
