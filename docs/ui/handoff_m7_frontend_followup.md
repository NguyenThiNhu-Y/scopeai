# Handoff — Frontend follow-up Màn 7 Đáp ứng yêu cầu

Ngày: 2026-10-11  
Vai trò: frontend-dev follow-up  
Trạng thái: **DONE — không còn lỗi CAO/TB đã xác nhận; các mục còn lại bị blocker browser hoặc API gap**

## Phạm vi

- Chỉ sửa `frontend/src/components/RequirementMatrix.tsx`.
- Không sửa backend, không bật selector ngôn ngữ khi API chưa hỗ trợ, không làm Màn 8/Màn 9 hoặc các node khác.

## Đã sửa

- Giữ nguyên bộ lọc, badge và empty state theo contract hiện có.
- Bổ sung `caption` cho bảng và `scope="col"` cho các tiêu đề cột.
- Bổ sung `aria-label` cụ thể cho hai nút export.
- Đồng bộ nhãn nút chính với prompt Màn 7: `Điền ○/△/× vào file Excel của khách`.
- Bổ sung `aria-busy` cho vùng ma trận và `role="status"`/`aria-live` cho trạng thái tạo file.
- Hiển thị trạng thái tạo file nhất quán trên cả hai nút export.
- Trì hoãn thu hồi object URL đến tick tiếp theo để tránh thu hồi URL trước khi trình duyệt bắt đầu download.
- Loại bỏ state không có tác dụng khỏi selector ngôn ngữ; selector vẫn disabled và ghi rõ lý do vì backend chưa nhận `note_language`.
- Cập nhật cột `Đã sửa` trong `docs/ui/compare_07_dap_ung.md`.

## API gap giữ nguyên

- `GET /api/bids/{id}/exports/requirements.xlsx` chưa nhận `note_language`.
- Gap đã được ghi trong `docs/ui/api_gaps.md`; không bịa nội dung file theo ngôn ngữ được chọn.

## Verification

- `frontend`: `npm run build` PASS.
- `frontend`: `npm run test` PASS, 1 test file và 6 tests passed.
- Preview/browser: vẫn BLOCKED theo tester handoff vì thiếu Chromium executable. Do đó chưa tuyên bố đã xác minh DOM, click thật, screenshot 1440x900 hoặc console runtime.
- Không tạo screenshot giả.

## Boundary

Đã dừng tại frontend follow-up Màn 7. Node tester cần chạy lại browser khi Chromium khả dụng; không tiếp tục sang Màn 8, Màn 9, Màn 2, Màn 10, backend aggregation, full-flow hoặc reviewer.
