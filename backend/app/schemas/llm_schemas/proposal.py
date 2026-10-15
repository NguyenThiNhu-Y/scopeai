from pydantic import BaseModel, ConfigDict, model_validator
import re

# 8 mục chuẩn của proposal — khóa JSON cố định bằng tiếng Anh (BR-02).
_REQUIRED_SECTIONS = frozenset({
    "introduction",
    "requirements_understanding",
    "solution_overview",
    "approach",
    "schedule",
    "team",
    "assumptions_and_scope",
    "risks",
})

# Bí danh khóa section theo ngôn ngữ khách (ja/vi/en) → khóa chuẩn tiếng Anh.
# Prompt B6 đã yêu cầu khóa cố định; ánh xạ này là lớp phòng thủ khi LLM vẫn
# dịch khóa — tránh đốt hết lượt retry chỉ vì lỗi định dạng khóa.
_SECTION_KEY_ALIASES: dict[str, str] = {
    # Tiếng Nhật (tên mục trong prompt B6).
    "はじめに": "introduction",
    "ご要件の理解": "requirements_understanding",
    "要件の理解": "requirements_understanding",
    "ご要件理解": "requirements_understanding",
    "提案概要": "solution_overview",
    "提案の概要": "solution_overview",
    "進め方": "approach",
    "進め方について": "approach",
    "スケジュール": "schedule",
    "スケジュール案": "schedule",
    "体制": "team",
    "実施体制": "team",
    "前提条件・対象外": "assumptions_and_scope",
    "前提条件と対象外": "assumptions_and_scope",
    "前提条件および対象外": "assumptions_and_scope",
    "リスク": "risks",
    "リスクと軽減策": "risks",
    # Tiếng Việt.
    "giới thiệu": "introduction",
    "hiểu yêu cầu": "requirements_understanding",
    "tổng quan giải pháp": "solution_overview",
    "cách tiếp cận": "approach",
    "cách làm": "approach",
    "lịch trình": "schedule",
    "đội ngũ": "team",
    "giả định và phạm vi": "assumptions_and_scope",
    "giả định và ngoài phạm vi": "assumptions_and_scope",
    "rủi ro": "risks",
    # Tiếng Anh (tiêu đề viết hoa, không phải snake_case).
    "introduction": "introduction",
    "requirements understanding": "requirements_understanding",
    "solution overview": "solution_overview",
    "approach": "approach",
    "schedule": "schedule",
    "team": "team",
    "assumptions and scope": "assumptions_and_scope",
    "assumptions & scope": "assumptions_and_scope",
    "risks": "risks",
}


def _normalize_section_key(key: str) -> str:
    """Đưa khóa về dạng chuẩn để tra bí danh: bỏ hoa/thường, khoảng trắng,
    dấu câu và ký tự nối (・, -, _, &, ., /, 、, 。, …)."""
    return re.sub(r"[\s・\-_&.,()/、。]+", "", key).casefold()


_SECTION_KEY_LOOKUP: dict[str, str] = {
    _normalize_section_key(alias): canonical
    for alias, canonical in _SECTION_KEY_ALIASES.items()
}


def _canonical_section_key(key: str) -> str | None:
    """Trả khóa chuẩn nếu ``key`` là khóa chuẩn hoặc bí danh đã biết; else None."""
    if key in _REQUIRED_SECTIONS:
        return key
    return _SECTION_KEY_LOOKUP.get(_normalize_section_key(key))


class ProposalOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sections: dict[str, str]
    assumptions_phrased: list[str] = []
    scope_out_phrased: list[str] = []

    @model_validator(mode="before")
    @classmethod
    def normalize_section_keys(cls, data):
        """Chuẩn hóa khóa ``sections``: bí danh ngôn ngữ → khóa chuẩn tiếng Anh.

        Chỉ ánh xạ khóa đã biết; khóa lạ giữ nguyên để validator sau vẫn chặn
        (sai schema → retry như BR-02).
        """
        if isinstance(data, dict) and isinstance(data.get("sections"), dict):
            sections = {}
            for key, value in data["sections"].items():
                canonical = _canonical_section_key(key)
                sections[canonical if canonical is not None else key] = value
            data = {**data, "sections": sections}
        return data

    @model_validator(mode="after")
    def valid_output(self):
        if set(self.sections) != _REQUIRED_SECTIONS or any(not str(v).strip() for v in self.sections.values()):
            raise ValueError("Proposal phải đủ section và không được rỗng")
        text = " ".join([*self.sections.values(), *self.assumptions_phrased, *self.scope_out_phrased])
        if "{{QUOTATION}}" not in text:
            raise ValueError("Proposal phải chứa dòng {{QUOTATION}} cho cổng giá")
        if re.search(r"(?:[$¥₫]|\b(?:man-day|person-day|MD)\b)\s*\d*|\d+\s*(?:[$¥₫]|man-day|person-day|MD)", text, re.I):
            raise ValueError("Proposal không được chứa tiền hoặc man-day")
        if re.search(r"[$¥₫]\s*\d|\d\s*[$¥₫]|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b", text):
            raise ValueError("Proposal không được chứa số tiền")
        return self