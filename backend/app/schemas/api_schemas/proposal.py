from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

SECTION_NAMES = ("introduction", "requirements_understanding", "solution_overview", "approach", "schedule", "team", "assumptions_and_scope", "risks")
class ProposalSections(BaseModel):
    introduction: str = Field(..., min_length=1)
    requirements_understanding: str = Field(..., min_length=1)
    solution_overview: str = Field(..., min_length=1)
    approach: str = Field(..., min_length=1)
    schedule: str = Field(..., min_length=1)
    team: str = Field(..., min_length=1)
    assumptions_and_scope: str = Field(..., min_length=1)
    risks: str = Field(..., min_length=1)
class ProposalUpdateIn(BaseModel):
    sections: ProposalSections
    customer_language: Literal["vi", "en", "ja"] | None = None
    by: str | None = None

class ProposalTranslateIn(BaseModel):
    language: Literal["vi", "en", "ja"]
    sections: ProposalSections | None = None
    by: str | None = Field(default=None, max_length=100)
class ProposalOut(BaseModel):
    bid_id: int
    sections: ProposalSections
    assumptions_phrased: list[str]
    scope_out_phrased: list[str]
    price_gate: str
    editable: bool
    updated_at: datetime
    quotation_markdown: str = "[Presales điền]"
    customer_language: Literal["vi", "en", "ja"] = "vi"
    translations: dict[str, ProposalSections] = Field(default_factory=dict)
    document: dict = Field(default_factory=dict)

class ProposalVersionCreateIn(BaseModel):
    by: str = Field(..., min_length=1, max_length=100)
    language: Literal["vi", "en", "ja"] | None = None

class DealStageUpdateIn(BaseModel):
    deal_stage: Literal["lead", "qualified", "proposal", "negotiation", "won", "lost"]
    note: str | None = Field(default=None, max_length=500)

class ProposalVersionOut(BaseModel):
    id: int
    version: str
    customer_language: str
    sections: ProposalSections
    sent: bool
    sent_at: datetime | None = None
    sent_note: str | None = None
    created_by: str
    created_at: datetime

class ProposalVersionSentIn(BaseModel):
    note: str | None = Field(default=None, max_length=500)
