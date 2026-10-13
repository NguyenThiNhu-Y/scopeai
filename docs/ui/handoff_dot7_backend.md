# Handoff — Đợt 7 backend

Ngày: 2026-10-11  
Vai trò: backend-dev  
Phạm vi: mục 3, 5, 6, 7, 8 của Đợt 7

## Trạng thái

**DONE — đã triển khai backend P0 và regression tests pass.**

## Đã triển khai

- `/api/settings` trả thêm `payload` cùng `yaml_preview`, giữ chung dữ liệu chuẩn cho giao diện; effort, rate card và factors vẫn được kiểm tra trước khi lưu bằng code.
- Budget output có `scope_check_required`, cảnh báo tiếng Việt khi chênh quá `±30%`, và `adjustment_suggestion_percent` bị kẹp trong `-30..30`.
- Intake trích mốc bắt đầu/MVP/Production từ các mốc RFP tiếng Nhật; không đưa số tính toán vào LLM. `start_date` của schedule có thể bỏ trống để service dùng mốc bắt đầu khách hàng làm mặc định.
- Schedule không còn đánh giá hay cảnh báo theo `submission_deadline`; `deadline_violation` luôn false ở contract mới và cảnh báo cũ về hạn nộp hồ sơ đã bỏ.
- Proposal schema/backend mock được mở rộng thành đúng 8 section: `introduction`, `requirements_understanding`, `solution_overview`, `approach`, `schedule`, `team`, `assumptions_and_scope`, `risks`. Mock tiếng Nhật/Anh/Việt dùng tiêu đề tương ứng và không tách thêm tiêu đề phụ assumptions/scope.
- Rà soát sau bước đã đồng bộ exporter DOCX/TOC theo 8 mục và bỏ phần assumptions/scope lặp; mock proposal dùng token cho ngân sách, mốc khách, số requirement và hướng giải pháp, sau đó code thay thế token bằng dữ liệu hồ sơ.
- `wbs_service.recalc_schedule` cũng đã bỏ truyền `submission_deadline`; settings payload và budget guard có regression tests riêng.

## Files chính đã sửa

- `backend/app/schemas/api_schemas/settings.py`
- `backend/app/services/settings_service.py`
- `backend/app/services/quotation_engine.py`
- `backend/app/pipeline/steps/b1_intake.py`
- `backend/app/services/schedule_engine.py`
- `backend/app/services/schedule_service.py`
- `backend/app/schemas/api_schemas/schedule.py`
- `backend/app/schemas/llm_schemas/proposal.py`
- `backend/app/schemas/api_schemas/proposal.py`
- `backend/app/services/proposal_service.py`
- `backend/app/pipeline/steps/b6_proposal.py`
- `backend/app/llm/mock_client.py`
- `backend/tests/test_proposal_schema.py`
- `backend/tests/test_schedule.py`
- `backend/tests/test_deadline_warning.py`

## Verification

Focused command trước rà soát gồm settings, pricing, schedule, deadline, proposal và LLM number-schema: **44 passed**. Regression sau rà soát gồm settings, pricing, schedule, proposal, exporter, sample/mock và pipeline context: **54 passed**. Có cảnh báo deprecation Starlette/httpx, không ảnh hưởng kết quả. Một số lần chạy qua wrapper báo `No tests collected`; lần chạy pytest nguyên bản tương ứng đã pass.

Chưa chạy Preview và chưa tạo bằng chứng trình duyệt; tester Đợt 7 cần xác nhận runtime với mẫu Nhật. Frontend cần nối `payload`, dùng `start_date` tùy chọn và hiển thị các field budget/proposal mới.

## Lưu ý cho bước tiếp theo

- Không sửa frontend trong boundary backend.
- Các test cũ kiểm tra trực tiếp cảnh báo hạn nộp hồ sơ đã được chuyển sang hành vi mới: không cảnh báo theo hạn nộp.
- Proposal mock hiện bảo đảm cấu trúc/tiêu đề ngôn ngữ; nội dung runtime cần frontend/tester đối chiếu đủ dữ liệu hồ sơ.

## DONE

Đã tự review các thay đổi backend, ghi handoff này và dừng tại boundary backend.
