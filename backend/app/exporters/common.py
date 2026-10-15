"""Shared labels and deterministic helpers for docx/xlsx/pptx exporters."""

from __future__ import annotations

from datetime import date, timedelta

PRICE_PLACEHOLDER = "[Presales điền]"
PHASES = ("poc", "mvp", "production")

LABELS: dict[str, dict[str, str]] = {
    "vi": {
        "proposal": "Đề xuất giải pháp", "toc": "Mục lục", "toc_hint": "Nhấn chuột phải → Cập nhật trường để làm mới mục lục.",
        "introduction": "Giới thiệu", "requirements_understanding": "Hiểu yêu cầu", "solution_overview": "Tổng quan đề xuất",
        "approach": "Cách triển khai", "schedule": "Lịch trình", "team": "Đội ngũ", "assumptions_and_scope": "Giả định và ngoài phạm vi",
        "risks": "Rủi ro", "conclusion": "Kết luận", "assumptions": "Giả định", "scope_out": "Ngoài phạm vi",
        "quotation": "Báo giá", "customer_suffix": "", "customer_prefix": "Kính gửi: ", "date": "Ngày", "prepared_by": "Đơn vị đề xuất",
        "page": "Trang", "wbs_appendix": "Phụ lục A. WBS và effort", "schedule_appendix": "Phụ lục B. Lịch tổng thể",
        "task_code": "Mã", "task_name": "Công việc", "phase": "Giai đoạn", "role": "Vai trò", "man_day": "Man-day",
        "total": "Tổng", "start": "Bắt đầu", "end": "Kết thúc", "payment_milestones": "Mốc thanh toán", "milestone": "Mốc",
        "percent": "Tỷ lệ", "due_date": "Ngày dự kiến", "item": "Hạng mục", "amount": "Thành tiền", "currency": "Tiền tệ",
        "contract_model": "Hình thức hợp đồng", "valid_until": "Hiệu lực báo giá đến", "tax_excluded": "Giá chưa bao gồm thuế",
        "tax_included": "Giá đã bao gồm thuế", "effort_summary": "Tổng hợp effort", "gantt": "Lịch triển khai", "agenda": "Nội dung",
        "by_phase": "Báo giá theo giai đoạn", "customer_deadline": "Hạn khách yêu cầu", "price_pending": "Giá sẽ được gửi sau khi phê duyệt nội bộ.",
        "no_schedule": "Chưa có lịch.", "continued": "(tiếp)",
    },
    "en": {
        "proposal": "Solution Proposal", "toc": "Table of contents", "toc_hint": "Right-click → Update field to refresh the table of contents.",
        "introduction": "Introduction", "requirements_understanding": "Requirements understanding", "solution_overview": "Solution overview",
        "approach": "Approach", "schedule": "Schedule", "team": "Team", "assumptions_and_scope": "Assumptions and out of scope",
        "risks": "Risks", "conclusion": "Conclusion", "assumptions": "Assumptions", "scope_out": "Out of scope",
        "quotation": "Quotation", "customer_suffix": "", "customer_prefix": "To: ", "date": "Date", "prepared_by": "Prepared by",
        "page": "Page", "wbs_appendix": "Appendix A. WBS and effort", "schedule_appendix": "Appendix B. Master schedule",
        "task_code": "Code", "task_name": "Task", "phase": "Phase", "role": "Role", "man_day": "Man-days",
        "total": "Total", "start": "Start", "end": "End", "payment_milestones": "Payment milestones", "milestone": "Milestone",
        "percent": "Share", "due_date": "Planned date", "item": "Item", "amount": "Amount", "currency": "Currency",
        "contract_model": "Contract model", "valid_until": "Valid until", "tax_excluded": "Prices exclude tax",
        "tax_included": "Prices include tax", "effort_summary": "Effort summary", "gantt": "Delivery schedule", "agenda": "Agenda",
        "by_phase": "Price by phase", "customer_deadline": "Customer deadline", "price_pending": "Pricing will be provided after internal approval.",
        "no_schedule": "Schedule not available.", "continued": "(cont.)",
    },
    "ja": {
        "proposal": "ご提案書", "toc": "目次", "toc_hint": "右クリック →「フィールド更新」で目次を更新できます。",
        "introduction": "はじめに", "requirements_understanding": "ご要件の理解", "solution_overview": "提案概要",
        "approach": "進め方", "schedule": "スケジュール", "team": "体制", "assumptions_and_scope": "前提条件・対象外",
        "risks": "リスク", "conclusion": "おわりに", "assumptions": "前提条件", "scope_out": "スコープ外",
        "quotation": "お見積り", "customer_suffix": " 御中", "customer_prefix": "", "date": "日付", "prepared_by": "提案者",
        "page": "ページ", "wbs_appendix": "別紙A. WBS・工数", "schedule_appendix": "別紙B. マスタースケジュール",
        "task_code": "コード", "task_name": "作業項目", "phase": "フェーズ", "role": "役割", "man_day": "人日",
        "total": "合計", "start": "開始", "end": "終了", "payment_milestones": "支払マイルストーン", "milestone": "マイルストーン",
        "percent": "割合", "due_date": "予定日", "item": "項目", "amount": "金額", "currency": "通貨",
        "contract_model": "契約形態", "valid_until": "見積有効期限", "tax_excluded": "金額は税抜です",
        "tax_included": "金額は税込です", "effort_summary": "工数サマリー", "gantt": "実施スケジュール", "agenda": "アジェンダ",
        "by_phase": "フェーズ別お見積り", "customer_deadline": "ご希望期限", "price_pending": "金額は社内承認後にご提示いたします。",
        "no_schedule": "スケジュール未作成", "continued": "（続き）",
    },
}

PHASE_LABELS = {
    "vi": {"poc": "PoC", "mvp": "MVP", "production": "Production"},
    "en": {"poc": "PoC", "mvp": "MVP", "production": "Production"},
    "ja": {"poc": "PoC", "mvp": "MVP", "production": "本番"},
}
ROLE_LABELS = {
    "pm": "PM", "ba": "BA", "brse": "BrSE", "ai_engineer": "AI Engineer", "backend": "Backend",
    "frontend": "Frontend", "qa": "QA", "infra": "Infra",
}
CONTRACT_LABELS = {
    "vi": {"fixed_price": "Trọn gói", "tm": "Theo thời gian (T&M)", "odc": "ODC"},
    "en": {"fixed_price": "Fixed price", "tm": "Time & Material", "odc": "ODC"},
    "ja": {"fixed_price": "一括請負", "tm": "準委任（T&M）", "odc": "ODC（ラボ型）"},
}


def labels_for(language: str | None, overrides: dict | None = None) -> dict[str, str]:
    return {**LABELS.get(language or "vi", LABELS["vi"]), **(overrides or {})}


def phase_label(phase: str | None, language: str | None) -> str:
    return PHASE_LABELS.get(language or "vi", PHASE_LABELS["vi"]).get(phase or "", phase or "")


def role_label(role: str | None) -> str:
    return ROLE_LABELS.get(role or "", role or "")


def money_decimals(currency: str | None) -> int:
    return 2 if currency == "USD" else 0


def format_money(amount, currency: str | None) -> str:
    if amount is None:
        return PRICE_PLACEHOLDER
    return f"{float(amount):,.{money_decimals(currency)}f} {currency or ''}".strip()


def as_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def wbs_rows(items) -> list[tuple[object, int, bool]]:
    """Return (item, level, is_parent) preserving the given order."""
    by_code = {item.task_code: item for item in items}
    parents = {getattr(item, "parent_code", None) for item in items}

    def level(item, depth=0) -> int:
        parent = getattr(item, "parent_code", None)
        if not parent or parent not in by_code or depth > 10:
            return 1
        return 1 + level(by_code[parent], depth + 1)

    return [(item, level(item), item.task_code in parents) for item in items]


def leaf_man_days(items) -> float:
    return round(sum(float(item.man_day or 0) for item, _, is_parent in wbs_rows(items) if not is_parent), 1)


def phase_summary(tasks: list[dict]) -> list[dict]:
    """Per-phase start/end/man-day from code-computed schedule tasks."""
    out = []
    for phase in PHASES:
        rows = [t for t in tasks if t.get("phase") == phase and as_date(t.get("start_date")) and as_date(t.get("end_date"))]
        if rows:
            out.append({
                "phase": phase,
                "start": min(as_date(t["start_date"]) for t in rows),
                "end": max(as_date(t["end_date"]) for t in rows),
                "man_day": round(sum(float(t.get("man_day") or 0) for t in rows), 1),
            })
    return out


def week_starts(first: date, last: date, limit: int = 104) -> list[date]:
    start = first - timedelta(days=first.weekday())
    weeks = []
    while start <= last and len(weeks) < limit:
        weeks.append(start)
        start += timedelta(days=7)
    return weeks
