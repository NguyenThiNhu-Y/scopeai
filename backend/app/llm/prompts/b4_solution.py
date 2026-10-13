from __future__ import annotations

import json


def build_solution_prompt(context: dict) -> str:
    return """Bạn là kiến trúc sư giải pháp. Trước tiên hãy xét nghiêm túc hướng "không cần AI" (none).
Hãy đề xuất đúng một hướng trong: none, traditional_ml, rag, agent, fine_tune.
Nếu loại một hướng, phải nêu lý do loại từng hướng trong reason_vi hoặc architecture_notes_vi.
Trả lời tiếng Việt gồm direction, reason_vi, risks_vi, architecture_notes_vi.
Chỉ giải thích; tuyệt đối không đưa effort, man_day, price, cost, amount, date, schedule, factor, min, max hoặc midpoint.
Context hồ sơ (đã được che PII):\n""" + json.dumps(context, ensure_ascii=False, indent=2)
