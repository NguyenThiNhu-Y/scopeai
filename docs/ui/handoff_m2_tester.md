# Handoff Màn 2 — Tester

## Boundary

- Chỉ kiểm tra Màn 2 Danh sách hồ sơ trên Preview.
- Không sửa code, không kiểm tra Màn 10 hoặc flow tổng.

## Trạng thái kiểm tra

- Chưa thể tạo screenshot/DOM/console evidence thật trong lượt frontend này.
- Automated evidence hiện có: `frontend npm run test` PASS 6/6.
- Cần tester chạy Preview với `LLM_PROVIDER=mock`, kiểm tra viewport 1440×900 và 1280×800, row click, keyboard Enter/Space, search, status filter, loading/error/empty và deadline ≤7 ngày.
- Không được tạo ảnh placeholder; nếu Chromium không khả dụng, ghi rõ blocker tương tự các handoff tester trước.

## Acceptance focus

1. Các cột mới không làm status xuống dòng.
2. Ngày hạn gần có màu cảnh báo và vẫn đọc được ngày đầy đủ.
3. Các cột thiếu contract hiển thị unavailable, không có số liệu tự dựng.
4. Row có focus rõ và mở đúng `/bids/{id}` bằng click/keyboard.
5. Bố cục responsive dùng scroll ngang có chủ đích thay vì làm vỡ bảng.

## Handoff status

**Tester chưa thực hiện runtime verification trong lượt này.** Chờ Preview/browser evidence thật; compare hiện tại ở `docs/ui/compare_02_danh_sach.md` phân biệt rõ phần đã sửa và blocker API.
