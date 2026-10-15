"""Rule-based Japanese export lint, with a bounded optional gateway assist."""
import json
import re
from app.llm.gateway import LLMSchemaError, complete_with_retry, get_llm_client
from app.privacy.mask import mask_text
from app.schemas.api_schemas.export import JaCheckResult

_LATIN = re.compile(r"[A-Za-z]{2,}")
_ALLOWED = {"CRM", "API", "AI", "IT", "RFP", "WBS", "QA", "PDF", "DOCX", "Excel"}
_MAX_SECTION_CHARS = 400


def _build_assist_prompt(sections: dict, customer_name: str, glossary: dict, issues: list[dict]) -> str:
    """Dựng prompt cho LLM phụ trợ — context GIỚI HẠN, có delimiter rõ (review M7 MEDIUM).

    Chỉ gửi: các section nghi ngờ (đã che PII, giới hạn ký tự), glossary và tên
    khách hàng sau masking. Không gửi binary/toàn văn RFP. Provider openai_compat
    chỉ gửi prompt chứ không gửi context, nên mọi dữ liệu hồ sơ phải nằm trong prompt.
    """
    parts = [
        "Bạn là chuyên gia kiểm tra chất lượng tiếng Nhật trong hồ sơ dự thầu.",
        "Dưới đây là dữ liệu hồ sơ giới hạn (đã che thông tin cá nhân) và nhiệm vụ.",
        "",
        "=== SECTION NGHI NGỜ (tối đa 400 ký tự mỗi section) ===",
    ]
    seen: set[str] = set()
    for issue in issues:
        section = issue.get("section", "")
        if section in seen:
            continue
        seen.add(section)
        text = str(sections.get(section, ""))
        parts.append(f"[{section}]\n{mask_text(text)[:_MAX_SECTION_CHARS]}")
    parts.append("")
    parts.append("=== GLOSSARY ===")
    parts.append(json.dumps(glossary, ensure_ascii=False))
    parts.append("")
    parts.append("=== TÊN KHÁCH HÀNG (đã che PII) ===")
    parts.append(mask_text(customer_name))
    parts.append("")
    parts.append("=== NHIỆM VỤ ===")
    parts.append("Đánh giá ngữ cảnh các lỗi sau và trả JSON đúng schema JaCheckResult:")
    parts.extend(f"- {issue.get('message_vi', '')}" for issue in issues)
    return "\n".join(parts)


def check_japanese(sections: dict, customer_name: str, glossary: dict | None = None, client=None) -> dict:
    glossary = glossary or {"proposal": "提案", "system": "システム", "schedule": "スケジュール"}
    issues = []
    for section, text in sections.items():
        value = str(text)
        for token in _LATIN.findall(value):
            if token not in _ALLOWED:
                issues.append({"severity": "warning", "section": section, "message_vi": f"Phát hiện thuật ngữ Latin chưa được duyệt: {token}", "suggestion_ja": "用語を日本語の表記に合わせてください。", "source": "latin"})
        for key in glossary:
            if key.lower() in value.lower():
                issues.append({"severity": "warning", "section": section, "message_vi": f"Thuật ngữ chưa khớp glossary: {key}", "suggestion_ja": str(glossary[key]), "source": "glossary"})
        if customer_name and customer_name not in value and section in ("introduction", "conclusion"):
            issues.append({"severity": "warning", "section": section, "message_vi": "Tên khách hàng chưa xuất hiện đúng như hồ sơ.", "suggestion_ja": customer_name, "source": "name"})
    # Only suspicious context is sent, never binary or unmasked customer text.
    if client and issues:
        try:
            assist = complete_with_retry(client, JaCheckResult, _build_assist_prompt(sections, customer_name, glossary, issues), {"customer_language": "ja"}, max_retries=2)
            if assist.get("result") == "warning":
                issues.extend(i for i in assist.get("issues", []) if i not in issues)
        except (LLMSchemaError, ValueError, KeyError):
            pass
    return JaCheckResult(result="warning" if issues else "pass", issues=issues).model_dump()
