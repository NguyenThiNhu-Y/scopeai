# Fix Log — CRITICAL/HIGH

Ngày: 2026-10-10

## Kết quả

| ID | Trạng thái | Thay đổi | Kiểm chứng |
|---|---|---|---|
| GATE-01 | FIXED WITH MVP LIMITATION | Bổ sung `authorize_bid` để kiểm tra owner/manager; áp dụng cho bid detail, danh sách, pipeline, questions, WBS, attachments, exports và settings. Identity tạo bid/sample lấy từ `get_identity`, không lấy trực tiếp từ body. Các role workflow được phép tiếp tục pipeline theo mô hình header giả lập đã frozen trong API contract; đây chưa phải authentication server production. | Thêm regression test chặn user khác đọc bid. Backend `223 passed`. |
| GATE-02 | FIXED | Upload đọc theo chunk tối đa 1 MiB và dừng tại `MAX_SIZE + 1`, không gọi `await file.read()` không giới hạn. | Regression test upload quá 20 MB; backend `223 passed`. |
| GATE-03 | FIXED | Đổi `FILE_TOO_LARGE` từ HTTP 413 về HTTP 400 theo frozen API contract. | Regression test assert `status_code == 400` và `code == FILE_TOO_LARGE`; backend `223 passed`. |
| GATE-04 | FIXED | CORS chuyển từ wildcard sang allowlist `CORS_ORIGINS`, mặc định development là `http://localhost:5173`; giới hạn methods/headers và bật credentials. | App khởi tạo được trong toàn bộ backend test suite; cấu hình đọc từ env. |
| GATE-15 | NOT FIXED — BLOCKED | Không thể chạy lại Playwright E2E vì runtime hiện thiếu Chromium. Không coi E2E là PASS và không suy diễn kết quả runtime. | Backend unit/integration `223 passed`; E2E vẫn BLOCKED trước điều hướng. Cần runtime có Chromium để xác nhận TC-E2E-01..05. |

## Ghi chú

- Không có phát hiện CRITICAL trong gate report.
- Các finding MEDIUM/LOW không thuộc phạm vi role Developer của bước này và được bàn giao cho bước tiếp theo.
- Verdict vẫn là **NO-GO** cho đến khi E2E TC-E2E-01..05 chạy được và đạt PASS; việc sửa code không thay thế bằng chứng runtime.
