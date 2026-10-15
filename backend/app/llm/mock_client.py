"""MockLLMClient — trả fixture theo schema, dùng cho test/CI/demo (BR-03).

Registry fixture theo tên schema + chế độ (spec §3.3):
- ``good``: hợp lệ (IntakeExtraction/GapQuestions có biến thể theo ngôn ngữ khách).
- ``bad_schema``: sai schema → test retry (BR-02).
- ``with_number``: chứa trường số ``man_day`` → bị chặn ở lớp schema (BR-01).
- ``money_in_text``: lẫn số tiền trong ``summary_vi`` — đăng ký sẵn cho M7.

Hỗ trợ ``fail_counts`` (schema → số lần trả fixture xấu trước khi trả tốt) để
test resume pipeline: bước fail ở lần chạy đầu, thành công ở lần rerun.
"""

from __future__ import annotations

from pydantic import BaseModel

from app.privacy import mask_text

# ---------------------------------------------------------------- IntakeExtraction

_INTAKE_JA = {
    "objectives_vi": (
        "Khách hàng (giả lập) muốn xây dựng hệ thống CRM để quản lý toàn bộ thông tin "
        "khách hàng, lịch sử giao dịch và quy trình chăm sóc khách hàng."
    ),
    "users_vi": "Nhân viên kinh doanh, nhân viên CSKH và quản lý phòng ban.",
    "data_vi": "Dữ liệu khách hàng hiện có trên Excel, dữ liệu giao dịch từ hệ thống kế toán.",
    "constraints_vi": [
        "Hệ thống phải tương thích môi trường đám mây hiện tại",
        "Giao diện sử dụng tiếng Nhật",
    ],
    "budget_mentioned": True,
    "budget_note_vi": "RFP có nêu ngân sách dự kiến cho phạm vi CRM ban đầu; cần đối chiếu với phương án và phê duyệt nội bộ.",
    "deadline_mentioned": True,
    "deadline_note_vi": "RFP nêu mốc khởi động, sử dụng MVP và triển khai chính thức; cần xác nhận các mốc nghiệm thu.",
    "customer_schedule_note_vi": "Khách dự kiến thực hiện từ tháng 1 đến tháng 9 năm 2027; cần xác nhận mốc chi tiết.",
    "customer_language_detected": "ja",
    "summary_vi": (
        "Khách hàng Nhật Bản (giả lập) cần xây dựng hệ thống CRM quản lý khách hàng, "
        "tích hợp dữ liệu hiện có, giao diện tiếng Nhật."
    ),
    "keywords": ["CRM", "quản lý khách hàng", "tích hợp"],
    "notes": ["Cần làm rõ số người dùng đồng thời"],
}

_INTAKE_VI = {
    "objectives_vi": (
        "Khách hàng (giả lập) muốn xây dựng hệ thống quản lý kho để theo dõi nhập xuất tồn "
        "theo thời gian thực và tích hợp với phần mềm kế toán."
    ),
    "users_vi": "Thủ kho, nhân viên kế toán và ban giám đốc.",
    "data_vi": "Dữ liệu tồn kho hiện đang quản lý bằng Excel, cần chuyển sang hệ thống tập trung.",
    "constraints_vi": [
        "Triển khai trong nước, hỗ trợ tiếng Việt",
        "Cần báo cáo theo yêu cầu của ban giám đốc",
    ],
    "budget_mentioned": True,
    "budget_note_vi": "Khách có ngân sách dự kiến nhưng chưa chốt con số cuối cùng.",
    "deadline_mentioned": False,
    "deadline_note_vi": "",
    "customer_schedule_note_vi": "",
    "customer_language_detected": "vi",
    "summary_vi": (
        "Khách hàng Việt Nam (giả lập) cần hệ thống quản lý kho, theo dõi nhập xuất tồn "
        "và tích hợp kế toán."
    ),
    "keywords": ["quản lý kho", "tích hợp kế toán", "báo cáo"],
    "notes": [],
}

# ---------------------------------------------------------------- GapQuestions

_GAP_QUESTION_TPL = [
    {
        "question": "ご要望のデータ件数はどのくらいですか？（例：100万件）",
        "reason_vi": "Ảnh hưởng trực tiếp tới effort xử lý dữ liệu",
        "impact": "effort",
        "related_req_codes": [],
    },
    {
        "question": "既存システムとの連携方法は決まっていますか？",
        "reason_vi": "Quyết định hướng giải pháp tích hợp",
        "impact": "solution",
        "related_req_codes": [],
    },
    {
        "question": "利用ユーザー数の想定は何人ですか？",
        "reason_vi": "Ảnh hưởng tới thiết kế hạ tầng và chi phí",
        "impact": "price",
        "related_req_codes": [],
    },
    {
        "question": "稼働時間帯や稼働率の要件はありますか？",
        "reason_vi": "Ảnh hưởng tới phương án vận hành",
        "impact": "solution",
        "related_req_codes": [],
    },
    {
        "question": "セキュリティ要件（認証方式など）はありますか？",
        "reason_vi": "Ảnh hưởng tới kiến trúc bảo mật và effort",
        "impact": "effort",
        "related_req_codes": [],
    },
]

_GAP_VI_QUESTION_TPL = [
    {
        "question": "Số lượng dữ liệu cần xử lý khoảng bao nhiêu?",
        "reason_vi": "Ảnh hưởng trực tiếp tới effort xử lý dữ liệu",
        "impact": "effort",
        "related_req_codes": [],
    },
    {
        "question": "Hệ thống hiện tại cần tích hợp những gì?",
        "reason_vi": "Quyết định hướng giải pháp tích hợp",
        "impact": "solution",
        "related_req_codes": [],
    },
]

_GAP_GOOD_JA = {
    "needs_clarification": True,
    "questions": _GAP_QUESTION_TPL,
}

_GAP_GOOD_VI = {
    "needs_clarification": True,
    "questions": _GAP_VI_QUESTION_TPL,
}

_GAP_NO_QUESTIONS = {"needs_clarification": False, "questions": []}

# ---------------------------------------------------------------- Tokai (Đợt 14 E)

# Dấu hiệu nhận diện bộ mẫu Tokai trong context (request/rfp_files/intake).
_TOKAI_MARKERS = ("設備保全ナレッジAI", "東海ミナトテック", "バクニン")


def _is_tokai_context(context: dict | None) -> bool:
    """Bộ mẫu Tokai? Nhận diện qua văn bản request/tài liệu hoặc mã requirement.

    EvaluationBatch/WbsStructure không có request/rfp_files trong context —
    nhận diện qua mã requirement kiểu khách Tokai (FR-QA-xxx / NFR-PF-xxx,
    ≥ 3 phần). ``requirements`` có thể là list dict (B1/B2) hoặc list chuỗi
    (B5) — xử lý cả hai.
    """
    context = context or {}
    parts = [
        str(context.get("request", "")),
        str(context.get("intake", "")),
        " ".join(str(item.get("text", "")) for item in context.get("rfp_files", [])),
    ]
    if any(marker in " ".join(parts) for marker in _TOKAI_MARKERS):
        return True
    for key in ("requirements", "requirements_data"):
        for item in context.get(key) or []:
            if not isinstance(item, dict):
                continue
            code = str(item.get("req_code", ""))
            if code.startswith(("FR-", "NFR-")) and len(code.split("-")) >= 3:
                return True
    return False


_INTAKE_TOKAI = {
    "objectives_vi": (
        "Khách hàng (giả lập) muốn xây dựng trợ lý tri thức bảo trì nhà máy: trả lời câu hỏi "
        "của nhân viên bảo trì dựa trên tài liệu hướng dẫn thiết bị, tiêu chuẩn thao tác và lịch "
        "sử sự cố; hỗ trợ tìm sự cố tương tự và soạn báo cáo công việc."
    ),
    "users_vi": "Nhân viên bảo trì tại 3 nhà máy (豊橋, 刈谷, バクニン), khoảng 230 người dùng.",
    "data_vi": (
        "Tài liệu hướng dẫn bảo trì dạng PDF (gồm PDF scan), tiêu chuẩn thao tác, lịch sử sự cố "
        "dạng CSV; cần OCR tài liệu scan và trả lời song ngữ (đa ngôn ngữ) Nhật–Việt."
    ),
    "constraints_vi": [
        "Triển khai trên Azure Japan East, dữ liệu nằm trong tenant của khách",
        "Trả lời song ngữ (đa ngôn ngữ) Nhật–Việt",
        "PoC 3 tháng, sau đó Phase 2 và Phase 3 theo mốc khách",
        "Tích hợp Microsoft Entra ID và SharePoint Online",
    ],
    "budget_mentioned": True,
    "budget_note_vi": "RFP nêu ngân sách PoC khoảng 15 triệu JPY; cần đối chiếu khi lập báo giá.",
    "deadline_mentioned": True,
    "deadline_note_vi": "RFP nêu mốc PoC tháng 12/2026; cần xác nhận mốc nghiệm thu từng giai đoạn.",
    "customer_schedule_note_vi": "PoC đến 2026/12; Phase 2 dự kiến 2027/4–9; Phase 3 từ 2027/10.",
    "customer_language_detected": "ja",
    "summary_vi": (
        "Khách hàng Nhật Bản (giả lập) cần trợ lý tri thức bảo trì nhà máy: tra cứu tài liệu và "
        "lịch sử sự cố, trả lời song ngữ Nhật–Việt, chạy trên Azure Japan East."
    ),
    "keywords": ["bảo trì nhà máy", "tri thức bảo trì", "OCR", "song ngữ Nhật–Việt", "Azure Japan East"],
    "notes": ["Cần làm rõ tỉ lệ PDF scan và mục tiêu độ chính xác khi nghiệm thu"],
}

_GAP_TOKAI_QUESTIONS = [
    {
        "question": "対象文書のうちPDFスキャン（手書き注記を含む）の割合はどのくらいですか？",
        "reason_vi": "Ảnh hưởng trực tiếp tới khối lượng OCR và chất lượng truy hồi",
        "impact": "effort",
        "related_req_codes": [],
    },
    {
        "question": "回答精度の目標値と、評価用300問の正解セットの準備状況を教えてください。",
        "reason_vi": "Quyết định tiêu chí nghiệm thu độ chính xác và phạm vi đánh giá",
        "impact": "solution",
        "related_req_codes": [],
    },
    {
        "question": "MAINTE-PROのAPI仕様（作業報告書の登録IF）は確定していますか？",
        "reason_vi": "Ảnh hưởng tới thiết kế tích hợp và effort",
        "impact": "effort",
        "related_req_codes": [],
    },
    {
        "question": "Azure Japan Eastで利用可能なLLMモデルの選定は決まっていますか？",
        "reason_vi": "Ảnh hưởng tới kiến trúc và chi phí vận hành",
        "impact": "price",
        "related_req_codes": [],
    },
    {
        "question": "故障履歴データの個人情報（作業者氏名・メール）の扱いは確認済みですか？",
        "reason_vi": "Ảnh hưởng tới phương án che dữ liệu và tuân thủ",
        "impact": "solution",
        "related_req_codes": [],
    },
]

_GAP_TOKAI = {"needs_clarification": True, "questions": _GAP_TOKAI_QUESTIONS}

_SOLUTION_TOKAI = {
    "direction": "rag",
    "reason_vi": (
        "RAG phù hợp vì bài toán là tra cứu tài liệu bảo trì và lịch sử sự cố phi cấu trúc; "
        "lớp truy hồi cho phép trả lời có căn cứ từ tài liệu được kiểm soát, kèm nguồn tham chiếu "
        "và hỗ trợ song ngữ Nhật–Việt. Loại agent vì luồng thao tác cần kiểm soát chặt; loại "
        "fine-tune và ML truyền thống vì chưa có bài toán dự đoán cần huấn luyện riêng."
    ),
    "risks_vi": [
        "Tài liệu PDF scan chất lượng thấp ảnh hưởng độ chính xác truy hồi.",
        "Tiêu chí nghiệm thu độ chính xác (bộ 300 câu) cần thống nhất trước khi chốt.",
        "Dữ liệu phải nằm trong Azure tenant của khách (Japan East).",
        "Quyền truy cập tài liệu theo nhà máy cần được kiểm soát.",
    ],
    "architecture_notes_vi": (
        "Lớp truy hồi trên chỉ mục tài liệu đã OCR; API trả kèm nguồn tham chiếu (tên tài liệu, "
        "trang); tích hợp Entra ID, SharePoint Online và MAINTE-PRO; triển khai trên Azure Japan East."
    ),
    "reliability_vi": "Khá tin cậy khi tài liệu nguồn được OCR và chuẩn hóa, có nguồn tham chiếu.",
    "assumptions_vi": ["Tài liệu nguồn được cung cấp và phân quyền đúng.", "Bộ 300 câu đánh giá do khách chuẩn bị."],
    "excluded_directions": ["agent", "fine_tune"],
    "feasibility": {
        "technical": "khả thi nếu tài liệu scan được OCR và chuẩn hóa",
        "delivery": "khả thi trong phạm vi PoC 3 tháng",
        "operational": "khả thi với phân quyền và giám sát phù hợp",
    },
    "risks": [
        {"type_vi": "OCR", "level": 4, "description_vi": "Tài liệu PDF scan (có ghi chú tay) có thể giảm độ chính xác truy hồi.", "mitigation_vi": "OCR + kiểm tra mẫu, đo tỉ lệ nhận dạng trước khi lập chỉ mục."},
        {"type_vi": "Nghiệm thu", "level": 4, "description_vi": "Mục tiêu độ chính xác trên bộ 300 câu chưa chốt.", "mitigation_vi": "Chốt tiêu chí và bộ câu hỏi đánh giá ngay từ giai đoạn làm rõ."},
        {"type_vi": "Dữ liệu", "level": 3, "description_vi": "Dữ liệu phải nằm trong Azure tenant khách (Japan East).", "mitigation_vi": "Xác nhận vùng triển khai và quyền truy cập dữ liệu."},
        {"type_vi": "Phân quyền", "level": 3, "description_vi": "Tài liệu cần giới hạn theo nhà máy.", "mitigation_vi": "Phân quyền trước khi lập chỉ mục, kiểm tra theo nhà máy."},
    ],
    "feasibility_score": {"score": 4, "reason_vi": "Khả thi nếu tài liệu scan được OCR chuẩn hóa và tiêu chí nghiệm thu được chốt sớm."},
}


def _evaluate_tokai(requirements: list[dict]) -> dict:
    """Đánh giá đáp ứng 41 requirement Tokai theo nội dung (deterministic).

    Ưu tiên: OCR/scan → △; bảo mật/Entra/暗号 → △; nghiệm thu độ chính xác → △;
    chức năng lõi RAG (trả lời, truy hồi, song ngữ, sự cố tương tự) → ◎;
    phi chức năng vận hành → ○.
    """
    items = []
    for item in requirements:
        content = str(item.get("content", ""))
        if any(word in content for word in ("スキャン", "OCR", "文字認識")):
            rating, note = "△", "OCR tài liệu scan cần xác nhận chất lượng và tỉ lệ nhận dạng trước khi chốt phương án."
        elif any(word in content for word in ("セキュリティ", "認証", "暗号", "Entra", "学習利用")):
            rating, note = "△", "Cần xác nhận tiêu chuẩn bảo mật và cấu hình triển khai trước khi kết luận."
        elif any(word in content for word in ("正答率", "評価用質問")):
            rating, note = "△", "Tiêu chí nghiệm thu độ chính xác cần thống nhất với khách trước khi chốt."
        elif any(word in content for word in ("質問応答", "回答", "検索", "類似", "故障履歴", "多言語", "対訳")):
            rating, note = "◎", "Chức năng này phù hợp trực tiếp với phạm vi trợ lý tri thức bảo trì."
        elif any(word in content for word in ("性能", "応答時間", "稼働", "利用者", "データ量", "研修", "マニュアル", "環境")):
            rating, note = "○", "Có thể đáp ứng bằng cấu hình vận hành và thiết kế phi chức năng phù hợp."
        else:
            rating, note = "○", "Có thể đáp ứng trong phạm vi trợ lý tri thức bảo trì sau khi xác nhận chi tiết nghiệp vụ."
        items.append(
            {
                "req_code": item["req_code"],
                "rating": rating,
                "needs_clarification": rating in {"△", "cần làm rõ"},
                "note_vi": note,
            }
        )
    return {"batch": items}

_SOLUTION_FIXTURES = {
    "rag": {
        "direction": "rag",
        "reason_vi": "RAG phù hợp vì hồ sơ khách hàng và lịch sử xử lý có nhiều dữ liệu phi cấu trúc cần truy vấn theo ngữ nghĩa. Lớp truy hồi giúp trả lời có căn cứ từ tài liệu được kiểm soát. Cách tiếp cận này cho phép triển khai từng phần và đo chất lượng trước khi mở rộng.",
        "risks_vi": ["Chất lượng dữ liệu nguồn cần được kiểm soát.", "Cần kiểm soát quyền truy cập theo khách hàng.", "Câu trả lời có thể thiếu căn cứ nếu tài liệu chưa được chuẩn hóa.", "Chi phí vận hành cần được theo dõi sau khi mở rộng."],
        "architecture_notes_vi": "Dùng lớp truy hồi và kho chỉ mục tách biệt. Dữ liệu được phân quyền trước khi lập chỉ mục. API ứng dụng ghi nhận nguồn tham chiếu để người dùng kiểm tra. Thiết kế có đường lui về tìm kiếm từ khóa khi độ tin cậy thấp.",
        "reliability_vi": "Khá tin cậy khi dữ liệu nguồn được chuẩn hóa và có thể truy xuất nguồn.",
        "assumptions_vi": ["Dữ liệu nguồn được cung cấp và phân quyền đúng."],
        "excluded_directions": ["agent", "fine_tune"],
        "feasibility": {"technical": "khả thi nếu dữ liệu được chuẩn hóa", "delivery": "khả thi trong phạm vi CRM đã chốt", "operational": "khả thi với phân quyền và giám sát phù hợp"},
        "risks": [
            {"type_vi": "Dữ liệu", "level": 3, "description_vi": "Dữ liệu nguồn chưa đồng nhất.", "mitigation_vi": "Chuẩn hóa và kiểm tra dữ liệu trước lập chỉ mục."},
            {"type_vi": "Bảo mật", "level": 4, "description_vi": "Có nguy cơ truy hồi sai quyền.", "mitigation_vi": "Áp dụng phân quyền trước và trong lớp truy hồi."},
            {"type_vi": "Chất lượng", "level": 3, "description_vi": "Tài liệu thiếu nguồn tham chiếu.", "mitigation_vi": "Bắt buộc ghi nhận nguồn và dùng ngưỡng fallback."},
            {"type_vi": "Vận hành", "level": 2, "description_vi": "Chi phí vận hành tăng khi mở rộng.", "mitigation_vi": "Theo dõi chi phí và giới hạn phạm vi truy vấn."},
        ],
        "feasibility_score": {"score": 4, "reason_vi": "Khả thi nếu dữ liệu và phân quyền được xác nhận."},
    },
    "none": {
        "direction": "none",
        "reason_vi": "Bài toán chưa cần thành phần AI.",
        "risks_vi": [],
        "architecture_notes_vi": "Triển khai nghiệp vụ truyền thống.",
        "reliability_vi": "Tin cậy khi phạm vi CRM và dữ liệu nghiệp vụ được xác nhận.",
        "assumptions_vi": ["Dữ liệu CRM có cấu trúc và quy trình nghiệp vụ được thống nhất."],
        "excluded_directions": ["rag", "agent", "fine_tune"],
        "feasibility": {"technical": "khả thi với mô hình dữ liệu CRM rõ ràng", "delivery": "khả thi sau khi thống nhất quy trình nghiệp vụ", "operational": "khả thi với kiểm soát truy cập và vận hành chuẩn"},
    },
    "traditional_ml": {
        "direction": "traditional_ml",
        "reason_vi": "Dữ liệu có nhãn phù hợp với mô hình ML truyền thống.",
        "risks_vi": ["Cần duy trì chất lượng nhãn."],
        "architecture_notes_vi": "Tách pipeline huấn luyện và phục vụ dự đoán.",
        "feasibility": {"technical": "phụ thuộc chất lượng dữ liệu có nhãn", "delivery": "cần xác nhận tiêu chí đo", "operational": "cần theo dõi chất lượng sau triển khai"},
    },
    "agent": {
        "direction": "agent",
        "reason_vi": "Luồng nghiệp vụ gồm nhiều bước có thể điều phối.",
        "risks_vi": ["Cần giới hạn quyền thao tác."],
        "architecture_notes_vi": "Dùng bộ điều phối với công cụ được cho phép.",
        "feasibility": {"technical": "cần kiểm soát công cụ và quyền gọi", "delivery": "phụ thuộc thiết kế luồng", "operational": "cần giám sát thao tác"},
    },
    "fine_tune": {
        "direction": "fine_tune",
        "reason_vi": "Miền nghiệp vụ chuyên biệt cần mô hình được điều chỉnh.",
        "risks_vi": ["Cần bộ dữ liệu huấn luyện đại diện."],
        "architecture_notes_vi": "Quản lý riêng dữ liệu và vòng đời mô hình.",
        "feasibility": {"technical": "phụ thuộc bộ dữ liệu huấn luyện", "delivery": "cần xác nhận tiêu chí đánh giá", "operational": "cần quản lý vòng đời mô hình"},
    },
}

_DEFAULT_SOLUTION_RISKS = [
    {"type_vi": "Phạm vi", "level": 3, "description_vi": "Phạm vi có thể thay đổi.", "mitigation_vi": "Chốt phạm vi và tiêu chí nghiệm thu trước khi triển khai."},
    {"type_vi": "Dữ liệu", "level": 3, "description_vi": "Dữ liệu đầu vào có thể chưa đồng nhất.", "mitigation_vi": "Kiểm tra mẫu dữ liệu và thống nhất quy tắc chuẩn hóa."},
    {"type_vi": "Tích hợp", "level": 2, "description_vi": "Hệ thống liên quan có thể thay đổi giao diện.", "mitigation_vi": "Xác nhận hợp đồng tích hợp và chuẩn bị phương án dự phòng."},
    {"type_vi": "Vận hành", "level": 2, "description_vi": "Quy trình vận hành cần được xác nhận.", "mitigation_vi": "Bổ sung hướng dẫn, phân quyền và giám sát trước nghiệm thu."},
]

_GAP_TOO_MANY = {
    "needs_clarification": True,
    "questions": [
        {
            "question": f"質問 {i} について教えてください。",
            "reason_vi": f"Lý do câu hỏi {i}",
            "impact": "effort",
            "related_req_codes": [],
        }
        for i in range(1, 10)
    ],
}

# ---------------------------------------------------------------- WbsStructure (M4)

# Đợt 14 (C2): mock WBS được SINH bằng builder để mọi task lá ≤ 10 man-day
# kể cả factor cap 2.0 (rag: poc 100/mvp 370/production 160; none: 55/200/95).
# Cây 3 cấp (nhóm→task→lá), mỗi phase ≥ 1 lá pm + ≥ 1 lá qa, không vòng phụ
# thuộc. Giữ mã neo mà test dùng: WBS-001-01-01 (pm poc), WBS-002-01-02
# (backend mvp), WBS-002-01-04 (qa mvp), ...

_WBS_ROLE_ORDER = ("pm", "ba", "backend", "frontend", "qa", "ai_engineer", "infra", "brse")

# Vai trò của subgroup ĐẦU TIÊN mỗi phase — giữ đúng mã neo của fixture cũ.
_WBS_FIRST_SUBGROUP_ROLES = {
    "poc": ["pm", "qa", "ba", "backend"],
    "mvp": ["pm", "backend", "frontend", "qa"],
    "production": ["pm", "backend", "qa", "frontend"],
}

# Vòng vai trò cho các subgroup tiếp theo — nghiêng về backend (dự án phát
# triển thường backend là nút thắt lịch) để thay đổi headcount backend thực sự
# làm thay đổi lịch (test schedule_update giữ nguyên ý nghĩa).
_WBS_ROLE_CYCLE = (
    "pm", "backend", "ba", "backend", "frontend", "qa",
    "backend", "ai_engineer", "infra", "brse", "backend", "frontend",
)

_WBS_FIRST_SUBGROUP_NAMES = {
    "poc": ["Phỏng vấn khách hàng", "Kiểm thử PoC", "Phân tích nghiệp vụ", "Lắp ráp backend mẫu"],
    "mvp": ["Điều phối dự án", "API xử lý dữ liệu", "Màn hình quản trị", "Kiểm thử MVP"],
    "production": ["Quản lý release", "Tối ưu hiệu năng", "Kiểm thử chấp nhận", "Đào tạo người dùng"],
}

_WBS_NAME_POOLS: dict[str, list[str]] = {
    "pm": ["Điều phối dự án", "Quản lý tiến độ", "Báo cáo tiến độ", "Quản lý rủi ro"],
    "ba": ["Phân tích nghiệp vụ", "Khảo sát hiện trạng", "Chuẩn hóa quy trình", "Thu thập yêu cầu"],
    "backend": ["Phát triển API", "Xử lý dữ liệu", "Tích hợp hệ thống", "Tối ưu truy vấn"],
    "frontend": ["Phát triển giao diện", "Màn hình quản trị", "Tối ưu hiển thị", "Kiểm thử giao diện"],
    "qa": ["Kiểm thử chức năng", "Kiểm thử chấp nhận", "Kiểm thử hiệu năng", "Rà soát chất lượng"],
    "ai_engineer": ["Dựng mẫu AI", "Xây dựng chỉ mục", "Đánh giá chất lượng trả lời", "Tinh chỉnh prompt"],
    "infra": ["Chuẩn bị hạ tầng", "Cài đặt môi trường", "Giám sát vận hành"],
    "brse": ["Làm rõ yêu cầu", "Đối chiếu nghiệp vụ"],
}

# Hướng RAG: tên task phản ánh đúng hồ sơ Tokai (OCR, chỉ mục, song ngữ,
# tìm sự cố tương tự) — Đợt 14 E.
_WBS_RAG_NAME_POOLS: dict[str, list[str]] = {
    **_WBS_NAME_POOLS,
    "ai_engineer": [
        "OCR tài liệu scan",
        "Xây dựng chỉ mục tài liệu",
        "Trả lời song ngữ Nhật–Việt",
        "Tìm sự cố tương tự từ lịch sử bảo trì",
        "Đánh giá chất lượng truy hồi",
        "Chuẩn hóa tài liệu nguồn",
    ],
    "backend": [
        "API truy hồi tài liệu",
        "Tích hợp ghi nhận nguồn trả lời",
        "Xử lý ảnh tài liệu",
        "Tối ưu truy vấn chỉ mục",
    ],
}


def _wbs_tree(
    leaves_per_phase: dict[str, int], *, direction: str, notes: list[str]
) -> dict:
    """Sinh cây WBS 3 cấp cân bằng với số lá cho trước mỗi phase.

    Mỗi lá có role + weight 10 (man_day do code phân bổ theo midpoint phase);
    đủ lá để mọi lá ≤ 10 man-day kể cả factor cap 2.0.
    """
    phase_prefix = {"poc": "WBS-001", "mvp": "WBS-002", "production": "WBS-003"}
    phase_label = {"poc": "PoC", "mvp": "MVP", "production": "Production"}
    pools = _WBS_RAG_NAME_POOLS if direction == "rag" else _WBS_NAME_POOLS
    # Hướng "Không dùng AI" KHÔNG được có vai trò ai_engineer (N3).
    if direction == "none":
        role_cycle = tuple(role for role in _WBS_ROLE_CYCLE if role != "ai_engineer")
    else:
        role_cycle = _WBS_ROLE_CYCLE
    tasks: list[dict] = []
    # Bộ đếm theo role dùng CHUNG cho cả 3 phase để tên task xoay vòng toàn cục
    # (nếu reset theo phase, các role ít xuất hiện sẽ chỉ lặp vài tên đầu).
    role_counter: dict[str, int] = {}
    for phase, count in leaves_per_phase.items():
        prefix = phase_prefix[phase]
        tasks.append(
            {
                "task_code": prefix,
                "name_vi": f"{phase_label[phase]} — Triển khai",
                "phase": phase,
                "parent_code": None,
                "role": None,
                "weight": None,
                "depends_on": [],
            }
        )
        subgroup_index = 1
        leaf_index = 1
        while leaf_index <= count:
            sub_code = f"{prefix}-{subgroup_index:02d}"
            tasks.append(
                {
                    "task_code": sub_code,
                    "name_vi": f"{phase_label[phase]} — Nhóm {subgroup_index}",
                    "phase": phase,
                    "parent_code": prefix,
                    "role": None,
                    "weight": None,
                    "depends_on": [],
                }
            )
            if subgroup_index == 1:
                roles = _WBS_FIRST_SUBGROUP_ROLES[phase]
                fixed_names = _WBS_FIRST_SUBGROUP_NAMES[phase]
            else:
                roles = list(role_cycle)
                fixed_names = None
            for slot, role in enumerate(roles):
                if leaf_index > count:
                    break
                counter = role_counter.get(role, 0)
                role_counter[role] = counter + 1
                if fixed_names is not None:
                    name = fixed_names[slot]
                else:
                    name = pools[role][counter % len(pools[role])]
                tasks.append(
                    {
                        "task_code": f"{sub_code}-{slot + 1:02d}",
                        "name_vi": name,
                        "phase": phase,
                        "parent_code": sub_code,
                        "role": role,
                        "weight": 10,
                        "depends_on": [],
                    }
                )
                leaf_index += 1
            subgroup_index += 1
    return {"tasks": tasks, "notes_vi": notes}


# Fixture "good": WBS 3 cấp đủ 3 phase, mỗi phase ≥ 1 PM + ≥ 1 QA, không vòng,
# đủ lá để mọi lá man_day ≤ 10 kể cả factor cap 2.0 (Đợt 14 C2).
# Số lá chọn sao cho target/lá đủ nhỏ để sai số làm tròn (dồn vào lá lớn nhất)
# không đẩy lá vượt 10: mvp 370/42 ≈ 8.8 (+0.4 dồn) → ≤ 9.2.
_WBS_GOOD = _wbs_tree(
    {"poc": 12, "mvp": 42, "production": 18},
    direction="rag",
    notes=["WBS giả lập cho milestone M4 — đủ lá để mọi lá ≤ 10 man-day"],
)

# Hướng "Không dùng AI": KHÔNG có task RAG/huấn luyện mô hình, KHÔNG có
# ai_engineer (N3); vẫn đủ lá để mọi lá ≤ 10 man-day.
_WBS_NONE = _wbs_tree(
    {"poc": 8, "mvp": 22, "production": 12},
    direction="none",
    notes=["WBS giả lập cho hướng Không dùng AI (không có AI Engineer)"],
)

# Fixture "flat_ok": WBS 2 cấp hợp lệ (tối thiểu) — đủ PM/QA mỗi phase.
_WBS_FLAT = {
    "tasks": [
        {"task_code": "WBS-001", "name_vi": "PoC", "phase": "poc", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-001-01", "name_vi": "Quản lý PoC", "phase": "poc", "parent_code": "WBS-001", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-001-02", "name_vi": "Kiểm thử PoC", "phase": "poc", "parent_code": "WBS-001", "role": "qa", "weight": 15, "depends_on": []},
        {"task_code": "WBS-001-03", "name_vi": "Khảo sát", "phase": "poc", "parent_code": "WBS-001", "role": "ba", "weight": 20, "depends_on": []},
        {"task_code": "WBS-001-04", "name_vi": "Dựng mẫu", "phase": "poc", "parent_code": "WBS-001", "role": "ai_engineer", "weight": 20, "depends_on": []},
        {"task_code": "WBS-001-05", "name_vi": "Backend mẫu", "phase": "poc", "parent_code": "WBS-001", "role": "backend", "weight": 15, "depends_on": []},
        {"task_code": "WBS-001-06", "name_vi": "Giao diện mẫu", "phase": "poc", "parent_code": "WBS-001", "role": "frontend", "weight": 10, "depends_on": []},
        {"task_code": "WBS-002", "name_vi": "MVP", "phase": "mvp", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-002-01", "name_vi": "Quản lý MVP", "phase": "mvp", "parent_code": "WBS-002", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-002-02", "name_vi": "Kiểm thử MVP", "phase": "mvp", "parent_code": "WBS-002", "role": "qa", "weight": 15, "depends_on": []},
        {"task_code": "WBS-002-03", "name_vi": "Phát triển backend", "phase": "mvp", "parent_code": "WBS-002", "role": "backend", "weight": 20, "depends_on": []},
        {"task_code": "WBS-002-04", "name_vi": "Phát triển frontend", "phase": "mvp", "parent_code": "WBS-002", "role": "frontend", "weight": 20, "depends_on": []},
        {"task_code": "WBS-002-05", "name_vi": "Mô hình AI", "phase": "mvp", "parent_code": "WBS-002", "role": "ai_engineer", "weight": 15, "depends_on": []},
        {"task_code": "WBS-002-06", "name_vi": "Hạ tầng", "phase": "mvp", "parent_code": "WBS-002", "role": "infra", "weight": 10, "depends_on": []},
        {"task_code": "WBS-003", "name_vi": "Production", "phase": "production", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-003-01", "name_vi": "Quản lý production", "phase": "production", "parent_code": "WBS-003", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-003-02", "name_vi": "Kiểm thử chấp nhận", "phase": "production", "parent_code": "WBS-003", "role": "qa", "weight": 15, "depends_on": []},
        {"task_code": "WBS-003-03", "name_vi": "Tối ưu backend", "phase": "production", "parent_code": "WBS-003", "role": "backend", "weight": 20, "depends_on": []},
        {"task_code": "WBS-003-04", "name_vi": "Hỗ trợ vận hành", "phase": "production", "parent_code": "WBS-003", "role": "ai_engineer", "weight": 15, "depends_on": []},
        {"task_code": "WBS-003-05", "name_vi": "Đào tạo", "phase": "production", "parent_code": "WBS-003", "role": "frontend", "weight": 10, "depends_on": []},
        {"task_code": "WBS-003-06", "name_vi": "Cài đặt hạ tầng", "phase": "production", "parent_code": "WBS-003", "role": "infra", "weight": 10, "depends_on": []},
    ],
    "notes_vi": [],
}

# Thiếu PM ở phase mvp → retry → cảnh báo (không fail schema).
_WBS_MISSING_PM = {
    "tasks": [
        {"task_code": "WBS-001", "name_vi": "PoC", "phase": "poc", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-001-01", "name_vi": "Quản lý", "phase": "poc", "parent_code": "WBS-001", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-001-02", "name_vi": "Kiểm thử", "phase": "poc", "parent_code": "WBS-001", "role": "qa", "weight": 15, "depends_on": []},
        {"task_code": "WBS-002", "name_vi": "MVP", "phase": "mvp", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-002-01", "name_vi": "Backend", "phase": "mvp", "parent_code": "WBS-002", "role": "backend", "weight": 30, "depends_on": []},
        {"task_code": "WBS-002-02", "name_vi": "QA", "phase": "mvp", "parent_code": "WBS-002", "role": "qa", "weight": 20, "depends_on": []},
        {"task_code": "WBS-003", "name_vi": "Production", "phase": "production", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-003-01", "name_vi": "Quản lý", "phase": "production", "parent_code": "WBS-003", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-003-02", "name_vi": "Kiểm thử", "phase": "production", "parent_code": "WBS-003", "role": "qa", "weight": 15, "depends_on": []},
    ],
    "notes_vi": [],
}

# Thiếu QA ở phase production → retry → cảnh báo.
_WBS_MISSING_QA = {
    "tasks": [
        {"task_code": "WBS-001", "name_vi": "PoC", "phase": "poc", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-001-01", "name_vi": "Quản lý", "phase": "poc", "parent_code": "WBS-001", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-001-02", "name_vi": "Kiểm thử", "phase": "poc", "parent_code": "WBS-001", "role": "qa", "weight": 15, "depends_on": []},
        {"task_code": "WBS-002", "name_vi": "MVP", "phase": "mvp", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-002-01", "name_vi": "Quản lý", "phase": "mvp", "parent_code": "WBS-002", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-002-02", "name_vi": "Kiểm thử", "phase": "mvp", "parent_code": "WBS-002", "role": "qa", "weight": 15, "depends_on": []},
        {"task_code": "WBS-003", "name_vi": "Production", "phase": "production", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-003-01", "name_vi": "Quản lý", "phase": "production", "parent_code": "WBS-003", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-003-02", "name_vi": "Backend", "phase": "production", "parent_code": "WBS-003", "role": "backend", "weight": 30, "depends_on": []},
    ],
    "notes_vi": [],
}

# Vòng phụ thuộc: A depends B, B depends A → retry → cảnh báo (không fail schema).
_WBS_CYCLE = {
    "tasks": [
        {"task_code": "WBS-001", "name_vi": "PoC", "phase": "poc", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-001-01", "name_vi": "Quản lý", "phase": "poc", "parent_code": "WBS-001", "role": "pm", "weight": 20, "depends_on": ["WBS-001-02"]},
        {"task_code": "WBS-001-02", "name_vi": "Kiểm thử", "phase": "poc", "parent_code": "WBS-001", "role": "qa", "weight": 15, "depends_on": ["WBS-001-01"]},
        {"task_code": "WBS-002", "name_vi": "MVP", "phase": "mvp", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-002-01", "name_vi": "Quản lý", "phase": "mvp", "parent_code": "WBS-002", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-002-02", "name_vi": "Kiểm thử", "phase": "mvp", "parent_code": "WBS-002", "role": "qa", "weight": 15, "depends_on": []},
        {"task_code": "WBS-003", "name_vi": "Production", "phase": "production", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-003-01", "name_vi": "Quản lý", "phase": "production", "parent_code": "WBS-003", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-003-02", "name_vi": "Kiểm thử", "phase": "production", "parent_code": "WBS-003", "role": "qa", "weight": 15, "depends_on": []},
    ],
    "notes_vi": [],
}

# Trọng số khiến lá > 10 man-day → retry → cảnh báo.
_WBS_LEAF_TOO_HEAVY = {
    "tasks": [
        {"task_code": "WBS-001", "name_vi": "PoC", "phase": "poc", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-001-01", "name_vi": "Quản lý", "phase": "poc", "parent_code": "WBS-001", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-001-02", "name_vi": "Kiểm thử", "phase": "poc", "parent_code": "WBS-001", "role": "qa", "weight": 15, "depends_on": []},
        {"task_code": "WBS-002", "name_vi": "MVP", "phase": "mvp", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-002-01", "name_vi": "Phát triển chính", "phase": "mvp", "parent_code": "WBS-002", "role": "backend", "weight": 90, "depends_on": []},
        {"task_code": "WBS-002-02", "name_vi": "Kiểm thử", "phase": "mvp", "parent_code": "WBS-002", "role": "qa", "weight": 10, "depends_on": []},
        {"task_code": "WBS-003", "name_vi": "Production", "phase": "production", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-003-01", "name_vi": "Quản lý", "phase": "production", "parent_code": "WBS-003", "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-003-02", "name_vi": "Kiểm thử", "phase": "production", "parent_code": "WBS-003", "role": "qa", "weight": 15, "depends_on": []},
    ],
    "notes_vi": [],
}

# Sai schema: task nhóm (có con) lại có role → ValidationError (retry → fail rõ).
_WBS_BAD_SCHEMA = {
    "tasks": [
        {"task_code": "WBS-001", "name_vi": "PoC", "phase": "poc", "parent_code": None, "role": "pm", "weight": 20, "depends_on": []},
        {"task_code": "WBS-001-01", "name_vi": "Lá", "phase": "poc", "parent_code": "WBS-001", "role": "qa", "weight": 15, "depends_on": []},
    ],
    "notes_vi": [],
}

# BR-01: chứa man_day → extra=forbid chặn (unit test assert).
_WBS_WITH_MAN_DAY = {
    "tasks": [
        {"task_code": "WBS-001", "name_vi": "PoC", "phase": "poc", "parent_code": None, "role": None, "weight": None, "depends_on": []},
        {"task_code": "WBS-001-01", "name_vi": "Quản lý", "phase": "poc", "parent_code": "WBS-001", "role": "pm", "weight": 20, "man_day": 8, "depends_on": []},
    ],
    "notes_vi": [],
}

# ---------------------------------------------------------------- Registries

_GOOD_FIXTURES: dict[str, dict] = {
    "RfpSummary": {
        "summary_vi": (
            "Khách hàng ABC (giả lập) cần xây dựng hệ thống quản lý kho tích hợp "
            "với hệ thống kế toán hiện tại. Phạm vi gồm quản lý nhập xuất tồn, "
            "báo cáo và phân quyền người dùng."
        ),
        "keywords": ["quản lý kho", "tích hợp ERP", "báo cáo"],
        "notes": ["Cần làm rõ số lượng người dùng đồng thời"],
    },
    # Biến thể theo ngôn ngữ khách (chọn qua context.customer_language).
    "IntakeExtraction": {"ja": _INTAKE_JA, "vi": _INTAKE_VI},
    "GapQuestions": {"ja": _GAP_GOOD_JA, "vi": _GAP_GOOD_VI},
    "SolutionProposal": _SOLUTION_FIXTURES["rag"],
    "WbsStructure": _WBS_GOOD,
}

_BAD_SCHEMA_FIXTURES: dict[str, dict] = {
    # Thiếu summary_vi + keywords vượt 10 phần tử → ValidationError.
    "RfpSummary": {
        "keywords": [f"kw-{i}" for i in range(12)],
        "notes": [],
    },
    # Thiếu objectives_vi (trường bắt buộc) → ValidationError.
    "IntakeExtraction": {
        "users_vi": "Người dùng (giả lập).",
        "data_vi": "Dữ liệu (giả lập).",
        "constraints_vi": [],
        "budget_mentioned": False,
        "budget_note_vi": "",
        "deadline_mentioned": False,
        "deadline_note_vi": "",
        "customer_language_detected": "ja",
        "summary_vi": "Tóm tắt (giả lập).",
        "keywords": [],
        "notes": [],
    },
    # impact sai enum → ValidationError.
    "GapQuestions": {
        "needs_clarification": True,
        "questions": [
            {
                "question": "データ件数は？",
                "reason_vi": "Ảnh hưởng effort",
                "impact": "cost",
                "related_req_codes": [],
            }
        ],
    },
    "SolutionProposal": {"direction": "not-valid"},
    # Task nhóm có role → ValidationError (role/weight chỉ trên lá).
    "WbsStructure": _WBS_BAD_SCHEMA,
}

_WITH_NUMBER_FIXTURES: dict[str, dict] = {
    # BR-01: LLM không được xuất man-day — schema extra=forbid chặn trường lạ.
    "RfpSummary": {
        "summary_vi": "Tóm tắt giả lập.",
        "keywords": ["a"],
        "notes": [],
        "man_day": 8,
    },
    "IntakeExtraction": {
        "objectives_vi": "Mục tiêu (giả lập).",
        "users_vi": "Người dùng (giả lập).",
        "data_vi": "Dữ liệu (giả lập).",
        "constraints_vi": [],
        "budget_mentioned": False,
        "budget_note_vi": "",
        "deadline_mentioned": False,
        "deadline_note_vi": "",
        "customer_language_detected": "ja",
        "summary_vi": "Tóm tắt (giả lập).",
        "keywords": [],
        "notes": [],
        "man_day": 8,
    },
    "SolutionProposal": {"direction": "rag", "reason_vi": "Có", "risks_vi": [], "architecture_notes_vi": "Ghi chú", "man_day": 8},
    "WbsStructure": _WBS_WITH_MAN_DAY,
}

_MONEY_IN_TEXT_FIXTURES: dict[str, dict] = {
    # Đăng ký sẵn cho M7 (proposal): lẫn số tiền trong văn bản.
    "RfpSummary": {
        "summary_vi": "Ngân sách dự kiến ¥1,000,000 (giả lập) cho giai đoạn PoC.",
        "keywords": ["ngân sách"],
        "notes": [],
    },
}

_NO_QUESTIONS_FIXTURES: dict[str, dict] = {
    # needs_clarification=false, questions=[] → pipeline chạy tiếp → done.
    "GapQuestions": _GAP_NO_QUESTIONS,
}

_TOO_MANY_FIXTURES: dict[str, dict] = {
    # 9 câu hỏi > 7 → code giữ 7 câu đầu + cảnh báo (không fail schema).
    "GapQuestions": _GAP_TOO_MANY,
}

_REGISTRY: dict[str, dict[str, dict]] = {
    "good": _GOOD_FIXTURES,
    "bad_schema": _BAD_SCHEMA_FIXTURES,
    "with_number": _WITH_NUMBER_FIXTURES,
    "money_in_text": _MONEY_IN_TEXT_FIXTURES,
    "no_questions": _NO_QUESTIONS_FIXTURES,
    "too_many": _TOO_MANY_FIXTURES,
    "good_none": {"SolutionProposal": _SOLUTION_FIXTURES["none"]},
    "good_traditional_ml": {"SolutionProposal": _SOLUTION_FIXTURES["traditional_ml"]},
    "good_agent": {"SolutionProposal": _SOLUTION_FIXTURES["agent"]},
    "good_fine_tune": {"SolutionProposal": _SOLUTION_FIXTURES["fine_tune"]},
    "forbidden_numbers": {"SolutionProposal": _WITH_NUMBER_FIXTURES["SolutionProposal"]},
    # WbsStructure (M4) — spec §3.2.
    "flat_ok": {"WbsStructure": _WBS_FLAT},
    "wbs_none": {"WbsStructure": _WBS_NONE},
    "missing_pm": {"WbsStructure": _WBS_MISSING_PM},
    "missing_qa": {"WbsStructure": _WBS_MISSING_QA},
    "cycle": {"WbsStructure": _WBS_CYCLE},
    "leaf_too_heavy": {"WbsStructure": _WBS_LEAF_TOO_HEAVY},
    "with_man_day": {"WbsStructure": _WBS_WITH_MAN_DAY},
}

_PROPOSAL_TEXT = {
    "introduction": "Đề xuất giải pháp phù hợp với mục tiêu và bối cảnh của khách hàng.",
    "solution_overview": "Giải pháp được triển khai theo phạm vi đã thống nhất.",
    "approach": "Đội dự án thực hiện theo từng giai đoạn và xác nhận đầu ra.",
    "risks": "Rủi ro và giả định sẽ được theo dõi trong quá trình triển khai.",
    "conclusion": "Đề xuất là cơ sở để hai bên tiếp tục xác nhận phạm vi.\n{{QUOTATION}}",
}
_PROPOSAL_EN_TEXT = {
    "introduction": "This proposal addresses the customer's stated objectives and context.",
    "solution_overview": "The solution will be delivered within the confirmed scope.",
    "approach": "The project team will work in stages and confirm each deliverable.",
    "risks": "Risks and assumptions will be tracked throughout delivery.",
    "conclusion": "This proposal provides a basis for confirming the scope together.\n{{QUOTATION}}",
}
_PROPOSAL_JA_TEXT = {
    "introduction": "本提案はお客様の目的と前提に基づく提案です。",
    "solution_overview": "確認したスコープに沿ってソリューションを段階的に提供します。",
    "approach": "各段階で成果物を確認しながらプロジェクトを進めます。",
    "risks": "リスクと前提条件をプロジェクト期間中に管理します。",
    "conclusion": "本提案をもとに双方でスコープを確認します。\n{{QUOTATION}}",
}
_REGISTRY["good"]["ProposalOutput"] = {
    "ja": {"sections": {"introduction": "お客様の業務課題とご要望を丁寧に整理し、最適なご提案をまとめました。本提案は予算{{BUDGET}}を前提としております。詳細は各章でご説明します。", "requirements_understanding": "確認対象のご要件は{{REQUIREMENT_COUNT}}件です。各要件の優先度と受入条件を整理しました。要件への対応方針は次章以降で詳述します。", "solution_overview": "{{SOLUTION_DIRECTION}}の方向でご提案します。現行業務への影響を抑えながら段階的に導入します。導入後の効果測定も含めてご支援します。", "approach": "現状確認、要件定義、設計、開発、受入確認の順に進めます。各段階で成果物をご確認いただきます。変更が生じた場合は都度ご相談しながら進めます。", "schedule": "開始{{CUSTOMER_START}}、MVP{{CUSTOMER_MVP}}、本番{{CUSTOMER_PRODUCTION}}を基準に計画します。各マイルストーンで進捗をご報告します。遅延リスクがある場合は早期にご連絡します。", "team": "必要な役割を配置し、各段階で成果物を確認します。プロジェクトマネージャーが全体を統括します。窓口を一本化し、迅速なコミュニケーションを図ります。", "assumptions_and_scope": "前提条件と対象外はお客様と事前に確認します。データ提供と権限設定はお客様側でご準備いただきます。対象外となる作業が発生した場合は別途ご相談させていただきます。", "risks": "データ品質と権限設計を早期に確認します。リスクは定期的に見直し、対策を講じます。重大なリスクが判明した場合は速やかにご報告します。\n{{QUOTATION}}"}, "assumptions_phrased": [], "scope_out_phrased": []},
    "en": {"sections": {"introduction": "This proposal addresses the customer's objectives and context. It assumes the budget of {{BUDGET}}. Details are presented in the following sections.", "requirements_understanding": "The confirmed requirement count is {{REQUIREMENT_COUNT}}. Priorities and acceptance criteria have been reviewed. Our response to each requirement is detailed in the following sections.", "solution_overview": "We propose the {{SOLUTION_DIRECTION}} approach. The solution is delivered in stages to limit impact on current operations. Success metrics are agreed before rollout.", "approach": "Work proceeds through discovery, design, development and acceptance. Deliverables are reviewed at each stage. Changes are discussed and confirmed together.", "schedule": "The plan follows the customer milestones: start {{CUSTOMER_START}}, MVP {{CUSTOMER_MVP}}, production {{CUSTOMER_PRODUCTION}}. Progress is reported at each milestone. Risks of delay are communicated early.", "team": "Required roles are assigned and deliverables are confirmed at each stage. A project manager oversees the whole engagement. A single point of contact ensures fast communication.", "assumptions_and_scope": "Assumptions and out-of-scope items are confirmed with the customer beforehand. Data provision and access rights are prepared by the customer. Additional work outside scope is discussed separately.", "risks": "Data quality and access design are confirmed early. Risks are reviewed regularly and mitigations applied. Material risks are reported promptly.\n{{QUOTATION}}"}, "assumptions_phrased": [], "scope_out_phrased": []},
    "vi": {"sections": {"introduction": "Đề xuất này được xây dựng dựa trên mục tiêu và bối cảnh của khách hàng. Ngân sách dự kiến {{BUDGET}} được dùng làm cơ sở. Chi tiết được trình bày trong các mục sau.", "requirements_understanding": "Tổng số requirement đã xác nhận là {{REQUIREMENT_COUNT}}. Mức ưu tiên và tiêu chí nghiệm thu đã được rà soát. Phương án đáp ứng từng yêu cầu được nêu ở các mục tiếp theo.", "solution_overview": "Chúng tôi đề xuất hướng {{SOLUTION_DIRECTION}}. Giải pháp được triển khai theo giai đoạn để hạn chế ảnh hưởng tới vận hành hiện tại. Tiêu chí đo hiệu quả được thống nhất trước khi triển khai.", "approach": "Công việc thực hiện theo thứ tự khảo sát, thiết kế, phát triển và nghiệm thu. Sản phẩm từng giai đoạn được xác nhận với khách hàng. Thay đổi phát sinh sẽ được trao đổi và chốt cùng khách hàng.", "schedule": "Kế hoạch bám theo các mốc: bắt đầu {{CUSTOMER_START}}, MVP {{CUSTOMER_MVP}}, Production {{CUSTOMER_PRODUCTION}}. Tiến độ được báo cáo tại từng mốc. Rủi ro chậm tiến độ sẽ được thông báo sớm.", "team": "Các vai trò cần thiết được bố trí và sản phẩm từng giai đoạn được xác nhận. Quản lý dự án điều phối toàn bộ. Đầu mối liên hệ duy nhất giúp trao đổi nhanh chóng.", "assumptions_and_scope": "Tiền đề và nội dung ngoài phạm vi được xác nhận với khách hàng trước khi triển khai. Dữ liệu và phân quyền do khách hàng chuẩn bị. Công việc ngoài phạm vi sẽ được trao đổi riêng.", "risks": "Chất lượng dữ liệu và thiết kế phân quyền được xác nhận sớm. Rủi ro được rà soát định kỳ và có biện pháp giảm thiểu. Rủi ro trọng yếu sẽ được báo cáo kịp thời.\n{{QUOTATION}}"}, "assumptions_phrased": [], "scope_out_phrased": []},
}
for _mode in ("proposal_vi_good", "proposal_en_good", "proposal_ja_good"):
    _REGISTRY[_mode] = {"ProposalOutput": _REGISTRY["good"]["ProposalOutput"]}
_REGISTRY["proposal_with_money"] = {"ProposalOutput": {"sections": {**_PROPOSAL_TEXT, "risks": "Chi phí ¥1000 cần được xác nhận."}, "assumptions_phrased": [], "scope_out_phrased": []}}
_REGISTRY["proposal_with_man_day"] = {"ProposalOutput": {"sections": {**_PROPOSAL_TEXT, "risks": "Cần 3 man-day."}, "assumptions_phrased": [], "scope_out_phrased": []}}
_REGISTRY["proposal_missing_assumption"] = {"ProposalOutput": {"sections": _PROPOSAL_TEXT, "assumptions_phrased": [], "scope_out_phrased": []}}
_REGISTRY["proposal_bad_schema"] = {"ProposalOutput": {"sections": {"introduction": "x"}, "assumptions_phrased": [], "scope_out_phrased": []}}
_REGISTRY["good"]["JaCheckResult"] = {"result": "pass", "issues": []}
_REGISTRY["bad_schema"]["JaCheckResult"] = {"result": "invalid"}
_REGISTRY["ja_check_pass"] = {"JaCheckResult": {"result": "pass", "issues": []}}
_REGISTRY["ja_check_warning"] = {"JaCheckResult": {"result": "warning", "issues": [{"severity": "warning", "section": "solution_overview", "message_vi": "Thuật ngữ chưa khớp glossary.", "suggestion_ja": "用語を glossary の表記に合わせてください。", "source": "glossary"}]}}
_REGISTRY["good"]["EmailDraft"] = {
    "ja": {"subject": "ご確認のお願い：追加質問", "body": "{{CUSTOMER_NAME}} ご担当者様\n\nお世話になっております。追加の確認事項について、ご回答をお願いいたします。\n\n何卒よろしくお願いいたします。"},
    "en": {"subject": "Request for clarification", "body": "Dear {{CUSTOMER_NAME}},\n\nCould you please review and answer the additional clarification questions?\n\nBest regards,"},
    "vi": {"subject": "Đề nghị xác nhận thông tin", "body": "Kính gửi {{CUSTOMER_NAME}},\n\nKính nhờ Quý khách xem và trả lời các câu hỏi cần làm rõ bổ sung.\n\nTrân trọng,"},
}


# ---------------------------------------------------------------- Truy vết requirement (B5 mock)

# Requirement chứa từ khóa này → coi là "cần làm rõ" → mock KHÔNG gán mã cho task
# (chưa đủ thông tin để lập kế hoạch — thiet_ke_danh_gia.md §4).
_UNCLEAR_KEYWORDS = ("未定", "要相談", "不明", "tbd", "chưa rõ", "cần làm rõ", "調整中")
# Tích hợp hệ thống ngoài chưa xác định giao diện → cần làm rõ trước khi lập kế
# hoạch. Với mẫu ja_email khớp đúng FR-019 (会計システム) và FR-020 (販売管理システム)
# → 34/36 được truy vết, 2 mục cần làm rõ nằm trong danh sách "chưa có task".
_EXTERNAL_INTEGRATION_KEYWORDS = ("会計システム", "販売管理システム")


def _is_unclear_requirement(req: dict) -> bool:
    content = str(req.get("content") or "")
    lowered = content.casefold()
    if req.get("unclear"):
        return True
    if any(token in content for token in _UNCLEAR_KEYWORDS):
        return True
    if any(token in lowered for token in _UNCLEAR_KEYWORDS):
        return True
    return any(token in content for token in _EXTERNAL_INTEGRATION_KEYWORDS)


def _assign_requirement_codes(base: dict, context: dict | None) -> dict:
    """Gán requirement_codes cho task lá theo category (thiet_ke_danh_gia.md §4).

    FR → task lá role backend/frontend, NFR → task lá role infra/qa, theo vòng
    tròn. Requirement "cần làm rõ" KHÔNG được gán.
    """
    tasks = [dict(task) for task in base["tasks"]]
    requirements = (context or {}).get("requirements_data") or []
    fr_codes = [
        req["req_code"]
        for req in requirements
        if str(req.get("req_code", "")).upper().startswith("FR")
        and not _is_unclear_requirement(req)
    ]
    nfr_codes = [
        req["req_code"]
        for req in requirements
        if str(req.get("req_code", "")).upper().startswith("NFR")
        and not _is_unclear_requirement(req)
    ]
    fe_leaves = [t for t in tasks if t.get("role") in ("backend", "frontend")]
    nfr_leaves = [t for t in tasks if t.get("role") in ("infra", "qa")]
    for index, code in enumerate(fr_codes):
        if fe_leaves:
            leaf = fe_leaves[index % len(fe_leaves)]
            leaf.setdefault("requirement_codes", []).append(code)
    for index, code in enumerate(nfr_codes):
        if nfr_leaves:
            leaf = nfr_leaves[index % len(nfr_leaves)]
            leaf.setdefault("requirement_codes", []).append(code)
    return {"tasks": tasks, "notes_vi": list(base.get("notes_vi", []))}


def _content_fixture(name: str, context: dict | None) -> dict | None:
    """Fixtures có ngữ nghĩa cho demo CRM/Tokai, vẫn hoàn toàn deterministic."""
    context = context or {}
    # Bộ mẫu Tokai — kiểm tra TRƯỚC các nhánh CRM/budget để không bị nhầm
    # (RFP Tokai cũng chứa từ khóa 予算/2027年) (Đợt 14 E).
    if _is_tokai_context(context):
        if name == "IntakeExtraction":
            return _INTAKE_TOKAI
        if name == "GapQuestions" and context.get("rounds_used", 0) < 1:
            return _GAP_TOKAI
        if name == "SolutionProposal":
            return _SOLUTION_TOKAI
        if name == "EvaluationBatch" and context.get("requirements"):
            return _evaluate_tokai(context["requirements"])
    if name == "GapQuestions" and context.get("rounds_used", 0) >= 1:
        answers = context.get("previous_answers", [])
        texts = [str(item.get("answer", "")).strip() for item in answers]
        # Vòng 2 chỉ khi còn thông tin chặn: trả lời ĐỦ vòng 1 → dừng ở vòng 1.
        still_blocked = any(
            not text or any(token in text.casefold() for token in ("未定", "tbd", "chưa rõ", "不明"))
            for text in texts
        )
        if texts and not still_blocked:
            return _GAP_NO_QUESTIONS
        lang = context.get("customer_language", "ja")
        if lang == "ja":
            return {"needs_clarification": True, "questions": [{"question": "本番運用の監視担当と対応時間帯を決めていますか？", "reason_vi": "Vòng 1 vẫn còn thông tin chặn cần xác nhận trước khi chốt giải pháp và lịch", "impact": "solution", "related_req_codes": []}]}
        return {"needs_clarification": True, "questions": [{"question": "Đã xác định người phụ trách giám sát và thời gian hỗ trợ vận hành chưa?", "reason_vi": "Vòng 1 vẫn còn thông tin chặn cần xác nhận trước khi chốt giải pháp và lịch", "impact": "solution", "related_req_codes": []}]}
    if name == "IntakeExtraction":
        files = " ".join(str(item.get("text", "")) for item in context.get("rfp_files", []))
        if any(token in files for token in ("1,500万円", "予算", "2027年")):
            return {
                **_INTAKE_JA,
                "budget_note_vi": "RFP nêu ngân sách khoảng 1,500万円 (JPY, chưa thuế) cho xây dựng ban đầu; cần đối chiếu khi lập báo giá.",
                "deadline_note_vi": "RFP nêu khởi động tháng 1/2027, MVP sử dụng tháng 6/2027 và triển khai chính thức tháng 9/2027.",
                "customer_schedule_note_vi": "Khách muốn khởi động tháng 1/2027, dùng MVP vào tháng 6/2027 và triển khai chính thức tháng 9/2027.",
            }
    if name == "EvaluationBatch" and context.get("requirements"):
        items = []
        for item in context["requirements"]:
            content = str(item.get("content", "")).lower()
            if any(word in content for word in ("unsupported", "not supported", "×", "対象外")):
                rating, note = "×", "Nội dung này nằm ngoài phạm vi CRM mẫu và cần loại khỏi phương án hiện tại."
            elif any(word in content for word in ("unclear", "tbd", "未定", "要相談", "cần làm rõ")):
                rating, note = "cần làm rõ", "Cần xác nhận phạm vi và tiêu chí nghiệm thu trước khi đánh giá đáp ứng."
            elif any(word in content for word in ("audit", "監査", "security", "セキュリティ", "暗号")):
                rating, note = "△", "Cần xác nhận tiêu chuẩn bảo mật và cấu hình triển khai trước khi kết luận."
            elif any(word in content for word in ("search", "検索")):
                rating, note = "◎", "Chức năng tìm kiếm phù hợp trực tiếp với phạm vi tra cứu CRM."
            elif any(word in content for word in ("report", "レポート")):
                rating, note = "◎", "Chức năng báo cáo phù hợp với nhu cầu tổng hợp và theo dõi CRM."
            elif any(word in content for word in ("register", "登録", "顧客")):
                rating, note = "◎", "Chức năng CRM này phù hợp trực tiếp với phạm vi quản lý dữ liệu khách hàng."
            elif any(word in content for word in ("performance", "性能", "backup", "バックアップ", "監視")):
                rating, note = "○", "Có thể đáp ứng bằng cấu hình vận hành và thiết kế phi chức năng phù hợp."
            else:
                rating, note = "○", "Có thể đáp ứng trong phạm vi CRM sau khi xác nhận chi tiết nghiệp vụ."
            items.append({"req_code": item["req_code"], "rating": rating, "needs_clarification": rating in {"△", "cần làm rõ"}, "note_vi": note})
        return {"batch": items}
    if name == "SolutionProposal":
        text = " ".join(str(context.get(key, "")) for key in ("request", "intake", "sample_profile")).lower()
        if any(word in text for word in ("crm", "khách hàng", "顧客", "customer")):
            return {**_SOLUTION_FIXTURES["none"], "reason_vi": "CRM chủ yếu là dữ liệu có cấu trúc và quy trình nghiệp vụ xác định; chọn giải pháp truyền thống, không cần RAG. Loại RAG vì không có nhu cầu truy hồi tài liệu phi cấu trúc; loại agent vì luồng thao tác cần kiểm soát; loại fine-tune và ML vì chưa có bài toán dự đoán cần huấn luyện."}
    if name == "WbsStructure":
        # Gán requirement_codes cho task lá theo category (FR → backend/frontend,
        # NFR → infra/qa, vòng tròn); requirement "cần làm rõ" không được gán.
        base = _WBS_NONE if context.get("direction") == "none" else _WBS_GOOD
        return _assign_requirement_codes(base, context)
    return None


def get_fixture(schema: type[BaseModel], mode: str = "good", context: dict | None = None) -> dict:
    """Lấy fixture theo tên schema + chế độ; biến thể ngôn ngữ theo context."""
    table = _REGISTRY.get(mode)
    if table is None:
        raise KeyError(f"Không có chế độ fixture '{mode}'")
    name = getattr(schema, "__name__", str(schema))
    if name not in table:
        raise KeyError(f"Không có fixture '{mode}' cho schema {name}")
    # Biến thể nội dung theo context (ngôn ngữ/hướng giải pháp) chỉ áp dụng
    # cho chế độ "good"; fixture chuyên biệt (missing_pm/bad_schema/...) giữ nguyên.
    value = (_content_fixture(name, context) if mode == "good" else None) or table[name]
    if isinstance(value, dict) and "ja" in value and "vi" in value:
        lang = (context or {}).get("customer_language", "ja")
        value = value.get(lang, value["ja"])
    value = dict(value)
    if name == "SolutionProposal":
        value.setdefault("risks", list(_DEFAULT_SOLUTION_RISKS))
        value.setdefault(
            "feasibility_score",
            {"score": 3, "reason_vi": "Khả thi sau khi xác nhận các tiền đề chính."},
        )
    return value


class MockLLMClient:
    """Client giả lập — không gọi HTTP, không gọi LLM thật.

    Ghi lại ``last_prompt`` (SAU khi che PII), ``call_count`` và ``call_counts``
    theo schema để test chứng minh BR-06 (prompt đã mask), BR-02 (retry ≤ 2)
    và FR-010.4 (vòng 2 không gọi LLM).
    """

    def __init__(
        self,
        fixture_mode: str = "good",
        fixture_modes: dict[str, str] | None = None,
        fail_counts: dict[str, int] | None = None,
    ) -> None:
        self.fixture_mode = fixture_mode
        self.fixture_modes = dict(fixture_modes or {})
        self.fail_counts = dict(fail_counts or {})
        self.call_count = 0
        self.call_counts: dict[str, int] = {}
        self.last_prompt: str | None = None
        self.last_context: dict | None = None
        self.prompts_by_schema: dict[str, list[str]] = {}

    def complete(
        self,
        *,
        schema: type[BaseModel],
        prompt: str,
        context: dict | None = None,
    ) -> dict:
        # Điểm chặn duy nhất BR-06: che PII trước khi "gửi" cho provider.
        prompt = mask_text(prompt)
        self.last_prompt = prompt
        self.last_context = context
        self.call_count += 1
        name = getattr(schema, "__name__", str(schema))
        self.call_counts[name] = self.call_counts.get(name, 0) + 1
        self.prompts_by_schema.setdefault(name, []).append(prompt)

        if self.fail_counts.get(name, 0) > 0:
            self.fail_counts[name] -= 1
            mode = "bad_schema"
        else:
            mode = self.fixture_modes.get(name, self.fixture_mode)
        # Older pipeline tests override only one schema. Keep the default
        # fixture for every other schema so adding B6 cannot break them.
        if name == "ProposalOutput" and mode == "good" and "ProposalOutput" not in _REGISTRY[mode]:
            mode = "proposal_vi_good"
        if name == "EvaluationBatch" and mode == "good":
            content_result = _content_fixture(name, context)
            if content_result is not None:
                return content_result
            return {
                "batch": [
                    {
                        "req_code": code,
                        "rating": "○",
                        "needs_clarification": False,
                        "note_vi": "Requirement phù hợp với hướng giải pháp đã chọn.",
                    }
                    for code in (context or {}).get("batch_codes", [])
                ]
            }
        # The generic bad-schema fixture must remain invalid for every schema;
        # older tests use it to exercise the bounded retry path.
        return get_fixture(schema, mode, context)
