"""Prompt B5 — WBS 3 cấp (llm_pipeline.md §6).

Prompt tiếng Việt; LLM chỉ đề xuất cấu trúc + trọng số; TUYỆT ĐỐI cấm mọi
con số man-day/giá/ngày (BR-01). Dải effort do code truyền vào (LLM không bịa).
"""

from __future__ import annotations


def build_wbs_prompt(context: dict) -> str:
    return """Bạn là chuyên gia lập kế hoạch dự án phần mềm. Hãy đề xuất WBS 3 cấp cho hồ sơ dự thầu.

Yêu cầu cấu trúc:
- Đúng 3 cấp: cấp 1 = nhóm (parent_code null), cấp 2 = task, cấp 3 = sub-task (task lá).
- Mỗi task có: task_code (mã nội bộ như WBS-001, WBS-001-01, WBS-001-01-01), name_vi (tiếng Việt), phase (poc/mvp/production), parent_code, depends_on (tối đa 5 mã, có thể rỗng).
- Task lá BẮT BUỘC có role (pm/ba/brse/ai_engineer/backend/frontend/qa/infra) và weight (số nguyên 1–100 — trọng số tương đối, KHÔNG phải man-day).
- Task nhóm (có con) KHÔNG được có role/weight.
- Mỗi giai đoạn poc/mvp/production phải có ÍT NHẤT 1 task lá role pm và 1 task lá role qa.
- depends_on không vòng, không tự tham chiếu.

TUYỆT ĐỐI KHÔNG đưa man_day, effort, price, cost, amount, date, schedule, midpoint, min, max hoặc bất kỳ con số nào khác ngoài weight. Mọi con số man-day/ngày do hệ thống tính sau.

Context hồ sơ (đã được che PII):\n""" + str(context)