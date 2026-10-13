from typing import Literal
from pydantic import BaseModel, Field


class JaIssue(BaseModel):
    severity: Literal["warning"]
    section: str = Field(min_length=1)
    message_vi: str = Field(min_length=1)
    suggestion_ja: str = Field(min_length=1)
    source: Literal["latin", "glossary", "name", "llm_context"]


class JaCheckResult(BaseModel):
    result: Literal["pass", "warning"]
    issues: list[JaIssue]
