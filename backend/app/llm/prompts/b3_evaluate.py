"""Prompt builder cho bước B3 — Đánh giá requirement (llm_pipeline.md §4)."""

from __future__ import annotations

import json


def build_evaluation_prompt(batch: list[dict], direction: str | None = None) -> str:
    """Dựng prompt đánh giá một lô requirement (tối đa 40).

    - Danh sách requirement (mã + nội dung + độ ưu tiên + nhóm) được nhúng
      TRỰC TIẾP vào prompt. Provider ``openai_compat`` chỉ gửi ``prompt`` chứ
      không gửi ``context`` (BR-03), nên nếu chỉ đặt requirement trong context
      thì LLM thật phải đoán rating mà không thấy nội dung.
    - PII trong nội dung requirement được che tại gateway trước khi gửi (BR-06).
    - LLM chỉ trả rating/nhận xét; mọi con số man-day/giá/ngày do code tính (BR-01).
    """
    requirements_text = json.dumps(batch, ensure_ascii=False, indent=2)
    direction_text = direction or "chưa chọn hướng giải pháp"
    return f"""Bạn là chuyên gia presales đánh giá mức độ đáp ứng của từng requirement theo hướng giải pháp và các thành phần kiến trúc.

HƯỚNG GIẢI PHÁP HIỆN TẠI: {direction_text}

DANH SÁCH REQUIREMENT CỦA LÔ HIỆN TẠI (đánh giá ĐÚNG từng requirement trong danh sách này, dùng req_code để đối chiếu):
{requirements_text}

QUY ƯỚC RATING:
- ◎ = đáp ứng đầy đủ
- ○ = đáp ứng với cấu hình chuẩn
- △ = cần tùy biến/điều kiện
- × = không đáp ứng
- cần làm rõ = thiếu thông tin để kết luận

YÊU CẦU:
- Mỗi requirement trong danh sách trên phải có đúng một mục trong "batch", req_code khớp CHÍNH XÁC mã trong danh sách.
- note_vi phải là một câu tiếng Việt cụ thể, nêu lý do cho từng rating; không được viết chung chung.
- Chỉ trả req_code, rating, needs_clarification và note_vi."""