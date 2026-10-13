# Handoff — QA Đợt 6a

Ngày: 2026-10-11  
Vai trò: QA tester

## Trạng thái

**DONE — đã kiểm tra trong phạm vi QA; verdict: CHƯA ĐẠT ĐẦY ĐỦ / BLOCKED.**

## Deliverables

- Báo cáo kiểm thử: `docs/ui/dot6a_check.md`.
- Đã dùng vibegraph MCP trước khi discovery code.
- Đã đọc các context file bắt buộc, handoff frontend Đợt 6a và API contract.
- Đã khởi động và kiểm tra Preview stack với `LLM_PROVIDER=mock`.
- Đã ghi số liệu thật của hồ sơ Nhật bid `97` cho quotation/schedule/lock.
- Đã đối chiếu từng yêu cầu gốc trong ma trận acceptance của `docs/ui/dot6a_check.md`.
- Đã phân biệt rõ bằng chứng API với bằng chứng UI; dữ liệu task không được ghi nhận như bằng chứng Gantt.

## Findings cần chuyển tiếp

1. Runtime OpenAPI không có `/questions/export`, `/questions/import` và `/questions/email-draft`, dù contract/handoff frontend yêu cầu các route này. Q&A và email bị Blocked.
2. Quotation runtime của bid `97` chỉ cho thấy `fixed_price`, JPY, dự phòng 20%, tổng `8,085,806 JPY`; budget là `null`, chưa đủ để kiểm tra so sánh ngân sách hoặc các mô hình T&M/ODC.
3. Schedule runtime có ngày `2026-10-26` đến `2027-04-30` nhưng thiếu go/no-go interval và mốc MVP/Production theo intake.
4. Browser Playwright bị Blocked do thiếu Chromium executable; không tạo screenshot/evidence giả.
5. Frontend test 9/9, type-check và build pass. Backend pytest không cho kết quả test hợp lệ, báo `No tests collected`.
6. Báo cáo không coi API task dates là bằng chứng Gantt UI; không có screenshot, file Excel hay Preview result giả.


- Không tạo số liệu, file Excel hoặc screenshot giả.
- Không thực hiện reviewer hoặc sửa blocker backend/frontend.


Đã ghi báo cáo và handoff này; dừng tại boundary QA tester.
