# Handoff Màn 8 — Frontend Proposal & hồ sơ

## Phạm vi

- Chỉ sửa tab Proposal & hồ sơ trong `frontend/src/pages/ProposalPage.tsx`.
- Giữ các export backend hiện có: Word, Excel ước tính, PDF, Excel requirement và ZIP.
- Không thay đổi backend contract, không gọi LLM thật và không tạo dữ liệu/screenshot giả.

## Đã triển khai

- Bỏ tiêu đề lớn `Proposal` lồng trong tab; giữ tiêu đề khu vực theo ngữ cảnh nghiệp vụ.
- Đưa `Tải .md` thành một thẻ tải file cùng kiểu với các thẻ export còn lại.
- Render nội dung proposal thành tài liệu Markdown có cấu trúc:
  - heading cấp 2;
  - danh sách gạch đầu dòng;
  - bảng Markdown;
  - in đậm inline cơ bản.
- Dòng `{{QUOTATION}}` được thay bằng `quotation_markdown` khi giá đã qua gate hoặc `[Presales điền]` khi chưa được duyệt.
- Đưa `assumptions_phrased` và `scope_out_phrased` vào thân proposal dưới các mục `Giả định` và `Ngoài phạm vi` (đổi nhãn theo ngôn ngữ đang xem), bỏ hai thẻ riêng bên dưới.
- Chế độ `Chỉnh sửa` hiển thị các section theo dạng 2 cột trên màn hình rộng và có preview Markdown khi thoát chế độ sửa.
- Trong chế độ chỉnh sửa, cột trái là soạn nội dung và cột phải là preview Markdown cập nhật theo draft.
- Hiển thị cảnh báo và khóa lưu nếu người dùng xóa toàn bộ dòng `{{QUOTATION}}`.
- Thêm trạng thái lưu, copy và tải file; trì hoãn revoke object URL để tránh hủy URL trước khi trình duyệt bắt đầu download.
- Nút `Copy Markdown` dùng nội dung proposal đã ghép đầy đủ placeholder/giả định/ngoài phạm vi.

## Contract/API

- Dùng đúng `ProposalDraft` hiện có: `sections`, `assumptions_phrased`, `scope_out_phrased`, `price_gate`, `editable`, `quotation_markdown`.
- Dùng đúng `downloadExport(id, kind)` cho 5 loại file hiện có.
- Ghi thêm API gap về bản dịch nội dung theo ngôn ngữ tại `docs/ui/api_gaps.md`; UI không giả lập nội dung dịch khi backend chỉ trả một bộ section.

## Kiểm chứng

- `frontend`: `npm run build` — PASS after completeness review.
- `frontend`: `npm run test` — PASS after completeness review, 1 test file, 6 tests passed.
- Preview stack đã được khởi động bằng `podman-compose.preview.vibeflow.yaml`; backend và frontend đang ở trạng thái `Up`.
- Chưa có browser/Chromium evidence trong bước này, nên chưa xác nhận bằng screenshot các tiêu chí pixel, thao tác click thực tế, console browser hoặc download trong trình duyệt. Không tạo screenshot giả.
- Completeness review đã xác nhận không có lỗi build/test; phần còn lại cần tester xác nhận trên Preview là hành vi click/render thực tế.

## Ranh giới bước

- Không sửa Màn 7, Màn 9, Màn 2, Màn 10, backend hoặc bước tester/reviewer tổng.
- Node frontend Màn 8 hoàn tất; bước tiếp theo chỉ tiếp tục khi workflow giao node kế tiếp.
