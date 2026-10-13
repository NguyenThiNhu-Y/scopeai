"""Cấu hình logging — cấm in API key / secret (BR-06, NFR-005)."""

from __future__ import annotations

import logging
import re

from app.core.config import settings

# Các pattern nhạy cảm bị chặn trong mọi dòng log.
_SENSITIVE_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"(Bearer\s+)[A-Za-z0-9._~+/=-]+", re.IGNORECASE),
    re.compile(r"(Authorization\s*[:=]\s*)[^\s,;]+", re.IGNORECASE),
)


class RedactingFormatter(logging.Formatter):
    """Formatter chặn API key và pattern secret trước khi in ra."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        key = getattr(settings, "llm_api_key", "") or ""
        if key:
            message = message.replace(key, "[REDACTED]")
        for pattern in _SENSITIVE_PATTERNS:
            message = pattern.sub(lambda m: m.group(1) + "[REDACTED]" if m.lastindex else "[REDACTED]", message)
        return message


def setup_logging() -> None:
    """Cấu hình root logger một lần (idempotent)."""
    root = logging.getLogger()
    if any(isinstance(h.formatter, RedactingFormatter) for h in root.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level)