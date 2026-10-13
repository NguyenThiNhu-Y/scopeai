"""Cấu hình tập trung từ env vars + file ``.env``.

Quy tắc (AGENTS.md BR-06, NFR-005):
- Không bao giờ log/in ra giá trị ``LLM_API_KEY``.
- Không hardcode secret trong code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

_ALLOWED_PROVIDERS = ("mock", "openai_compat")

# Đọc thêm từ file ``.env`` (tìm từ thư mục hiện tại trở lên). Env vars thật
# (VD: do Preview/CI/container bơm vào) vẫn ưu tiên hơn — ``override=False`` mặc định.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Cấu hình ứng dụng đọc từ env vars (mặc định phù hợp M1)."""

    llm_provider: str
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    database_url: str
    app_env: str
    log_level: str
    llm_max_retries: int
    llm_response_format_json: bool
    llm_verify_ssl: bool
    llm_ca_bundle: str
    rfp_summary_max_chars: int
    cors_origins: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
        if provider not in _ALLOWED_PROVIDERS:
            # Giá trị env lạ không được làm sập app; quay về mock an toàn (test/CI/demo).
            provider = "mock"
        try:
            max_retries = int(os.getenv("LLM_MAX_RETRIES", "2"))
        except ValueError:
            max_retries = 2
        response_format_json = os.getenv("LLM_RESPONSE_FORMAT_JSON", "true").strip().lower() not in {"0", "false", "no", "off"}
        verify_ssl = os.getenv("LLM_VERIFY_SSL", "true").strip().lower() not in {"0", "false", "no", "off"}
        try:
            summary_max_chars = max(1, int(os.getenv("RFP_SUMMARY_MAX_CHARS", "8000")))
        except ValueError:
            summary_max_chars = 8000
        return cls(
            llm_provider=provider,
            llm_base_url=os.getenv("LLM_BASE_URL", "").strip(),
            llm_api_key=os.getenv("LLM_API_KEY", "").strip(),
            llm_model=os.getenv("LLM_MODEL", "").strip(),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./data/bidding.db").strip(),
            app_env=os.getenv("APP_ENV", "development").strip(),
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
            llm_max_retries=max_retries,
            llm_response_format_json=response_format_json,
            llm_verify_ssl=verify_ssl,
            llm_ca_bundle=os.getenv("LLM_CA_BUNDLE", "").strip(),
            rfp_summary_max_chars=summary_max_chars,
            cors_origins=tuple(
                origin.strip()
                for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
                if origin.strip()
            ),
        )


settings = Settings.from_env()
