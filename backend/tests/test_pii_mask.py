"""Tests cho privacy/mask.py — bộ PII ≥ 50 mẫu, tỷ lệ che ≥ 99% (NFR-002)."""

from __future__ import annotations

from app.privacy import mask_text
from app.privacy.mask import mask_email, mask_phone_jp, mask_phone_vn
from tests.fixtures.pii_samples import (
    ALL_SAMPLES,
    EMAIL_BODY_SAMPLES,
    EMAIL_SAMPLES,
    JP_PHONE_SAMPLES,
    MIXED_SAMPLES,
    NEGATIVE_SAMPLES,
    POSITIVE_SAMPLES,
    VN_PHONE_SAMPLES,
)

MARKERS = ("[EMAIL]", "[PHONE_VN]", "[PHONE_JP]")


def test_sample_count_at_least_50():
    assert len(ALL_SAMPLES) >= 50
    assert len(EMAIL_SAMPLES) >= 15
    assert len(VN_PHONE_SAMPLES) >= 15
    assert len(JP_PHONE_SAMPLES) >= 15
    assert len(MIXED_SAMPLES) >= 5
    assert len(NEGATIVE_SAMPLES) >= 5
    # M2: ≥ 10 mẫu email/SĐT lẫn trong thân email tiếng Việt + tiếng Nhật.
    assert len(EMAIL_BODY_SAMPLES) >= 10


def test_each_pii_category_masked():
    for sample in EMAIL_SAMPLES:
        masked = mask_text(sample)
        assert masked != sample and "[EMAIL]" in masked, f"Email chưa che: {sample!r}"

    for sample in VN_PHONE_SAMPLES:
        masked = mask_text(sample)
        assert masked != sample and "[PHONE_VN]" in masked, f"SĐT VN chưa che: {sample!r}"

    for sample in JP_PHONE_SAMPLES:
        masked = mask_text(sample)
        assert masked != sample and "[PHONE_JP]" in masked, f"SĐT Nhật chưa che: {sample!r}"

    for sample in MIXED_SAMPLES:
        masked = mask_text(sample)
        assert masked != sample, f"Văn bản hỗn hợp chưa che: {sample!r}"
        assert any(marker in masked for marker in MARKERS)

    for sample in EMAIL_BODY_SAMPLES:
        masked = mask_text(sample)
        assert masked != sample, f"Thân email chưa che PII: {sample!r}"
        assert any(marker in masked for marker in MARKERS)


def test_masking_rate_at_least_99_percent():
    masked_count = sum(1 for sample in POSITIVE_SAMPLES if mask_text(sample) != sample)
    rate = masked_count / len(POSITIVE_SAMPLES)
    assert rate >= 0.99, f"Tỷ lệ che chỉ đạt {rate:.2%}"


def test_negative_samples_not_masked():
    for sample in NEGATIVE_SAMPLES:
        assert mask_text(sample) == sample, f"Che nhầm mẫu âm: {sample!r}"


def test_unit_functions():
    assert mask_email("a@b.com") == "[EMAIL]"
    assert mask_phone_vn("0912345678") == "[PHONE_VN]"
    assert mask_phone_jp("03-1234-5678") == "[PHONE_JP]"
    assert mask_text("email a@b.com, SĐT 0912345678") == "email [EMAIL], SĐT [PHONE_VN]"
