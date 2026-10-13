"""Prompt builder cho bước B1 — Intake (llm_pipeline.md §2)."""

from __future__ import annotations

import json


def build_intake_prompt(
    request_content_masked: str,
    customer_language: str,
    rfp_files: list[dict] | None = None,
    requirements: list[dict] | None = None,
    requirement_count: int = 0,
) -> str:
    """Dựng prompt tiếng Việt cho bước trích xuất thông tin (B1).

    - Text đầu vào ĐÃ được che PII (BR-06) — điểm chặn nằm ở gateway.
    - Dặn BR-01: KHÔNG xuất con số/ngày — ngân sách/thời hạn là ghi chú văn bản.
    """
    files_text = json.dumps(rfp_files or [], ensure_ascii=False, indent=2)
    requirements_text = json.dumps(requirements or [], ensure_ascii=False, indent=2)
    return f"""Bạn là trợ lý presales (chuyên viên chào thầu) của một công ty phần mềm.
Hãy đọc nội dung yêu cầu của khách hàng bên dưới (đã được che thông tin cá nhân) và trích xuất thông tin theo JSON đúng schema.

NHIỆM VỤ — trích xuất 7 nhóm thông tin:
1. objectives_vi — mục tiêu dự án (tiếng Việt, ≤ 300 từ)
2. users_vi — người dùng / đối tượng sử dụng (tiếng Việt, ≤ 200 từ)
3. data_vi — dữ liệu liên quan (tiếng Việt, ≤ 200 từ)
4. constraints_vi — ràng buộc (tối đa 5 mục)
5. budget_mentioned + budget_note_vi — nội dung có đề cập ngân sách không; nếu có, ghi chú bằng TIẾNG VIỆT (≤ 100 từ)
6. deadline_mentioned + deadline_note_vi — nội dung có đề cập thời hạn không; nếu có, ghi chú bằng TIẾNG VIỆT (≤ 100 từ)
7. customer_schedule_note_vi — trích nguyên ý mốc lịch khách nêu, không tự tính hoặc suy diễn
8. customer_language_detected — ngôn ngữ chính của nội dung (vi | en | ja | unknown)

QUY TẮC BẮT BUỘC (BR-01):
- TUYỆT ĐỐI KHÔNG xuất ra con số man-day, giá tiền, tỷ giá, hoặc ngày lịch cụ thể.
- Ngân sách / thời hạn chỉ mô tả bằng VĂN BẢN tiếng Việt trong budget_note_vi / deadline_note_vi.
- Nếu nội dung không đề cập ngân sách/thời hạn, đặt cờ false và để ghi chú rỗng.

Ngoài ra hãy tạo:
- summary_vi — tóm tắt nội dung (tiếng Việt, ≤ 500 từ)
- keywords — tối đa 10 từ khóa
- notes — tối đa 5 điểm cần chú ý

Ngôn ngữ khách hàng khai báo trên hồ sơ: {customer_language}

NỘI DUNG FILE RFP ĐÍNH KÈM (đã trích và che PII, có thể rỗng):
{files_text}

DANH SÁCH REQUIREMENT MẪU (tối đa 40 dòng; tổng số: {requirement_count}):
{requirements_text}

NỘI DUNG YÊU CẦU (đã che PII):
\"\"\"
{request_content_masked}
\"\"\"

Trả về JSON hợp lệ, đúng schema, không kèm giải thích."""
