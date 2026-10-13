from typing import Literal
from pydantic import BaseModel, Field
class SheetMapping(BaseModel):
    sheet_name: str
    sheet_kind: Literal["requirement", "sample_data", "other"] = "requirement"
    col_map: dict[str, str] = Field(default_factory=dict)
class AttachmentOut(BaseModel):
    id: int; filename: str; file_type: str; detected_type: str; size_bytes: int
    parse_status: str; parse_error: str | None = None; sheet_mappings: list = []
    model_config = {"from_attributes": True}
class AttachmentListOut(BaseModel): items: list[AttachmentOut]
class AttachmentUpdate(BaseModel):
    file_type: Literal["rfp", "requirement", "sample_data"] | None = None
    sheet_mappings: list[SheetMapping] | None = None
class RequirementsCount(BaseModel): count: int; no_requirement_file: bool
class ParseOut(BaseModel):
    requirements: RequirementsCount
    attachments: list[dict]
    sample_profile: dict | None = None
    column_mapping_confirmed: bool
class ParseConfirmIn(BaseModel):
    data_readiness: Literal["low", "medium", "high"]
    confirmed: bool
