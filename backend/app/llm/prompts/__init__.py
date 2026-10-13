"""Prompt builders cho các bước pipeline (M2: B1 Intake, B2 Gap)."""

from app.llm.prompts.b1_intake import build_intake_prompt
from app.llm.prompts.b2_gap import build_gap_prompt

__all__ = ["build_gap_prompt", "build_intake_prompt"]