# Handoff Đợt 10 — Backend

Ngày: 12/10/2026. LLM_PROVIDER=mock. Test: **256 passed** (245 cũ + 11 mới).

## Tóm tắt thay đổi

### A. Lịch
1. **N1 — MVP sau go/no-go, Production sau MVP** (`schedule_engine.py`, `schedule_service.py`)
   - `compute_schedule` nhận thêm `go_no_go_gap_working_days`; tính `go_no_go_start/go_no_go_end`
     ngay trong engine (sau PoC xong + gap ngày LV); **MVP phase bắt đầu = max(start tự nhiên, go_no_go_end)**;
     **Production phase bắt đầu sau khi MVP phase kết thúc**.
   - `earliest_mvp_start` / `earliest_production_start` nay = ngày bắt đầu thực của phase trong lịch
     (trước đây tính kiểu `max(mvp_start, customer_schedule_start)` gây mâu thuẫn với chính lịch).
   - `schedule_service.update_schedule` bỏ đoạn tính go/no-go thủ công, đọc thẳng từ kết quả engine.
2. **N2 — Chạy song song theo vai trò trong cùng phase** (`schedule_engine.py`)
   - Mỗi role giữ **cursor riêng** trong phase; task bắt đầu tại
     `max(cursor_role, end của depends_on, phase_start)`; duration = `ceil(man_day ÷ headcount[role])`;
     phase kết thúc khi task cuối của phase xong. 210 man-day với PM3/BA1/AI2/BE3/FE3/QA2/Infra1
     ngắn hơn rõ so với tuần tự (test chứng minh chênh ≥ 20 ngày LV).
3. **A3 — Trích mốc khách + lịch mặc định + cảnh báo** (`b1_intake.py`, `b5_wbs.py`, `schedule_service.py`)
   - `_find_milestone` mới: quét từng câu, chọn mốc ngày **đứng trước từ khóa** và gần nhất
     (bắt được "2027年1月に着手", "同年6月までにMVP", "同年9月に本番展開").
   - `customer_schedule_start` = 2027-01-01, `customer_mvp_start` = 2027-06-01,
     `customer_production_start` = 2027-09-01, **`customer_schedule_end` = mốc Production 2027-09-01**
     (trước đây sai = max month với day 30/1).
   - `b5_wbs` lịch mặc định bắt đầu từ `customer_schedule_start` (fallback 2 tuần tới như cũ).
   - `schedule_to_out` thêm **cảnh báo** khi lịch MVP/Production/end trễ hơn mốc khách.

### B. Nhất quán giải pháp (N3)
- `mock_client.py`: thêm fixture `_WBS_NONE` — hướng "Không dùng AI" **không có task RAG/huấn luyện mô hình,
  không có role `ai_engineer`**; áp dụng qua `_content_fixture` khi `context.direction == "none"`
  (chỉ trong chế độ "good" — không nuốt fixture `missing_pm/bad_schema/...`).
- `b5_wbs` allocation nhân sự tự không có `ai_engineer` khi WBS không có role đó.
- `evaluations` router + `SolutionCurrentOut`: bổ sung **`risks` (loại, mức 1–5, mô tả, giảm thiểu)**,
  **`risks_vi`**, **`feasibility_score` (1–5)** — trước đây thiếu nên UI thấy "Chưa có rủi ro được ghi nhận".

### C. Câu hỏi (phần API)
- `mock_client.py` `_content_fixture(GapQuestions)`: **trả lời ĐỦ vòng 1 → dừng ở vòng 1**
  (trả `_GAP_NO_QUESTIONS`); chỉ hỏi vòng 2 khi còn thông tin chặn (câu trả lời trống hoặc chứa
  "未定"/"tbd"/"chưa rõ"/"不明").
- `round_two_reason_vi` đã có sẵn trong `list_questions` — giữ nguyên, có test chứng minh.
- Cập nhật 2 test cũ (`test_round_two_no_llm_call`, `test_round_two_response_exposes_blocking_reason`)
  sang dùng câu trả lời chặn để kích hoạt vòng 2.

### D. Bid/No-bid
- `bid_qualification_service.get_or_create`: khi hồ sơ chưa có tiêu chí → **tải tiêu chí mặc định từ
  Cài đặt** (`ReferenceSetting key='bid_no_bid'`, fallback `OPTIONAL_DEFAULTS`) → `GET /bid-qualification`
  trả **200** (trước đây 500 vì schema bắt buộc ≥ 1 tiêu chí).

### E. Phần backend của mục frontend
- `quotation_engine.py`: **`totals.subtotal` = trước dự phòng** (base + overhead, không gồm contingency/operating);
  thêm `tax_amount`, `tax_percent`; `tax_included` tính theo `tax_mode` (tax_included → không cộng thêm thuế);
  `tax_mode` lưu vào row; `contingency_percent` lưu/trả đúng (20 → 20, không thành 2000).
- `mock_client.py` ProposalOutput: **mỗi mục một nội dung 3–5 câu, KHÔNG lặp tiêu đề** (tiêu đề do UI render);
  bản tiếng Nhật **không lẫn tiếng Việt**; dùng placeholder `{{BUDGET}}`, `{{CUSTOMER_START}}`,
  `{{CUSTOMER_MVP}}`, `{{CUSTOMER_PRODUCTION}}`, `{{REQUIREMENT_COUNT}}`, `{{SOLUTION_DIRECTION}}`.
- `b6_proposal._render_customer_facts`: nhãn thiếu dữ liệu/ngân sách/hướng giải pháp **theo ngôn ngữ khách**
  (ja: "未定"/"予算データなし"; vi: "chưa có dữ liệu"; en: "not yet defined").

## File đã sửa
- `backend/app/services/schedule_engine.py`
- `backend/app/services/schedule_service.py`
- `backend/app/pipeline/steps/b5_wbs.py`
- `backend/app/pipeline/steps/b1_intake.py`
- `backend/app/llm/mock_client.py`
- `backend/app/schemas/api_schemas/solution.py`
- `backend/app/api/routers/evaluations.py`
- `backend/app/services/bid_qualification_service.py`
- `backend/app/services/quotation_engine.py`
- `backend/app/pipeline/steps/b6_proposal.py`
- `backend/tests/test_dot10_backend.py` (mới — 11 test: A1, A2 ×2, A3 ×3, B ×2, C ×2, D)
- `backend/tests/test_clarifying_questions.py` (cập nhật 2 test vòng 2)
- `backend/tests/test_m3_sample_and_mock.py` (cập nhật test proposal: không lặp tiêu đề + không lẫn tiếng Việt)

## Kiểm tra
- `pytest` backend: **256 passed** (chạy 2 lần; lần 2 sau khi sửa `earliest_mvp_start` trả date thay vì ISO string
  gây lỗi SQLite Date, và giới hạn `_content_fixture` chỉ áp dụng ở mode "good").

## Lưu ý cho frontend (bước kế tiếp)
- `QuestionsResponse` cần thêm field `round_two_reason_vi` (backend đã trả) và hiển thị khi có vòng 2.
- `totals.subtotal` giờ là **trước dự phòng**; `totals.tax_amount`/`tax_mode` có sẵn để vẽ dòng thuế đúng chế độ.
- `solution_direction.risks` (mảng có `type_vi/level/description_vi/mitigation_vi`) và `feasibility_score` đã có.
- WBS hướng "none" không còn `ai_engineer`; lịch mặc định bắt đầu từ mốc khách; `warning` có thể chứa
  "trễ hơn mốc khách".