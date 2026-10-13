# Handoff QA Màn 4 — Yêu cầu & câu hỏi

Ngày: 2026-10-11  
Vai trò: QA engineer  
Phạm vi: chỉ Màn 4, không sửa source và không thực hiện Màn 3/5/6.

## Deliverables

- Báo cáo đối chiếu: `docs/ui/compare_04_yeu_cau.md`.
- Không có screenshot trong `docs/ui_v3/` vì Chromium executable không khả dụng; không tạo ảnh giả.

## Thực thi

- Đã đọc `docs/ui/review_ui_tung_man.md` và `AGENTS.md` trước khi làm.
- Đã dùng vibegraph MCP trước khi discovery code.
- Preview được khởi động bằng compose; backend có health check `200 OK`, frontend ở trạng thái `Up`.
- Đã thử chạy Playwright ở viewport `1440x900`, nhưng bị Blocked tại bước khởi động browser vì thiếu Chromium executable.
- Không tải browser, không sửa mã nguồn để làm test pass.

## Kết quả

- Tổng số kiểm tra trong compare: 10.
- PASS: 0, vì không có runtime browser evidence để xác nhận.
- FAIL: 0, vì không được phép suy diễn lỗi UI khi chưa quan sát được DOM thật.
- BLOCKED: 9.
- NOT RUN: 1 (`M4-QA-05`, do contract thiếu `topic` và `blocking`).

## Đối chiếu completeness

- Đã bao phủ đủ 4 nhóm nội dung bắt buộc của Màn 4: phân tích yêu cầu, Q&A, file đính kèm và yêu cầu gốc Markdown.
- Đã bao phủ các quy tắc trạng thái loading/rỗng/lỗi trong ma trận kiểm tra.
- Đã ghi rõ LLM mock, hồ sơ mẫu tiếng Nhật, viewport mục tiêu `1440x900`, giới hạn browser và nguyên tắc không tạo ảnh giả.
- Đã phân loại CAO/TB/THẤP; hiện không có mục THẤP riêng vì chưa đủ bằng chứng giao diện để kết luận.
- Đã sửa số liệu tổng hợp để khớp ma trận: 10 ca = 9 BLOCKED + 1 NOT RUN.
- Không có mục nào được đánh dấu PASS hoặc FAIL khi chưa có DOM/screenshot thật.

## Vấn đề cần chuyển tiếp

- `sample_key` trong request sample preview hiện trả `400`; cần backend/Preview owner xác định cách nạp đúng hồ sơ mẫu tiếng Nhật.
- `/api/bids/83/pipeline` trả `404` trong log Preview; cần xác minh route contract.
- Question contract thiếu `topic` và `blocking`.
- Chưa có endpoint export/import Q&A sheet.
- Cần chạy lại QA trên môi trường có Chromium để có screenshot thật, kiểm tra DOM ở `1440x900` và chuyển các ca BLOCKED thành PASS/FAIL có bằng chứng.

## Boundary

QA step complete with a blocked result. Không sửa frontend/backend, không chuyển sang vai trò frontend-dev, backend-dev hoặc reviewer. Dừng tại đây để workflow tiếp theo xử lý.
