from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select
from sqlalchemy.orm import Session, object_session
from app.api.errors import state_conflict
from app.models import Bid, Quotation, ReferenceSnapshot, Schedule, WbsItem
from app.services.reference_service import load_rate_card

def calculate_quotation(
    session: Session,
    bid_id: int,
    contract_model="fixed_price",
    contingency_percent=None,
    onsite_percent=None,
    price_to_win_percent=0.0,
    tm_months=None,
    odc_fte=None,
    odc_months=None,
    tax_mode="tax_excluded",
    by="system",
) -> dict:
    bid = session.get(Bid, bid_id)
    if not bid: raise state_conflict("Không tìm thấy dữ liệu hồ sơ")
    items = session.execute(select(WbsItem).where(WbsItem.bid_id == bid_id)).scalars().all()
    if not items: raise state_conflict("Chưa có WBS — chưa thể tính báo giá")
    card = load_rate_card(session); rates = card["rates"]
    currency = bid.display_currency or ("JPY" if bid.customer_language == "ja" else "VND")
    fx = next((entry for entry in card["fx"] if entry["pair"] == f"VND/{currency}"), None)
    if fx is None:
        raise state_conflict(f"Rate card chưa có FX cho {currency}")
    fx_value = float(fx["value"])
    onsite_percent = float(
        onsite_percent
        if onsite_percent is not None
        else card.get("onsite_percent", 0.10 if bid.customer_language == "ja" else 0.0)
    )
    rounding_by_currency = card.get("rounding_by_currency") or {}
    unit = Decimal(str(rounding_by_currency.get(currency, card["rounding"]["unit"])))

    def round_currency(value: float) -> int | float:
        rounded = (Decimal(str(value)) / unit).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * unit
        return int(rounded) if unit >= 1 else float(rounded)

    groups = {}
    for item in items:
        if item.role and item.man_day is not None:
            role = item.role; md = float(item.man_day)
            offshore = float(rates[role]["offshore"]); onsite = float(rates[role]["onsite"])
            rate = (offshore * (1 - onsite_percent) + onsite * onsite_percent) * fx_value
            groups.setdefault(role, {"man_day": 0.0, "rate": rate, "onsite_percent": onsite_percent})["man_day"] += md
    groups = {r: {**v, "man_day": round(v["man_day"], 1), "amount": round_currency(v["man_day"] * v["rate"])} for r,v in groups.items()}
    base = sum(v["amount"] for v in groups.values())
    overhead = {"pm": 0, "brse": 0}
    if not any(i.role == "pm" and i.man_day for i in items):
        overhead["pm"] = round(base * float(card["overhead"]["pm"]))
    if bid.customer_language == "ja" and not any(i.role == "brse" and i.man_day for i in items):
        overhead["brse"] = round(base * float(card["overhead"]["brse"]))
    subtotal = base + sum(overhead.values())
    default_contingency = card["contingency"].get(contract_model, card["contingency"].get("fixed_price", 0))
    pct = float(contingency_percent if contingency_percent is not None else default_contingency) * (1 if (contingency_percent is not None and contingency_percent > 1) else 100)
    contingency = round_currency(subtotal * pct / 100)
    tax_excluded = subtotal + contingency + float(card.get("operating_cost", 0))
    tax_percent = float(card.get("tax_percent", 0))
    if tax_mode == "tax_included":
        # Giá đã gồm thuế: tổng hiển thị không cộng thêm dòng thuế.
        tax_included = round_currency(tax_excluded)
    else:
        tax_included = round_currency(tax_excluded * (1 + tax_percent / 100))
    tax_amount = round_currency(tax_included - tax_excluded)
    raw_grand = round_currency(tax_excluded)
    adjustment = float(price_to_win_percent or 0)
    grand = round_currency(raw_grand * (1 + adjustment / 100))
    payment_plan = []
    if contract_model == "tm":
        months = int(tm_months or 1)
        monthly_amount = round_currency(grand / months)
        payment_plan = [{"name": f"T&M tháng {month}", "percent": round(100 / months, 2), "month": month, "amount": monthly_amount} for month in range(1, months + 1)]
    elif contract_model == "odc":
        months = int(odc_months or 1)
        fte = float(odc_fte or 1)
        fte_months = round(fte * months, 2)
        monthly_amount = round_currency(grand / months)
        payment_plan = [{"name": f"ODC tháng {month}", "percent": round(100 / months, 2), "month": month, "fte": fte, "fte_months": fte_months, "amount": monthly_amount} for month in range(1, months + 1)]
    snap = ReferenceSnapshot(bid_id=bid_id, payload=card); session.add(snap); session.flush()
    by_phase = {}
    phase_man_days = {}
    phase_raw = {}
    for phase in ("poc", "mvp", "production"):
        phase_man_days[phase] = round(
            sum(float(i.man_day or 0) for i in items if i.phase == phase), 1
        )
        phase_amount = sum(
            v["amount"] * float(i.man_day or 0) / max(v["man_day"], 1)
            for role, v in groups.items()
            for i in items
            if i.phase == phase and i.role == role
        )
        if phase_amount:
            phase_raw[phase] = phase_amount / base * (base + sum(overhead.values()) + contingency)
    if phase_raw:
        ordered = list(phase_raw)
        rounded = {phase: round_currency(value) for phase, value in phase_raw.items()}
        remainder = grand - sum(rounded.values())
        rounded[ordered[-1]] += remainder
        by_phase = rounded
    totals = {"by_role": groups, "by_phase": by_phase, "phase_man_days": phase_man_days, "overhead": overhead, "onsite_percent": onsite_percent, "contingency_amount": contingency, "operating_cost": card.get("operating_cost",0), "subtotal": subtotal, "tax_excluded": tax_excluded, "tax_included": tax_included, "tax_amount": tax_amount, "tax_percent": tax_percent, "grand_total": grand, "pre_adjustment_total": raw_grand, "payment_plan": payment_plan, "odc_fte_months": round(float(odc_fte or 0) * int(odc_months or 0), 2) if contract_model == "odc" else None}
    row = Quotation(bid_id=bid_id, contract_model=contract_model, contingency_percent=pct, onsite_percent=onsite_percent, price_to_win_percent=adjustment, tm_months=tm_months, odc_fte=odc_fte, odc_months=odc_months, fx_rate_value=fx_value, fx_rate_date=date.fromisoformat(fx["date"]), totals=totals, valid_until=date.today()+timedelta(days=int(card.get("validity_days",30))), tax_mode=tax_mode, reference_snapshot_id=snap.id, rounding_note=f"round_half_up({unit}) {currency}", computed_by=by)
    session.add(row); session.commit(); session.refresh(row)
    return quotation_to_out(row, bid)

def quotation_to_out(row, bid):
    currency = bid.display_currency or "VND"
    budget = None
    budget_value = None
    scope = "total"
    comparison_total = None
    if bid.budget_amount is not None:
        budget_currency = bid.budget_currency or currency
        budget_value = float(bid.budget_amount)
        if budget_currency != currency:
            from app.services.reference_service import load_rate_card
            card = load_rate_card()
            fx = next((x for x in card["fx"] if x["pair"] == f"VND/{budget_currency}"), None)
            target = next((x for x in card["fx"] if x["pair"] == f"VND/{currency}"), None)
            if fx is not None and target is not None:
                budget_value = budget_value / float(fx["value"]) * float(target["value"])
        scope = getattr(bid, "budget_scope", None) or "total"
        comparison_total = float(row.totals["grand_total"])
        if scope == "poc":
            # Ngân sách chỉ cho PoC (vd "PoC：1,500万円以内") → đối chiếu giá PoC.
            comparison_total = float(
                ((row.totals.get("by_phase") or {}).get("poc")) or comparison_total
            )
        difference = round(comparison_total - budget_value, 2)
        budget = {"amount": bid.budget_amount, "currency": budget_currency, "difference": difference}
    snapshot_version = 1
    if row.reference_snapshot_id:
        from app.models import ReferenceSnapshot
        session = object_session(row)
        snapshot = session.get(ReferenceSnapshot, row.reference_snapshot_id) if session else None
        snapshot_version = (snapshot.payload or {}).get("version", 1) if snapshot else 1
    session = object_session(row)
    schedule = session.execute(select(Schedule).where(Schedule.bid_id == bid.id).order_by(Schedule.id.desc())).scalars().first() if session else None
    if budget is not None:
        budget["scope"] = "poc" if scope == "poc" else "bid_budget"
        budget["scope_label_vi"] = "Ngân sách PoC" if scope == "poc" else "Ngân sách khách"
        budget["difference_percent"] = (
            round(budget["difference"] / float(budget_value) * 100, 2)
            if budget_value
            else None
        )
        pre_adjustment = comparison_total
        raw_suggestion = (
            round((float(budget_value) / float(pre_adjustment) - 1) * 100, 2)
            if isinstance(budget_value, (int, float))
            and isinstance(pre_adjustment, (int, float))
            and pre_adjustment
            else None
        )
        budget["adjustment_suggestion_percent"] = max(-30.0, min(30.0, raw_suggestion)) if raw_suggestion is not None else None
        budget["scope_check_required"] = bool(budget["difference_percent"] is not None and abs(budget["difference_percent"]) > 30)
        budget["warning"] = "Giá lệch ngân sách quá ±30%: kiểm tra lại phạm vi/effort" if budget["scope_check_required"] else None
    return {"contract_model": row.contract_model, "contingency_percent": row.contingency_percent, "price_to_win_percent": row.price_to_win_percent, "fx_rate": {"value": row.fx_rate_value, "date": row.fx_rate_date, "pair": f"VND/{currency}"}, "currency": currency, "valid_until": row.valid_until, "tax_mode": row.tax_mode, "totals": row.totals, "budget": budget, "payment_milestones": (schedule.payment_milestones if schedule and schedule.payment_milestones else []), "trace": {"formula": "Σ(man_day × blended_rate) + conditional overhead + contingency, then code-only price adjustment", "rate_card_version": snapshot_version, "reference_snapshot_id": row.reference_snapshot_id, "rounding": row.rounding_note}}
