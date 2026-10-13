"""Rule-based Japanese export lint, with a bounded optional gateway assist."""
import re
from app.llm.gateway import LLMSchemaError, complete_with_retry, get_llm_client
from app.privacy.mask import mask_text
from app.schemas.api_schemas.export import JaCheckResult

_LATIN = re.compile(r"[A-Za-z]{2,}")
_ALLOWED = {"CRM", "API", "AI", "IT", "RFP", "WBS", "QA", "PDF", "DOCX", "Excel"}


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
            assist = complete_with_retry(client, JaCheckResult, mask_text("Đánh giá ngữ cảnh: " + " ".join(x["message_vi"] for x in issues)), {"customer_language": "ja"}, max_retries=2)
            if assist.get("result") == "warning":
                issues.extend(i for i in assist.get("issues", []) if i not in issues)
        except (LLMSchemaError, ValueError, KeyError):
            pass
    return JaCheckResult(result="warning" if issues else "pass", issues=issues).model_dump()
