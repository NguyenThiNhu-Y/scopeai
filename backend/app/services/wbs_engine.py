"""WbsEngine — dựng cây WBS 3 cấp và gán man-day cho task lá (BR-01, ADR-006).

LLM chỉ đề xuất cấu trúc + trọng số; man-day do CODE tính:
    man_day(lá) = round(target_phase × weight_i / Σweight_phase, 1)
với target_phase = midpoint(dải effort sau hệ số). Cân bằng sai số làm tròn
vào lá lớn nhất để tổng phase khớp target. Nhóm/task cha = Σ con (tính khi trả
response). Engines KHÔNG import gateway LLM (spec §3.2).
"""

from __future__ import annotations

from collections import defaultdict

PHASES = ["poc", "mvp", "production"]


def assign_man_days(tasks: list[dict], by_phase: dict[str, dict]) -> list[dict]:
    """Gán ``man_day`` cho từng task lá theo midpoint phase × trọng số chuẩn hóa.

    Args:
        tasks: list dict từ ``WbsStructure`` (task_code, phase, weight, ...).
        by_phase: ``{phase: {"min": float, "max": float}}`` — dải effort sau hệ số.

    Returns:
        tasks với ``man_day`` đã gán trên lá (nhóm giữ ``man_day=None``).
    """
    leaves_by_phase: dict[str, list[dict]] = defaultdict(list)
    for task in tasks:
        if task.get("role") is not None:  # lá = có role (schema đã ép)
            leaves_by_phase[task["phase"]].append(task)

    for phase, leaves in leaves_by_phase.items():
        target = (by_phase[phase]["min"] + by_phase[phase]["max"]) / 2.0
        total_weight = sum(int(t.get("weight") or 0) for t in leaves)
        if total_weight <= 0:
            # Phòng thủ: chia đều (không nên xảy ra vì schema bắt weight trên lá).
            share = round(target / len(leaves), 1)
            for t in leaves:
                t["man_day"] = share
            continue

        raw = [target * int(t.get("weight") or 0) / total_weight for t in leaves]
        rounded = [round(v, 1) for v in raw]
        diff = round(target - sum(rounded), 1)
        if diff != 0:
            # Cân bằng sai số làm tròn vào lá lớn nhất (theo weight).
            idx = max(range(len(leaves)), key=lambda i: int(leaves[i].get("weight") or 0))
            adjusted = round(rounded[idx] + diff, 1)
            rounded[idx] = max(adjusted, 0.0)
        for task, md in zip(leaves, rounded):
            task["man_day"] = md
    return tasks


def enrich_items(tasks: list[dict]) -> list[dict]:
    """Tính ``level``, ``is_leaf`` và ``man_day`` nhóm/task cha = Σ con.

    Trả về list dict mới (không sửa input) — mỗi item có đủ trường response §8.1.
    """
    by_code = {t["task_code"]: t for t in tasks}
    children: dict[str, list[str]] = defaultdict(list)
    for t in tasks:
        if t.get("parent_code"):
            children[t["parent_code"]].append(t["task_code"])

    def depth_of(code: str) -> int:
        parent = by_code[code].get("parent_code")
        if not parent:
            return 1
        return depth_of(parent) + 1

    def man_day_of(code: str) -> float:
        task = by_code[code]
        if task.get("man_day") is not None:
            return float(task["man_day"])
        kids = children.get(code, [])
        if not kids:
            return 0.0
        return round(sum(man_day_of(k) for k in kids), 1)

    out: list[dict] = []
    for t in tasks:
        code = t["task_code"]
        leaf = code not in children
        item = {
            "task_code": code,
            "name_vi": t["name_vi"],
            "phase": t["phase"],
            "parent_code": t.get("parent_code"),
            "level": depth_of(code),
            "role": t.get("role"),
            "weight": t.get("weight"),
            "man_day": float(t["man_day"]) if t.get("man_day") is not None else None,
            "depends_on": list(t.get("depends_on") or []),
            "sort_order": int(t.get("sort_order") or 0),
            "is_leaf": leaf,
        }
        if not leaf:
            item["man_day"] = man_day_of(code)
        out.append(item)
    return out


def leaf_items(items: list[dict]) -> list[dict]:
    return [i for i in items if i["is_leaf"]]