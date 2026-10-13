from typing import Literal
from pydantic import BaseModel
class EvaluationItemOut(BaseModel):
    req_code: str; content: str; priority: str | None; category: str | None
    rating: Literal["◎", "○", "△", "×", "cần làm rõ"]; needs_clarification: bool; note_vi: str
    solution_direction: str | None; batch_no: int
class EvaluationResponse(BaseModel):
    solution_direction: dict | None
    warnings: list[dict]
    items: list[EvaluationItemOut]
    stats: dict
