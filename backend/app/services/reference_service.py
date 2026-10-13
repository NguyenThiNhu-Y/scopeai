from __future__ import annotations

from pathlib import Path
import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import ReferenceSetting

ROOT = Path(__file__).resolve().parents[1]

def _load(key: str, filename: str, session: Session | None = None) -> dict:
    # Một số caller/test dùng fake session chỉ implement query(), không phải
    # toàn bộ Session API. Chỉ dùng override khi session có get(); nếu không
    # thì quay về bảng chuẩn, vẫn giữ DB override cho Session thật.
    if session is not None and hasattr(session, "get"):
        row = session.get(ReferenceSetting, key)
        if row is not None:
            return row.payload
    with (ROOT / "reference" / filename).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_rate_card(session: Session | None = None) -> dict:
    data = _load("rate_card", "rate_card.yaml", session)
    if not isinstance(data, dict) or not isinstance(data.get("rates"), dict):
        raise ValueError("rate_card.yaml không hợp lệ")
    required = {"pm", "ba", "brse", "ai_engineer", "backend", "frontend", "qa", "infra"}
    if set(data["rates"]) != required:
        raise ValueError("rate_card.yaml thiếu vai trò")
    if data.get("version", 0) <= 0 or not data.get("fx"):
        raise ValueError("rate_card.yaml thiếu version hoặc FX")
    return data


def load_effort(session: Session | None = None) -> dict:
    data = _load("effort", "effort.yaml", session)
    directions = data.get("directions", {})
    if set(directions) != {"none", "traditional_ml", "rag", "agent", "fine_tune"}:
        raise ValueError("Bảng effort thiếu tổ hợp hướng giải pháp")
    for phases in directions.values():
        if set(phases) != {"poc", "mvp", "production"}:
            raise ValueError("Bảng effort thiếu phase")
        for value in phases.values():
            if value["min"] < 0 or value["min"] > value["max"]:
                raise ValueError("Dải effort không hợp lệ")
        if phases["mvp"]["min"] <= phases["poc"]["max"]:
            raise ValueError("MVP phải lớn hơn PoC theo dải effort")
        if phases["mvp"]["min"] <= phases["production"]["max"]:
            raise ValueError("MVP phải lớn hơn Production theo dải effort")
    return data


def load_factors(session: Session | None = None) -> dict:
    data = _load("factors", "factors.yaml", session)
    if data.get("factor_cap", 0) <= 0:
        raise ValueError("factor_cap không hợp lệ")
    return data


def load_holidays() -> dict:
    """Nghỉ lễ VN/Nhật 2026 — ``{"vn": [...], "jp": [...]}`` (holidays.yaml)."""
    with (ROOT / "reference" / "holidays.yaml").open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    for key in ("vn", "jp"):
        if not isinstance(data.get(key), list) or not data[key]:
            raise ValueError(f"holidays.yaml thiếu danh sách nghỉ lễ '{key}'")
    return data


def load_payment() -> dict:
    """Mốc thanh toán mặc định — ``{"milestones": [{name, percent, due_offset_days}]}``."""
    with (ROOT / "reference" / "payment.yaml").open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    milestones = data.get("milestones")
    if not isinstance(milestones, list) or not milestones:
        raise ValueError("payment.yaml thiếu milestones")
    total = sum(float(m.get("percent", 0)) for m in milestones)
    if total > 100:
        raise ValueError("Tổng percent trong payment.yaml vượt quá 100")
    return data
