"""Regression tests for the real OpenAI-compatible LLM contract."""

from __future__ import annotations

import json

import httpx
import pytest
from pydantic import BaseModel, ConfigDict

from app.llm.gateway import complete_with_retry, get_llm_client
from app.llm.openai_compat_client import LLMProviderError, OpenAICompatClient


class TinyResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str


def _response(content: str, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code,
        json={"choices": [{"message": {"content": content}}]},
        request=httpx.Request("POST", "https://llm.example/chat/completions"),
    )


def test_openai_compat_sends_schema_system_message_and_json_mode(monkeypatch):
    captured: dict = {}

    def fake_post(url, **kwargs):
        captured.update(kwargs)
        return _response(json.dumps({"answer": "ok"}))

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OpenAICompatClient("https://llm.example", "secret-not-printed", "model")

    assert client.complete(schema=TinyResult, prompt="Email a@example.com") == {"answer": "ok"}
    payload = captured["json"]
    assert payload["response_format"] == {"type": "json_object"}
    assert [message["role"] for message in payload["messages"]] == ["system", "user"]
    assert "Chỉ trả về MỘT object JSON đúng JSON Schema sau" in payload["messages"][0]["content"]
    assert json.dumps(TinyResult.model_json_schema(), ensure_ascii=False) in payload["messages"][0]["content"]
    assert "a@example.com" not in payload["messages"][1]["content"]


def test_openai_compat_can_disable_json_mode(monkeypatch):
    captured: dict = {}
    monkeypatch.setattr(httpx, "post", lambda url, **kwargs: captured.update(kwargs) or _response('{"answer":"ok"}'))
    client = OpenAICompatClient("https://llm.example", "key", "model", response_format_json=False)

    client.complete(schema=TinyResult, prompt="prompt")

    assert "response_format" not in captured["json"]


def test_openai_compat_verifies_tls_by_default(monkeypatch):
    captured: dict = {}
    monkeypatch.setattr(httpx, "post", lambda url, **kwargs: captured.update(kwargs) or _response('{"answer":"ok"}'))

    OpenAICompatClient("https://llm.example", "key", "model").complete(schema=TinyResult, prompt="prompt")

    assert captured["verify"] is True


def test_openai_compat_can_disable_tls_verification(monkeypatch):
    captured: dict = {}
    monkeypatch.setattr(httpx, "post", lambda url, **kwargs: captured.update(kwargs) or _response('{"answer":"ok"}'))

    OpenAICompatClient("https://llm.example", "key", "model", verify=False).complete(
        schema=TinyResult, prompt="prompt"
    )

    assert captured["verify"] is False


def test_openai_compat_accepts_custom_ca_bundle(monkeypatch):
    captured: dict = {}
    monkeypatch.setattr(httpx, "post", lambda url, **kwargs: captured.update(kwargs) or _response('{"answer":"ok"}'))

    OpenAICompatClient("https://llm.example", "key", "model", verify="/etc/ssl/certs/internal-ca.pem").complete(
        schema=TinyResult, prompt="prompt"
    )

    assert captured["verify"] == "/etc/ssl/certs/internal-ca.pem"


def test_get_llm_client_forwards_tls_settings(monkeypatch):
    import types

    captured: dict = {}

    class FakeClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("app.llm.gateway.OpenAICompatClient", FakeClient)
    fake_settings = types.SimpleNamespace(
        llm_provider="openai_compat",
        llm_base_url="https://llm.example",
        llm_api_key="key",
        llm_model="model",
        llm_response_format_json=True,
        llm_verify_ssl=False,
        llm_ca_bundle="",
    )
    monkeypatch.setattr("app.llm.gateway.settings", fake_settings)

    get_llm_client()
    assert captured["verify"] is False

    fake_settings.llm_verify_ssl = True
    fake_settings.llm_ca_bundle = "/etc/ssl/certs/internal-ca.pem"
    get_llm_client()
    assert captured["verify"] == "/etc/ssl/certs/internal-ca.pem"


def test_retry_retries_provider_errors_with_backoff(monkeypatch):
    calls: list[int] = []
    sleeps: list[float] = []

    class FlakyClient:
        def complete(self, **kwargs):
            calls.append(1)
            if len(calls) < 3:
                raise LLMProviderError("temporary provider failure")
            return {"answer": "ok"}

    monkeypatch.setattr("app.llm.gateway.time.sleep", sleeps.append)
    assert complete_with_retry(FlakyClient(), TinyResult, "prompt", max_retries=2) == {"answer": "ok"}
    assert len(calls) == 3
    assert sleeps == [1.0, 2.0]


def test_schema_retry_adds_previous_error_to_next_prompt(monkeypatch):
    prompts: list[str] = []

    class FixingClient:
        def complete(self, **kwargs):
            prompts.append(kwargs["prompt"])
            return {"wrong": "value"} if len(prompts) == 1 else {"answer": "ok"}

    result = complete_with_retry(FixingClient(), TinyResult, "prompt", max_retries=1)

    assert result == {"answer": "ok"}
    assert "Schema validation error from previous attempt" in prompts[1]
    assert len(prompts[1]) < 600
