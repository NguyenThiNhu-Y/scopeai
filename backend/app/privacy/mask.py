"""Che PII (email, SĐT Việt Nam, SĐT Nhật Bản) — deterministic, thuần regex.

BR-06 / NFR-002: mọi văn bản gửi LLM phải qua ``mask_text`` trước.
Nhãn thay thế: ``[EMAIL]``, ``[PHONE_VN]``, ``[PHONE_JP]``.

Lưu ý thứ tự: che SĐT Nhật TRƯỚC SĐT Việt Nam để tránh nhầm định dạng
``0X0-XXXX-XXXX`` (Nhật) với ``091-234-5678`` (Việt Nam).
"""

from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

# Nhật: +81 / 0081 + (1-2 số) + 4 + 4
_JP_INTL_RE = re.compile(
    r"(?<!\d)\(?(\+81|0081)\)?[-.\s]?\d{1,2}[-.\s]?\d{4}[-.\s]?\d{4}(?!\d)"
)
# Nhật: 0X-XXXX-XXXX / 0X XXXX XXXX (bắt buộc có dấu phân tách giữa các nhóm)
_JP_LOCAL_RE = re.compile(r"(?<!\d)0\d{1,2}[-.\s]\d{4}[-.\s]\d{4}(?!\d)")
# Nhật: 11 chữ số liền nhau bắt đầu bằng 0 (vd 08012345678)
_JP_UNSEP_RE = re.compile(r"(?<!\d)0\d{2}\d{4}\d{4}(?!\d)")

# Việt Nam: +84 / 0084 + 2 + 3 + (3-4)
_VN_INTL_RE = re.compile(
    r"(?<!\d)\(?(\+84|0084)\)?[-.\s]?\d{2}[-.\s]?\d{3}[-.\s]?\d{3,4}(?!\d)"
)
# Việt Nam: 0 + 2 + 3 + (3-4) — vd 0912345678, 091-234-5678, 028 1234 567
_VN_GROUP_RE = re.compile(r"(?<!\d)0\d{2}[-.\s]?\d{3}[-.\s]?\d{3,4}(?!\d)")
# Việt Nam: 0 + 3 + 3 + 3 — vd 0912 345 678
_VN_GROUP3_RE = re.compile(r"(?<!\d)0\d{3}[-.\s]?\d{3}[-.\s]?\d{3}(?!\d)")
# Việt Nam: 0 + 2 + 4 + (3-4) — vd 028 1234 567 (điện thoại bàn Hà Nội)
_VN_GROUP4_RE = re.compile(r"(?<!\d)0\d{2}[-.\s]?\d{4}[-.\s]?\d{3,4}(?!\d)")


def mask_email(text: str) -> str:
    """Che mọi địa chỉ email bằng ``[EMAIL]``."""
    return _EMAIL_RE.sub("[EMAIL]", text)


def mask_phone_jp(text: str) -> str:
    """Che SĐT Nhật Bản (0X-XXXX-XXXX, +81/0081, 11 số liền) bằng ``[PHONE_JP]``."""
    text = _JP_INTL_RE.sub("[PHONE_JP]", text)
    text = _JP_LOCAL_RE.sub("[PHONE_JP]", text)
    text = _JP_UNSEP_RE.sub("[PHONE_JP]", text)
    return text


def mask_phone_vn(text: str) -> str:
    """Che SĐT Việt Nam (+84/0xx) bằng ``[PHONE_VN]``."""
    text = _VN_INTL_RE.sub("[PHONE_VN]", text)
    text = _VN_GROUP_RE.sub("[PHONE_VN]", text)
    text = _VN_GROUP3_RE.sub("[PHONE_VN]", text)
    text = _VN_GROUP4_RE.sub("[PHONE_VN]", text)
    return text


def mask_text(text: str) -> str:
    """Che toàn bộ PII (email + SĐT VN + SĐT Nhật). Deterministic."""
    text = mask_email(text)
    text = mask_phone_jp(text)
    text = mask_phone_vn(text)
    return text