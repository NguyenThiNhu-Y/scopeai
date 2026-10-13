"""OpenAICompatClient — gọi endpoint ``/chat/completions`` tương thích OpenAI.

- Dùng httpx (không SDK nặng — BR-09).
- KHÔNG bao giờ log/in API key (BR-06, NFR-005).
- Prompt luôn qua ``mask_text`` trước khi gửi (BR-06) — điểm chặn duy nhất.
"""

from __future__ import annotations

import json
import logging
import re

import httpx
from pydantic import BaseModel

from app.privacy import mask_text

logger = logging.getLogger(__name__)

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class LLMProviderError(RuntimeError):
    """Lỗi gọi provider (mạng, HTTP, response sai định dạng)."""


class OpenAICompatClient:
    """Client cho provider tương thích OpenAI Chat Completions."""

    def __init__(
        self,
        base_url: str = "",
        api_key: str = "",
        model: str = "",
        timeout: float = 60.0,
        response_format_json: bool = True,
        verify: bool | str = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.response_format_json = response_format_json
        # True = verify theo CA store hệ thống; False = bỏ qua (endpoint nội bộ
        # self-signed, người dùng chủ động bật qua LLM_VERIFY_SSL=false);
        # str = đường dẫn CA bundle tùy chỉnh (LLM_CA_BUNDLE).
        self.verify = verify

    def complete(
        self,
        *,
        schema: type[BaseModel],
        prompt: str,
        context: dict | None = None,
    ) -> dict:
        if not self.base_url:
            raise LLMProviderError("LLM_BASE_URL chưa được cấu hình")
        if not self.api_key:
            raise LLMProviderError("LLM_API_KEY chưa được cấu hình")
        if not self.model:
            raise LLMProviderError("LLM_MODEL chưa được cấu hình")

        # Điểm chặn duy nhất BR-06: che PII trước khi gửi ra ngoài.
        prompt = mask_text(prompt)

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
        system_prompt = (
            "Bạn là một API chỉ trả dữ liệu có cấu trúc. "
            "Chỉ trả về MỘT object JSON đúng JSON Schema sau:\n"
            f"{schema_json}"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
        }
        if self.response_format_json:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                verify=self.verify,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Lỗi gọi LLM provider: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMProviderError("Response LLM không phải JSON hợp lệ") from exc
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(
                "Response LLM thiếu trường choices[0].message.content"
            ) from exc

        content = _CODE_FENCE_RE.sub("", content.strip())
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMProviderError(f"Nội dung LLM không phải JSON hợp lệ: {exc}") from exc
