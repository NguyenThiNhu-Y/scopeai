# Handoff — Màn 3 Tổng quan

- Đã sửa: frontend/src/pages/BidDetailPage.tsx.
- Đã thay lưới card tổng quan bằng các card có nội dung có cấu trúc: mục tiêu/ràng buộc, hướng giải pháp, khả thi, rủi ro, effort theo giai đoạn, báo giá, thống kê đáp ứng và 3 câu hỏi đầu.
- Đã chuyển ClarifySection khỏi tab Tổng quan để nội dung câu hỏi nằm ở tab Yêu cầu & câu hỏi.
- Dữ liệu thiếu điểm khả thi, độ tin cậy, hướng bị loại và mức độ rủi ro vẫn được hiển thị bằng trạng thái hướng dẫn hoặc danh sách an toàn, không bịa dữ liệu.
- Bổ sung gọi `GET /api/bids/{id}/schedule` và hiển thị số task WBS/ngày kết thúc trong thẻ Effort & kế hoạch.
- Bổ sung `MarkdownPreview` không thêm dependency để render heading, đoạn văn và danh sách trong phần Yêu cầu gốc thu gọn.
- Bổ sung hiển thị dự phòng, chi phí vận hành/tháng, ngân sách và chênh lệch khi quotation API trả về; ánh xạ thống kê đáp ứng sang nhãn nghiệp vụ tiếng Việt.
- Build: npm run build — PASS.
- Test: npm run test — 6 tests PASS.
- Follow-up build: `npm run build` — PASS.
- Follow-up test: `npm run test` — 1 file, 6 tests PASS. Có cảnh báo console hiện query schedule undefined trong mock test, nhưng không làm test thất bại.
- Chưa chạy lại Preview/chụp ảnh trong step này; Chromium vẫn chưa có bằng chứng browser từ handoff QA trước đó.
