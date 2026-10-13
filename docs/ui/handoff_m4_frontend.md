# Handoff — Frontend-dev Màn 4 Yêu cầu & câu hỏi

Ngày: 2026-10-11  
Vai trò: frontend-dev, vòng sửa CAO/TB sau QA  
Phạm vi: chỉ Màn 4, không sửa backend và không chuyển sang màn khác.

## Đã sửa

- `frontend/src/components/ClarifySection.tsx`
  - Số thứ tự câu hỏi liên tục giữa các vòng hỏi.
  - Hiển thị nhãn cấu trúc `Câu hỏi N` và `Vì sao hỏi`.
  - Giữ danh sách câu hỏi đã trả lời, hiển thị câu trả lời và trạng thái giả định.
- `frontend/src/components/AttachmentUploader.tsx`
  - Hiển thị loại file backend nhận diện nếu khác loại người dùng chọn.
  - Hiển thị sheet mapping khi backend trả dữ liệu.
  - Giữ trạng thái đọc/lỗi parse, tên file, loại và dung lượng hiện có.
- `frontend/src/pages/BidDetailPage.tsx`
  - Hai nút xuất/nhập Q&A vẫn disabled khi chưa có endpoint.
  - Bổ sung lý do disabled và hướng dẫn trả lời trực tiếp từng câu hỏi.
- `docs/ui/compare_04_yeu_cau.md`
  - Cập nhật cột evidence và phạm vi thay đổi sau vòng sửa.

## Kiểm chứng

- `frontend`: `npm run build` — PASS.
- `frontend`: `npm run test` — PASS, 1 test file và 6 tests passed.
- Sau completeness audit: compare report đã có đủ cột `Đã sửa`, mapping yêu cầu gốc, phân loại blocker và API gap; `api_gaps.md` đã bổ sung các lỗi runtime sample preview/pipeline route.
- Preview: backend startup complete, frontend đang chạy; `/api/health` trả `200 OK`; các endpoint `questions`, `attachments`, `evaluations`, `effort`, `quotation`, `schedule` đã có phản hồi.
- Browser screenshot/DOM: BLOCKED vì Chromium executable không khả dụng; không tạo screenshot giả.
- QA compare đã có ma trận `Đã sửa`: không còn finding CAO/TB nào được xác nhận là lỗi frontend có thể xử lý thêm trong phạm vi contract hiện tại; các mức CAO còn lại là trạng thái kiểm thử BLOCKED.

## Còn lại

- `topic` và `blocking` chưa có trong Question contract: tiếp tục theo dõi trong `docs/ui/api_gaps.md`, không bịa badge Chặn/chủ đề.
- Endpoint xuất/nhập Q&A sheet chưa có: hai nút tiếp tục disabled có giải thích.
- Số requirement đọc được phải lấy từ kết quả parse/backend; không thêm số giả vào danh sách attachment.
- Các kiểm tra QA vẫn BLOCKED cho tới khi chạy lại được browser ở `1440x900`.
- Cần tester chạy lại các kiểm tra runtime sau khi có Chromium; cần backend-dev xử lý các API gap trước khi đánh giá badge Chặn/chủ đề và xuất/nhập Q&A.

## Điểm dừng

Bước frontend-dev Màn 4 hoàn tất. Dừng tại workflow boundary; không thực hiện tester, backend-dev, reviewer hoặc các màn 3/5/6.
