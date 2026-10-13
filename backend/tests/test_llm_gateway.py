"""Tests cho LLM gateway (BR-02, BR-03, BR-06)."""

from __future__ import annotations

import httpx
import pytest

from app.llm import LLMSchemaError, complete_with_retry, get_llm_client
from app.llm.mock_client import MockLLMClient
from app.schemas.llm_schemas import RfpSummary


@pytest.fixture(autouse=True)
def _block_real_http(monkeypatch):
    """BR-03: test không bao giờ gọi HTTP ra ngoài."""
    calls: list = []

    def _forbidden(*args, **kwargs):
        calls.append(args)
        raise AssertionError("Test đã cố gọi HTTP ra ngoài!")

    monkeypatch.setattr(httpx, "post", _forbidden)
    monkeypatch.setattr(httpx, "get", _forbidden)
    monkeypatch.setattr(httpx, "stream", _forbidden)
    return calls


def test_get_llm_client_default_is_mock():
    """(1) Factory mặc định trả MockLLMClient (LLM_PROVIDER=mock trong test)."""
    client = get_llm_client()
    assert isinstance(client, MockLLMClient)


def test_mock_valid_fixture_returns_rfp_summary():
    """(2) Fixture hợp lệ trả JSON đúng RfpSummary."""
    client = MockLLMClient()
    result = client.complete(schema=RfpSummary, prompt="Tóm tắt RFP.")
    validated = RfpSummary.model_validate(result)
    assert validated.summary_vi
    assert 1 <= len(validated.keywords) <= 10
    assert 1 <= len(validated.notes) <= 5


def test_retry_on_invalid_schema():
    """(3) Fixture xấu → retry ≤ 2 → lỗi rõ (BR-02)."""
    client = MockLLMClient(fixture_mode="bad_schema")
    with pytest.raises(LLMSchemaError) as exc_info:
        complete_with_retry(client, RfpSummary, "prompt", max_retries=2)
    assert client.call_count == 3  # 1 lần đầu + 2 lần retry
    assert "RfpSummary" in str(exc_info.value)


def test_with_number_fixture_blocked_by_schema():
    """BR-01: fixture chứa man_day bị chặn ngay ở lớp schema (extra=forbid)."""
    client = MockLLMClient(fixture_mode="with_number")
    with pytest.raises(LLMSchemaError):
        complete_with_retry(client, RfpSummary, "prompt", max_retries=2)


def test_no_http_request_in_tests(_block_real_http):
    """(4) Không có request HTTP nào trong test (BR-03)."""
    client = get_llm_client()
    result = client.complete(schema=RfpSummary, prompt="Tóm tắt RFP.")
    assert RfpSummary.model_validate(result)
    assert _block_real_http == []


def test_prompt_is_masked_before_send():
    """(5) Prompt gửi vào mock đã được che PII (BR-06)."""
    client = MockLLMClient()
    prompt = "Liên hệ minh.nguyen@example.com hoặc 0912345678, fax 03-1234-5678."
    client.complete(schema=RfpSummary, prompt=prompt)

    assert client.last_prompt is not None
    assert "minh.nguyen@example.com" not in client.last_prompt
    assert "0912345678" not in client.last_prompt
    assert "03-1234-5678" not in client.last_prompt
    assert "[EMAIL]" in client.last_prompt
    assert "[PHONE_VN]" in client.last_prompt
    assert "[PHONE_JP]" in client.last_prompt