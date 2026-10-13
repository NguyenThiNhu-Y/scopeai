"""CheckEngine — kiểm tra ngữ nghĩa WBS (spec §3.2, contract §8.1).

Các cờ: pm_qa_ok (mỗi phase ≥ 1 lá PM + ≥ 1 lá QA), within_20pct (so midpoint),
cycle_free (DFS trên depends_on), leaf_within_limit (lá man_day ≤ 10).
Lỗi ngữ nghĩa → retry ≤ 2 → cảnh báo (không chặn pipeline).
"""

from __future__ import annotations

from app.services.wbs_engine import PHASES, leaf_items


def pm_qa_ok(items: list[dict]) -> bool:
    """Mỗi phase (poc/mvp/production) có ≥ 1 lá role pm và ≥ 1 lá role qa."""
    leaves = leaf_items(items)
    for phase in PHASES:
        phase_leaves = [i for i in leaves if i["phase"] == phase]
        if not any(i["role"] == "pm" for i in phase_leaves):
            return False
        if not any(i["role"] == "qa" for i in phase_leaves):
            return False
    return True


def within_20pct(total: float, midpoint: float) -> bool:
    if midpoint <= 0:
        return True
    return abs(total - midpoint) / midpoint <= 0.20


def cycle_free(items: list[dict]) -> bool:
    """Không vòng phụ thuộc — DFS trên ``depends_on`` (không kể tự tham chiếu)."""
    by_code = {i["task_code"]: i for i in items}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(code: str) -> bool:
        if code in visited:
            return True
        if code in visiting:
            return False
        visiting.add(code)
        for dep in by_code[code].get("depends_on") or []:
            if dep in by_code and not visit(dep):
                return False
        visiting.remove(code)
        visited.add(code)
        return True

    return all(visit(code) for code in by_code)


def leaf_within_limit(items: list[dict], limit: float = 10.0) -> bool:
    leaves = leaf_items(items)
    return all((i.get("man_day") or 0) <= limit for i in leaves)


def leaf_max_man_day(items: list[dict]) -> float:
    leaves = leaf_items(items)
    return max((i.get("man_day") or 0.0) for i in leaves) if leaves else 0.0


def check_wbs(
    items: list[dict], midpoint: float, by_phase: dict[str, dict] | None = None
) -> dict:
    """Tính toàn bộ check §8.1 — trả dict khớp ``WbsCheckOut``."""
    total = round(sum(i.get("man_day") or 0.0 for i in leaf_items(items)), 1)
    deviation = (
        round(abs(total - midpoint) / midpoint * 100, 1) if midpoint else 0.0
    )
    pm_qa = pm_qa_ok(items)
    cycle = cycle_free(items)
    leaf_limit = leaf_within_limit(items)
    leaf_max = leaf_max_man_day(items)
    within = within_20pct(total, midpoint)

    warnings: list[str] = []
    if not within:
        warnings.append(
            f"Tổng effort lệch {deviation}% so với midpoint ({total} vs {midpoint}) — cần ghi chú override"
        )
    if not pm_qa:
        warnings.append("Thiếu task PM hoặc QA ở một giai đoạn (poc/mvp/production)")
    if not cycle:
        warnings.append("Phụ thuộc task có vòng lặp")
    if not leaf_limit:
        warnings.append(f"Task lá vượt quá 10 man-day (lớn nhất {leaf_max})")

    return {
        "midpoint": round(midpoint, 1),
        "deviation_pct": deviation,
        "within_20pct": within,
        "pm_qa_ok": pm_qa,
        "cycle_free": cycle,
        "leaf_max_man_day": leaf_max,
        "leaf_within_limit": leaf_limit,
        "warning": "; ".join(warnings) if warnings else None,
    }


def semantic_issues(check: dict) -> list[str]:
    """Danh sách lỗi ngữ nghĩa (rỗng = WBS hợp lệ) — dùng cho retry B5."""
    issues: list[str] = []
    if not check["pm_qa_ok"]:
        issues.append("thiếu PM/QA")
    if not check["within_20pct"]:
        issues.append("lệch ±20%")
    if not check["cycle_free"]:
        issues.append("vòng phụ thuộc")
    # leaf_within_limit là cảnh báo về phân bổ/reference range, không phải
    # lỗi khiến B5 gọi lại LLM: LLM không được sinh man-day và không thể tự
    # sửa con số do code phân bổ.
    return issues
