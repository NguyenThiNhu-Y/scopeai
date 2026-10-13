"""Structured output schema for customer-language clarification email drafts."""

from pydantic import BaseModel, Field


class EmailDraft(BaseModel):
    """Editable email content; identity fields are supplied by application code."""

    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
