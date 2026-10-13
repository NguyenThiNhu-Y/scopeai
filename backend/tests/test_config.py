"""Tests cho Settings.from_env — TLS của LLM gateway (LLM_VERIFY_SSL / LLM_CA_BUNDLE) + đọc file .env."""

from __future__ import annotations

from app.core.config import Settings


def test_llm_tls_defaults_verify_true(monkeypatch):
    monkeypatch.delenv("LLM_VERIFY_SSL", raising=False)
    monkeypatch.delenv("LLM_CA_BUNDLE", raising=False)

    settings = Settings.from_env()

    assert settings.llm_verify_ssl is True
    assert settings.llm_ca_bundle == ""


def test_llm_verify_ssl_false_parsed(monkeypatch):
    monkeypatch.setenv("LLM_VERIFY_SSL", "false")
    monkeypatch.delenv("LLM_CA_BUNDLE", raising=False)

    assert Settings.from_env().llm_verify_ssl is False


def test_llm_ca_bundle_path_parsed(monkeypatch):
    monkeypatch.delenv("LLM_VERIFY_SSL", raising=False)
    monkeypatch.setenv("LLM_CA_BUNDLE", "/etc/ssl/certs/internal-ca.pem")

    settings = Settings.from_env()

    assert settings.llm_verify_ssl is True
    assert settings.llm_ca_bundle == "/etc/ssl/certs/internal-ca.pem"


def test_settings_reads_from_dotenv_file(monkeypatch, tmp_path):
    """Settings đọc thêm từ file ``.env`` (dotenv) khi env var không được set."""
    from app.core.config import load_dotenv

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "LLM_VERIFY_SSL=false\nLLM_CA_BUNDLE=/etc/ssl/certs/internal-ca.pem\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("LLM_VERIFY_SSL", raising=False)
    monkeypatch.delenv("LLM_CA_BUNDLE", raising=False)

    load_dotenv(tmp_path / ".env")

    settings = Settings.from_env()
    assert settings.llm_verify_ssl is False
    assert settings.llm_ca_bundle == "/etc/ssl/certs/internal-ca.pem"


def test_real_env_var_overrides_dotenv_file(monkeypatch, tmp_path):
    """Env var thật ưu tiên hơn giá trị trong file ``.env`` (override=False)."""
    from app.core.config import load_dotenv

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("LLM_VERIFY_SSL=false\n", encoding="utf-8")
    monkeypatch.setenv("LLM_VERIFY_SSL", "true")

    load_dotenv(tmp_path / ".env")

    assert Settings.from_env().llm_verify_ssl is True