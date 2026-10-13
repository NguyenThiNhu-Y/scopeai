# Handoff Màn 10 — Frontend

## Boundary

- Chỉ sửa trang Cài đặt (Màn 10), không sửa Màn 2 hay màn khác.
- Không đổi backend/API contract; giữ `LLM_PROVIDER=mock`.

## Đã làm

- Thay textarea YAML bằng ba bảng nhập dữ liệu nghiệp vụ:
  - effort: hướng giải pháp và min/max theo PoC, MVP, Production;
  - đơn giá: vai trò, offshore/onsite, overhead PM/BrSE, tỷ giá VND/JPY;
  - hệ số: tên, giá trị, lý do, trần hệ số.
- Parse dữ liệu từ `yaml_preview` theo đúng field backend đang trả, không thêm field giả.
- Mỗi tab có nút lưu riêng, dựng YAML và gọi `PUT /api/settings/{key}` hiện có.
- Validation tiếng Việt trước khi lưu: số hợp lệ, số dương cho đơn giá, min không vượt max, lý do hệ số bắt buộc.
- Overhead PM/BrSE và tỷ giá VND/JPY được parse đúng từ YAML, validate trước khi lưu và ghi ngược vào YAML payload của bảng đơn giá.
- Thêm `Xem YAML thu gọn` dạng read-only để kiểm tra payload; bỏ nhãn `M8 · Quản trị`.
- Giữ loading/error/retry, thông báo thành công và trạng thái lỗi; thêm caption/label cho accessibility.

## Kiểm chứng

- `frontend/npm run build`: PASS sau completeness audit.
- `frontend/npm run test -- --run`: PASS, 6/6 tests.
- Preview/browser: chưa có screenshot thật hoặc DOM runtime evidence vì Chromium unavailable trong môi trường kiểm tra; không tạo ảnh giả.

## Tài liệu

- So sánh chi tiết: `docs/ui/compare_10_cai_dat.md`.
- Không phát sinh API gap: API hiện có đủ để lưu từng bảng bằng YAML payload. Nếu cần backend trả JSON schema trực tiếp để bỏ parse YAML phía frontend, đó là cải tiến contract ngoài phạm vi này.

## Trạng thái

**Frontend Màn 10 complete for source/build/test, browser QA BLOCKED.** Bàn giao tester chạy Preview với dữ liệu mock để xác nhận visual, nhập liệu, validation và PUT thật, bao gồm overhead/tỷ giá.
