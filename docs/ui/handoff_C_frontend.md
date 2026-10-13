# Handoff — Mục C Proposal frontend

Ngày: 12/10/2026

## Đã làm

- Proposal bắt buộc chọn `vi/en/ja` trước khi soạn; khi chưa chọn không hiện vùng soạn/nội dung.
- Khi chọn ngôn ngữ, nội dung toàn bộ section lấy từ `translations`; section thiếu được fallback về bản gốc và báo rõ.
- Khi chưa có bản dịch, hiển thị nút `Dịch sang ...` và gọi `POST /api/bids/{id}/proposal/translate` bằng root-relative URL. Không sửa API client/types dùng chung.
- Thêm `Xem dạng tài liệu`: overlay tài liệu A4 có bìa, mục lục theo tám section, nội dung printable, nút in và đóng. Metadata chỉ dùng mã hồ sơ/ngôn ngữ thực có; không tự dựng tên khách, ngày hay giá.
- Thêm CSS print A4, page-break cho bìa/mục lục và responsive document view.

## Kiểm tra

- Trước khi thay đổi C, `frontend/npm test` và `frontend/npm run build` đều pass.
- Sau thay đổi C, `npm run build` vẫn pass. Lần chạy test cuối bị 2 test cũ ở WBS/Settings fail trong workspace đang được các agent khác sửa đồng thời (không liên quan file C); 12/14 test pass. Cần chạy lại sau khi workspace hội tụ.

## Phạm vi file

- `frontend/src/pages/ProposalPage.tsx`
- `frontend/src/index.css`
