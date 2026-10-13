from pydantic import BaseModel, ConfigDict, model_validator
import re

class ProposalOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sections: dict[str, str]
    assumptions_phrased: list[str] = []
    scope_out_phrased: list[str] = []

    @model_validator(mode="after")
    def valid_output(self):
        required = {"introduction", "requirements_understanding", "solution_overview", "approach", "schedule", "team", "assumptions_and_scope", "risks"}
        if set(self.sections) != required or any(not str(v).strip() for v in self.sections.values()):
            raise ValueError("Proposal phải đủ section và không được rỗng")
        text = " ".join([*self.sections.values(), *self.assumptions_phrased, *self.scope_out_phrased])
        if "{{QUOTATION}}" not in text:
            raise ValueError("Proposal phải chứa dòng {{QUOTATION}} cho cổng giá")
        if re.search(r"(?:[$¥₫]|\b(?:man-day|person-day|MD)\b)\s*\d*|\d+\s*(?:[$¥₫]|man-day|person-day|MD)", text, re.I):
            raise ValueError("Proposal không được chứa tiền hoặc man-day")
        if re.search(r"[$¥₫]\s*\d|\d\s*[$¥₫]|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b", text):
            raise ValueError("Proposal không được chứa số tiền")
        return self
