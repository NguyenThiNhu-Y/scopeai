from __future__ import annotations

from app.services.factor_engine import calculate_factors
from app.services.reference_service import load_effort


def calculate_effort(bid, direction: str, session=None) -> dict:
    table = load_effort(session)
    factor = calculate_factors(bid, session)
    multiplier = factor["product"]
    digits = int(table.get("rounding_digits", 1))
    by_phase = {}
    midpoint_total = 0.0
    for phase, values in table["directions"][direction].items():
        low = round(values["min"] * multiplier, digits)
        high = round(values["max"] * multiplier, digits)
        by_phase[phase] = {"min": low, "max": high}
        midpoint_total += (low + high) / 2
    midpoint_total = round(midpoint_total, digits)
    return {
        "direction": direction, "factors": factor["factors"], "factor_product": multiplier,
        "cap": factor["cap"], "by_phase": by_phase, "midpoint_total": midpoint_total,
         "trace": {"table_version": table["version"], "source": "reference/effort.yaml + context hồ sơ",
                   "formula": "Σ midpoint(min,max) × factor_product",
                   "raw_factor_product": factor["raw"], "capped_factor_product": multiplier},
    }
