from __future__ import annotations

from pathlib import Path
import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.errors import validation_error
from app.models import Bid, Changelog, ReferenceSetting
from app.services.reference_service import ROOT, load_effort, load_factors, load_rate_card

FILES = {"effort": "effort.yaml", "rate_card": "rate_card.yaml", "factors": "factors.yaml"}
OPTIONAL_DEFAULTS = {
    "company": {"company_name": "Công ty Mẫu Presales", "logo_filename": None, "filename_rule": "{customer}_{project}_{version}"},
    "templates": {"word": {"source": "builtin", "filename": "proposal-default.docx", "valid": True}, "excel": {"source": "builtin", "filename": "quotation-default.xlsx", "valid": True}, "powerpoint": {"source": "builtin", "filename": "proposal-default.pptx", "valid": True}},
    "standard_content": {"vi": {"company_intro": "Giới thiệu công ty mẫu", "security": "Bảo mật theo thỏa thuận", "terms": "Điều khoản mẫu"}, "en": {"company_intro": "Fictional company introduction", "security": "Security subject to agreement", "terms": "Sample terms"}, "ja": {"company_intro": "サンプル会社の紹介", "security": "合意に基づくセキュリティ", "terms": "サンプル条件"}},
    "case_studies": [{"title": "Cổng dữ liệu mẫu", "industry": "Bán lẻ", "summary": "Case study giả lập, không chỉ tên khách hàng thật"}],
    "bid_no_bid": {"criteria": [{"id": "strategic_fit", "label_vi": "Phù hợp chiến lược", "weight": 30}, {"id": "delivery_feasibility", "label_vi": "Khả năng triển khai", "weight": 40}, {"id": "commercial_fit", "label_vi": "Phù hợp thương mại", "weight": 30}]},
}


def _repo_payload(key: str) -> dict:
    if key in OPTIONAL_DEFAULTS:
        return OPTIONAL_DEFAULTS[key]
    with (ROOT / "reference" / FILES[key]).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _validate(key: str, payload: object) -> dict | list:
    if key == "case_studies":
        if not isinstance(payload, list):
            raise validation_error("Case study phải là YAML dạng danh sách", {"errors": ["root"]})
        return payload
    if not isinstance(payload, dict):
        raise validation_error("Bảng chuẩn phải là YAML dạng object", {"errors": ["root"]})
    errors: list[str] = []
    if key in OPTIONAL_DEFAULTS:
        if key == "bid_no_bid":
            criteria = payload.get("criteria") if isinstance(payload, dict) else None
            if not isinstance(criteria, list) or not criteria or abs(sum(float(item.get("weight", 0)) for item in criteria) - 100) > 0.001:
                errors.append("Tiêu chí Bid/No-bid phải có danh sách và tổng trọng số bằng 100")
        elif key == "templates":
            for kind in ("word", "excel", "powerpoint"):
                item = payload.get(kind) if isinstance(payload, dict) else None
                if not isinstance(item, dict) or item.get("valid") is not True:
                    errors.append(f"Template {kind} chưa được kiểm tra hợp lệ")
    elif key == "effort":
        directions = payload.get("directions")
        expected = {"none", "traditional_ml", "rag", "agent", "fine_tune"}
        if not isinstance(directions, dict) or set(directions) != expected:
            errors.append("Thiếu tổ hợp hướng giải pháp")
        else:
            for direction, phases in directions.items():
                if not isinstance(phases, dict) or set(phases) != {"poc", "mvp", "production"}:
                    errors.append(f"{direction}: thiếu phase")
                    continue
                for phase, value in phases.items():
                    if not isinstance(value, dict) or value.get("min") is None or value.get("max") is None or value["min"] < 0 or value["min"] > value["max"]:
                        errors.append(f"{direction}.{phase}: min/max không hợp lệ")
    elif key == "rate_card":
        rates = payload.get("rates")
        roles = {"pm", "ba", "brse", "ai_engineer", "backend", "frontend", "qa", "infra"}
        if not isinstance(rates, dict) or set(rates) != roles:
            errors.append("Rate card phải có đủ vai trò")
        else:
            for role, rate in rates.items():
                if not isinstance(rate, dict) or any(float(rate.get(place, 0)) <= 0 for place in ("offshore", "onsite")):
                    errors.append(f"{role}: phải có đơn giá offshore/onsite dương")
    elif key == "factors" and float(payload.get("factor_cap", 0)) <= 1:
        errors.append("Trần hệ số phải lớn hơn 1")
    if errors:
        raise validation_error("Bảng chuẩn không hợp lệ, giá trị cũ vẫn được giữ nguyên", {"errors": errors})
    return payload


def list_settings(session: Session) -> list[dict]:
    result = []
    for key, filename in {**FILES, **{key: "" for key in OPTIONAL_DEFAULTS}}.items():
        row = session.get(ReferenceSetting, key)
        payload = row.payload if row else _repo_payload(key)
        default_version = payload.get("version", 1) if isinstance(payload, dict) else 1
        result.append({"key": key, "source": "db" if row else "repo", "version": row.version if row else default_version, "updated_by": row.updated_by if row else None, "updated_at": row.updated_at if row else None, "yaml_preview": yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), "payload": payload})
    return result


def update_setting(session: Session, key: str, yaml_content: str, by: str) -> dict:
    if key not in {**FILES, **OPTIONAL_DEFAULTS}:
        raise validation_error("Loại bảng chuẩn không được hỗ trợ")
    try:
        payload = _validate(key, yaml.safe_load(yaml_content))
    except yaml.YAMLError as exc:
        raise validation_error("YAML không hợp lệ, hãy kiểm tra thụt dòng và dấu ngoặc", {"errors": [str(exc)]}) from exc
    row = session.get(ReferenceSetting, key)
    version = (row.version if row else int(payload.get("version", 1) if isinstance(payload, dict) else 1)) + 1
    if row:
        row.version, row.payload, row.updated_by = version, payload, by
    else:
        session.add(ReferenceSetting(key=key, version=version, payload=payload, updated_by=by))
    # A settings audit has no bid; attach it to the latest bid when available.
    bid = session.scalar(select(Bid).order_by(Bid.id.desc()))
    if bid is not None:
        session.add(Changelog(bid_id=bid.id, actor=by, action="update_reference", field_changed=key, note=f"Bảng {key} phiên bản {version}"))
    session.commit()
    return {"key": key, "version": version, "source": "db"}
