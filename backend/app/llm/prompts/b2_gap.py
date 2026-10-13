"""Prompt builder cho bước B2 — Gap detection → câu hỏi làm rõ (llm_pipeline.md §3)."""

from __future__ import annotations

import json

_MAX_QUESTIONS = 7


def build_gap_prompt(
    intake_output: dict,
    rounds_used: int,
    previous_answers: list[dict],
    customer_language: str,
    rfp_files: list[dict] | None = None,
    requirements: list[dict] | None = None,
    requirement_count: int = 0,
) -> str:
    """Dựng prompt cho bước phát hiện thiếu thông tin (B2).

    - Câu hỏi viết bằng NGÔN NGỮ KHÁCH (vi/en/ja); lý do bằng tiếng Việt (BR-07).
    - Tối đa 7 câu hỏi (FR-010.1).
    - ``related_req_codes`` LUÔN rỗng ở M2 (chưa có bảng requirements — M6).
    """
    intake_text = json.dumps(intake_output, ensure_ascii=False, indent=2)
    prev_text = json.dumps(previous_answers, ensure_ascii=False, indent=2) if previous_answers else "[]"
    files_text = json.dumps(rfp_files or [], ensure_ascii=False, indent=2)
    requirements_text = json.dumps(requirements or [], ensure_ascii=False, indent=2)

    return f"""Bạn là trợ lý presales (chuyên viên chào thầu). Bước B1 đã trích xuất thông tin yêu cầu; nhiệm vụ của bạn là phát hiện THÔNG TIN CÒN THIẾU ảnh hưởng tới giải pháp (solution), công sức ước tính (effort) hoặc giá (price).

NGÔN NGỮ KHÁCH HÀNG: {customer_language}

QUY TẮC:
- Nếu thông tin đã đủ → needs_clarification=false, questions rỗng.
- Nếu thiếu thông tin QUAN TRỌNG → needs_clarification=true và hỏi TỐI ĐA {_MAX_QUESTIONS} câu.
- Mỗi câu hỏi:
  * question — viết bằng NGÔN NGỮ KHÁCH HÀNG ({customer_language}), ngắn gọn, dễ trả lời.
  * reason_vi — lý do hỏi bằng TIẾNG VIỆT (nội bộ).
  * impact — một trong: solution | effort | price.
  * related_req_codes — LUÔN ĐỂ RỖNG [] (hệ thống chưa có danh sách yêu cầu).
- KHÔNG hỏi lại điều đã có trong phần trích xuất B1.
- KHÔNG xuất con số man-day, giá tiền hay ngày lịch (BR-01).
- Chỉ hỏi những gì THỰC SỰ cần để chốt giải pháp / ước lượng / báo giá.

KẾT QUẢ BƯỚC B1 (trích xuất):
{intake_text}

NỘI DUNG FILE RFP ĐÍNH KÈM (đã trích và che PII):
{files_text}

DANH SÁCH REQUIREMENT MẪU (tối đa 40 dòng; tổng số: {requirement_count}):
{requirements_text}

SỐ VÒNG HỎI ĐÃ DÙNG: {rounds_used} (tối đa 2 vòng — chỉ hỏi nếu còn vòng)

CÂU TRẢ LỜI VÒNG TRƯỚC (nếu có):
{prev_text}

Trả về JSON hợp lệ, đúng schema, không kèm giải thích."""
