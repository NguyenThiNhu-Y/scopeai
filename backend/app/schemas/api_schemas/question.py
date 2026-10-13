"""API schemas cho hỏi làm rõ — contract api_contract.md §6 (M2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class QuestionOut(BaseModel):
    """Một câu hỏi làm rõ (contract §6.1)."""

    id: int
    round_no: int
    question: str
    reason_vi: str
    impact: str
    related_req_codes: list[str] = Field(default_factory=list)
    answer: str | None = None
    is_assumption: bool = False
    status: str


class AnswerItemIn(BaseModel):
    """Một câu trả lời (contract §6.2)."""

    question_id: int
    answer: str
    is_assumption: bool = False


class AnswersIn(BaseModel):
    """Body ``POST /api/bids/{id}/questions/{round}/answers``."""

    answers: list[AnswerItemIn]


class QuestionsOut(BaseModel):
    """Response 200 ``GET /api/bids/{id}/questions`` (contract §6.1)."""

    items: list[QuestionOut]
    rounds_used: int
    max_rounds: int
    round_two_reason_vi: str | None = None


class AnswersOut(BaseModel):
    """Response 200 ``POST .../answers`` (contract §6.2)."""

    status: str
    pipeline_resumed_from: str
    warnings: list[str] = Field(default_factory=list)
