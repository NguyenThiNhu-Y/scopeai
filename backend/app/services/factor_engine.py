from __future__ import annotations

from app.services.reference_service import load_factors


def applicable_factors(bid, intake: dict | None = None, requirement_count: int | None = None) -> list[str]:
    intake = intake or {}
    constraints = " ".join(str(x) for x in intake.get("constraints_vi", []))
    data = str(intake.get("data_vi", ""))
    keys: list[str] = []
    if bid.customer_language == "ja": keys.append("customer_jp")
    if bid.data_readiness == "low" or bid.no_requirement_file: keys.append("data_not_ready")
    # Hồ sơ cũ chưa có intake_context vẫn cần tính đúng các hệ số từ nội dung
    # đã lưu. Đây chỉ là fallback tương thích; khi đã có intake thì chỉ dùng
    # kết quả phân tích có cấu trúc, không dò email thô.
    combined = f"{constraints} {data}".lower()
    if not intake:
        combined = f"{combined} {getattr(bid, 'request_content', '')}".lower()
    if any(word in combined for word in ("on-premise", "on premise", "オンプレ")): keys.append("on_premise")
    if any(word in combined for word in ("compliance", "tuân thủ", "認証")): keys.append("strict_compliance")
    if any(word in combined for word in ("multi", "đa ngôn ngữ", "多言語")): keys.append("multilingual")
    if any(word in combined for word in ("ocr", "scan", "スキャン")): keys.append("ocr")
    if any(word in combined for word in ("million", "triệu", "lớn", "100万")): keys.append("large_data")
    # Chỉ bật khi có count thực tế từ parser/DB; không đoán từ nội dung email.
    if requirement_count is not None and requirement_count >= 30:
        keys.append("many_requirements")
    return list(dict.fromkeys(keys))


def calculate_factors(bid, session=None) -> dict:
    config = load_factors(session)
    intake = getattr(bid, "intake_context", None) or {}
    requirement_count = getattr(bid, "requirement_count", None)
    if session is not None and requirement_count is None and hasattr(session, "query"):
        from app.models import Requirement
        requirement_count = session.query(Requirement).filter_by(bid_id=bid.id).count()
    applied = []
    raw = 1.0
    for key in applicable_factors(bid, intake, requirement_count):
        item = config["factors"][key]
        raw *= float(item["value"])
        applied.append({"key": key, "value": float(item["value"]), "reason": item["reason"]})
    cap = float(config["factor_cap"])
    return {"factors": applied, "raw": raw, "product": min(raw, cap), "cap": cap}
