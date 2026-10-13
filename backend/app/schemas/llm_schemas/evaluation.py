from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
class EvaluationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    req_code: str = Field(..., min_length=1)
    rating: Literal["◎", "○", "△", "×", "cần làm rõ"]
    needs_clarification: bool
    note_vi: str = Field(..., max_length=200)
class EvaluationBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    batch: list[EvaluationItem]
