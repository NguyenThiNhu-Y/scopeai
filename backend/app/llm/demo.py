"""CLI demo mock LLM + mask PII.

Chạy: ``cd backend && python -m app.llm.demo``

In ra (1) prompt ĐÃ che PII và (2) JSON kết quả từ MockLLMClient —
minh chứng mock (không gọi LLM thật) + mask (BR-06).
"""

from __future__ import annotations

import json

from app.llm import get_llm_client
from app.privacy import mask_text
from app.schemas.llm_schemas import RfpSummary

# Văn bản mẫu 100% GIẢ LẬP (BR-06) — có email + SĐT VN + SĐT Nhật.
SAMPLE_PROMPT = """Bạn là trợ lý presales. Tóm tắt RFP sau (đã che PII) thành JSON đúng schema.
Khách hàng ABC株式会社 (giả lập) gửi yêu cầu xây dựng hệ thống quản lý kho.
Liên hệ: bà Tanaka qua email tanaka.hanako@example.co.jp hoặc SĐT 03-1234-5678.
Phía Việt Nam: anh Minh (minh.nguyen@example.com, 0912 345 678)."""


def main() -> None:
    client = get_llm_client()
    result = client.complete(schema=RfpSummary, prompt=SAMPLE_PROMPT)
    masked_prompt = getattr(client, "last_prompt", None) or mask_text(SAMPLE_PROMPT)

    print("=== Prompt đã che PII ===")
    print(masked_prompt)
    print("\n=== Kết quả (mock — không gọi LLM thật) ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()