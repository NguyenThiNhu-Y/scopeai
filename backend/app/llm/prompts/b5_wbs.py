"""Prompt B5 — WBS 3 cấp (llm_pipeline.md §6).

Prompt tiếng Việt; LLM chỉ đề xuất cấu trúc + trọng số; TUYỆT ĐỐI cấm mọi
con số man-day/giá/ngày (BR-01). Dải effort do code truyền vào (LLM không bịa).

Truy vết requirement (thiet_ke_danh_gia.md §4): context chứa danh sách requirement
gọn (mã + 80 ký tự đầu + nhóm, tối đa 150 dòng); mỗi task lá ghi mã requirement
nó thực hiện; requirement chưa rõ thì để trống, không đoán.
"""

from __future__ import annotations


def _render_requirements(context: dict) -> str:
    lines = context.get("requirements") or []
    if not lines:
        return ""
    parts = ["Danh sách requirement (mã | nội dung tóm tắt | nhóm):"]
    parts.extend(f"- {line}" for line in lines[:150])
    parts.append(
        "\nYêu cầu truy vết: với mỗi task LÁ, ghi requirement_codes (tối đa 8 mã) "
        "là mã requirement mà task đó thực hiện. Requirement chưa rõ hoặc chưa đủ "
        "thông tin thì KHÔNG gán mã (để trống). Không bịa mã không có trong danh sách."
    )
    return "\n".join(parts)


def build_wbs_prompt(context: dict) -> str:
    base = """Bạn là chuyên gia lập kế hoạch dự án phần mềm. Hãy đề xuất WBS 3 cấp cho hồ sơ dự thầu.

Yêu cầu cấu trúc:
- Đúng 3 cấp: cấp 1 = nhóm (parent_code null), cấp 2 = task, cấp 3 = sub-task (task lá).
- Mỗi task có: task_code (mã nội bộ như WBS-001, WBS-001-01, WBS-001-01-01), name_vi (tiếng Việt), phase (poc/mvp/production), parent_code, depends_on (tối đa 5 mã, có thể rỗng).
- Task lá BẮT BUỘC có role (pm/ba/brse/ai_engineer/backend/frontend/qa/infra) và weight (số nguyên 1–100 — trọng số tương đối, KHÔNG phải man-day).
- Task nhóm (có con) KHÔNG được có role/weight.
- Mỗi giai đoạn poc/mvp/production phải có ÍT NHẤT 1 task lá role pm và 1 task lá role qa.
- depends_on không vòng, không tự tham chiếu.

TUYỆT ĐỐI KHÔNG đưa man_day, effort, price, cost, amount, date, schedule, midpoint, min, max hoặc bất kỳ con số nào khác ngoài weight. Mọi con số man-day/ngày do hệ thống tính sau.

Context hồ sơ (đã được che PII):
"""
    parts = [base]
    for key, value in context.items():
        if key in ("requirements", "requirements_data"):
            continue
        parts.append(f"- {key}: {value}")
    requirements_text = _render_requirements(context)
    if requirements_text:
        parts.append(requirements_text)
    return "\n".join(parts)