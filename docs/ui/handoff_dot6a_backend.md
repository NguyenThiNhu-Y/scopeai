# Handoff — Dot 6a backend

Ngày: 2026-10-11  
Vai trò: backend parallel coordinator

## Trạng thái

**DONE — Dot 6a items 1–4 đã hoàn tất ở backend, contract và focused tests; sẵn sàng chuyển frontend.**

## Báo giá và lịch

- `backend/app/models/quotation.py` và `backend/app/schemas/api_schemas/quotation.py` hỗ trợ:
  - Trọn gói (`fixed_price`), T&M (`tm`) và ODC (`odc`)
  - VND, JPY, USD
  - Dự phòng, onsite và price-to-win trong khoảng `-50..200`
  - T&M theo tháng và ODC theo FTE × tháng
- `backend/app/services/quotation_engine.py` tính lại hoàn toàn bằng code, gồm ngân sách lấy từ intake,
  quy đổi cùng tiền tệ, chênh lệch phần trăm và gợi ý điều chỉnh.
- Price gate tiếp tục dùng `ensure_unlocked`; hồ sơ đã khóa không thể sửa báo giá/lịch.
- Schedule có khoảng go/no-go mặc định 10 ngày làm việc, interval Gantt `day|week|month`,
  ngày bắt đầu sớm nhất của MVP và Production theo dữ liệu lịch khách, cùng
  `go_no_go_start`/`go_no_go_end` để Gantt thể hiện khoảng nghỉ sau PoC.
- Các thay đổi liên quan nằm trong `backend/app/models/schedule.py`,
  `backend/app/schemas/api_schemas/schedule.py` và `backend/app/services/schedule_service.py`.

## Q&A và email

- `backend/app/api/routers/questions.py`:
  - `GET /api/bids/{id}/questions/export` xuất workbook theo ngôn ngữ khách, gồm mã câu hỏi,
    câu hỏi, lý do và câu trả lời; cột trả lời được tô vàng.
  - `POST /api/bids/{id}/questions/import` đọc workbook mới hoặc định dạng tám cột cũ,
    kiểm tra mã câu hỏi thuộc hồ sơ, gộp câu trả lời và resume từ bước `gap`.
  - `POST /api/bids/{id}/questions/email-draft` trả email nháp theo ngôn ngữ khách.
    Tên khách và người gửi do code điền; nội dung do người dùng chỉnh sửa được.
- `backend/app/schemas/llm_schemas/email_draft.py` định nghĩa output có cấu trúc.
- `backend/app/llm/mock_client.py` có fixture email cho `vi`, `en`, `ja`; không gọi LLM thật.
- Prompt email được mask PII trước khi gửi qua gateway; output được validate bằng Pydantic.

## Contract

- Đã cập nhật `docs/04_architecture/api_contract.md` cho báo giá/lịch, Q&A export/import và email draft.
- Frontend cần dùng API root-relative `/api/...`, không hardcode URL localhost.

## Verification

- Pricing/schedule focused tests: **18 passed** (`test_pricing.py`, `test_pricing_mitsumorisho.py`,
  `test_schedule_update.py`).
- Q&A/email focused tests: **13 passed** (`test_clarifying_questions.py`).
- Python compilation: **pass**.
- Chỉ dùng `LLM_PROVIDER=mock`; không gọi LLM thật và không dùng dữ liệu khách hàng thật.
- Cảnh báo deprecation Starlette/httpx trong nhóm Q&A không ảnh hưởng kết quả.

## Lưu ý cho frontend

- Dùng các trường mới trong `QuotationOut`: `contract_model`, `currency`, `totals.payment_plan`,
  `budget.difference`, `budget.difference_percent` và `budget.adjustment_suggestion_percent`.
- Dùng các trường mới trong `ScheduleOut`: `go_no_go_gap_working_days`, `earliest_mvp_start`,
  `earliest_production_start` và `gantt_break_interval`.
- Sau khi tích hợp, cần kiểm chứng trên Preview bằng mẫu Nhật; chưa có evidence Preview ở bước backend.
- Review follow-up đã bổ sung mốc intake riêng cho MVP/Production, giá trị tiền theo kỳ cho T&M/ODC,
  `FTE × tháng`, fallback contingency cho các mô hình hợp đồng mới và các test contract tương ứng.

## DONE

Đã reconcile handoff dùng chung của hai nhánh backend, giữ lại đầy đủ phạm vi items 1–4 và kết quả test.
Dừng tại boundary backend; không sửa frontend. Lần chạy focused sau các sửa follow-up trước phần
go/no-go cuối đã pass `33` tests; lần chạy sau cùng bị wrapper báo ``No tests collected`` và không tạo
ra bằng chứng mới, nên Preview vẫn là verification bắt buộc ở bước tester.
