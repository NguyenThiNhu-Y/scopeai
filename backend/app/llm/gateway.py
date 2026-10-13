"""Gateway LLM: protocol, factory, retry + validate (BR-02, BR-03, BR-06)."""

from __future__ import annotations

import json
import logging
import time
from typing import Protocol

from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.llm.mock_client import MockLLMClient
from app.llm.openai_compat_client import LLMProviderError, OpenAICompatClient

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """Interface duy nhất cho mọi lời gọi LLM (BR-03)."""

    def complete(
        self,
        *,
        schema: type[BaseModel],
        prompt: str,
        context: dict | None = None,
    ) -> dict:
        """Gọi LLM, trả dict JSON. Prompt ĐÃ được che PII trước khi gửi (BR-06)."""
        ...


class LLMSchemaError(RuntimeError):
    """Output LLM sai schema sau khi đã retry tối đa (BR-02)."""


def get_llm_client() -> LLMClient:
    """Factory đọc env ``LLM_PROVIDER``: mock (mặc định) | openai_compat."""
    if settings.llm_provider == "openai_compat":
        # TLS: CA bundle tùy chỉnh thắng; nếu không có thì dùng cờ verify bool
        # (LLM_VERIFY_SSL=false cho endpoint nội bộ self-signed).
        verify: bool | str = settings.llm_ca_bundle or settings.llm_verify_ssl
        return OpenAICompatClient(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            response_format_json=settings.llm_response_format_json,
            verify=verify,
        )
    return MockLLMClient()


def complete_with_retry(
    client: LLMClient,
    schema: type[BaseModel],
    prompt: str,
    context: dict | None = None,
    max_retries: int | None = None,
) -> dict:
    """Gọi ``client.complete``, validate theo ``schema``, retry ≤ 2 (BR-02).

    Raises:
        LLMSchemaError: nếu output sai schema sau ``max_retries + 1`` lần thử.
    """
    if max_retries is None:
        max_retries = settings.llm_max_retries
    last_error: Exception | None = None
    retry_prompt = prompt
    for attempt in range(max_retries + 1):
        try:
            raw = client.complete(schema=schema, prompt=retry_prompt, context=context)
            validated = schema.model_validate(raw)
            return validated.model_dump()
        except LLMProviderError as exc:
            last_error = exc
            logger.warning("LLM provider lỗi (lần %d/%d): %s", attempt + 1, max_retries + 1, exc)
        except (ValidationError, json.JSONDecodeError) as exc:
            last_error = exc
            retry_prompt = (
                f"{prompt}\n\nSchema validation error from previous attempt: "
                f"{str(exc)[:500]}"
            )
            logger.warning(
                "Output LLM không đúng schema %s (lần %d/%d): %s",
                schema.__name__,
                attempt + 1,
                max_retries + 1,
                exc,
            )
        if attempt < max_retries:
            time.sleep(2**attempt)
    if isinstance(last_error, LLMProviderError):
        detail = (
            f"Lỗi gọi LLM provider sau {max_retries + 1} lần thử "
            f"(retry ≤ {max_retries}): {last_error}"
        )
    else:
        detail = (
            f"Output LLM không đúng schema {schema.__name__} sau "
            f"{max_retries + 1} lần thử (retry ≤ {max_retries}): {last_error}"
        )
    raise LLMSchemaError(detail) from last_error
