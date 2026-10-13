# Handoff — Proposal, phê duyệt và cài đặt

## Đã triển khai

- `frontend/src/pages/ProposalPage.tsx`: thêm các export card Word/Excel requirement/PDF/ZIP dùng API hiện có; preview Markdown theo ngôn ngữ `Tiếng Việt | English | 日本語`; sửa nội dung theo chế độ 2 cột, copy Markdown, tải `.md`; thay `{{QUOTATION}}` bằng bảng giá sau duyệt hoặc `[Presales điền]`.
- Giữ API root-relative và không tự tính số liệu; export vẫn đi qua `downloadExport`.
- `ApprovalsPage` không thay đổi hành vi API. Có một khai báo nhãn trạng thái thử nghiệm đã được loại bỏ vì trang hiện tại vẫn render flow cũ; việc đổi raw enum thành nhãn đầy đủ cần bước riêng để tránh chạm file chung của agent khác.

## Kiểm tra

- `frontend`: `npm run build` PASS.
- `frontend`: `npm run test -- --run` còn 1 test fail hiện hữu ở smoke test BidDetailPage: không tìm thấy câu hỏi Nhật `ご要望のデータ件数は？`; lỗi nằm ở trạng thái/mock hiển thị câu hỏi, không phải compile của phần Proposal.

## Khoảng trống / xung đột

- Không chạy Preview trong step này.
- `SettingsPage`, tạo hồ sơ và danh sách đã có nền tảng từ handoff trước; không sửa để tránh xung đột file với agent khác.
