# Handoff — QA Đợt 8

Ngày: 2026-10-11  
Vai trò: QA / tester

## Trạng thái

**DONE với phát hiện cần sửa — đã ghi báo cáo QA tại `docs/ui/dot8_check.md`.**

## Đã kiểm tra

- Đọc `AGENTS.md`, `docs/ui/review_luot4.md` mục 1, handoff backend/frontend Đợt 8 và ảnh reference/current được chỉ định.
- Khởi động Preview bằng `podman-compose.preview.vibeflow.yaml`; backend/frontend đều chạy và frontend production build thành công.
- Chạy mẫu Nhật qua API thật:
  - Tạo sample `ja_email`: `201`, `customer_language=ja`, `display_currency=JPY`.
  - Parse: `200`, 36 requirement, có requirement file.
  - Confirm parse: `200`.
  - Start pipeline: `202`.
  - Pipeline dừng ở `waiting_clarification` với 5 câu hỏi vòng 1, mỗi câu có `reason_vi`.
  - Downstream effort/quotation/schedule/WBS trả `409 STATE_CONFLICT` phù hợp với trạng thái chưa trả lời câu hỏi/chưa có WBS.
- Backend test suite: **PASS**.
- Frontend test suite: **11 passed**.
- Frontend build: **PASS**.
- Chạy browser QA bằng Chromium bundled và tạo evidence thật trong `docs/ui_current/`.
- Xác minh render trang Tạo hồ sơ và chọn mẫu Nhật: tiền tệ là `JPY`.
- Xác minh render tab Kế hoạch: có khu vực nhân sự/lịch và cấu trúc công việc.

## Finding

- Tab Proposal trên hồ sơ mẫu render rỗng và phát sinh `TypeError: Cannot read properties of undefined (reading 'split')` khi section proposal thiếu dữ liệu. Evidence: `docs/ui_current/dot8_proposal_runtime.png` và `docs/ui_current/runtime_report.json`.
- Không sửa app source để làm test pass; frontend-dev cần xử lý lỗi này.

## Blocked / chưa chứng minh

- Chưa chạy được các tương tác sâu: import file thật, trả lời câu hỏi và tạo vòng 2, staffing save/recalculation, WBS edit/add/delete/save, payment detail, price gate.
- Chưa xác minh đầy đủ KPI sau pipeline hoàn tất và solution/effort/schedule sau khi vượt vòng hỏi.
- API danh sách chưa trả stats theo trạng thái.

## Handoff cho reviewer

- Đọc `docs/ui/dot8_check.md` để xem bảng 17 test case, kết quả và command evidence.
- Reviewer cần quyết định trạng thái release dựa trên lỗi Proposal, các case chưa chứng minh và gap stats backend được nêu trong báo cáo.
- Đây là boundary QA; không thực hiện review code hoặc cập nhật `docs/ui/dot8_review.md`.

## DONE

Đã hoàn tất vai trò QA, ghi nhận trung thực Pass/Blocked và dừng tại workflow boundary.
