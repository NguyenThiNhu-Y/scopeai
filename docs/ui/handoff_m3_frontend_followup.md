# Handoff — Màn 3 Tổng quan, sửa CAO/TB

- Phạm vi: chỉ xử lý follow-up frontend Màn 3 theo `docs/ui/compare_03_tong_quan.md`; không triển khai Màn 4–6.
- Đã sửa `frontend/src/pages/BidDetailPage.tsx`:
  - Card `Effort & kế hoạch` gọi `GET /api/bids/{id}/schedule` và hiển thị số task WBS cùng ngày kết thúc.
  - Phần `Yêu cầu gốc của khách` vẫn thu gọn bằng `details`, đồng thời render Markdown tối giản cho heading, đoạn văn và danh sách.
- Không bịa dữ liệu: độ tin cậy, hướng bị loại, điểm khả thi và mức độ/type/mitigation của rủi ro vẫn được ghi là blocker API/schema trong `docs/ui/api_gaps.md`.
- Đã cập nhật `docs/ui/compare_03_tong_quan.md`: M3-06 và M3-10 đánh dấu đã sửa; M3-03/04/05 ghi rõ blocked bởi API/schema; không còn mục CAO.
- Đã cập nhật `docs/ui/api_gaps.md`: loại bỏ ghi chú M3-06 đã lỗi thời.
- Kiểm tra tự động sau audit:
  - `frontend/npm run build`: PASS.
  - `frontend/npm run test`: PASS, 1 file / 6 tests.
  - Fixture Màn 3 đã trả một `ScheduleResponse` hợp lệ; không còn cảnh báo query schedule trả `undefined`.
- Cảnh báo còn lại chỉ là React Router future-flag warning từ các smoke test hiện có, không liên quan thay đổi Màn 3.
- Preview/browser: chưa có ảnh hoặc DOM mới; theo QA trước, Chromium không khởi động được trong sandbox. Không tạo ảnh giả.
- Trạng thái: Màn 3 frontend follow-up hoàn tất. Không còn mục CAO; blocker TB còn lại là M3-13 (chưa thể xác minh browser/pixel trong sandbox) và các blocker API/schema M3-03/04/05.
