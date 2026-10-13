# Handoff Đợt 11 — Frontend

Ngày: 2026-10-12. Phạm vi: A, B, C frontend sau fan-out song song.

## Đã triển khai

- A: `SettingsPage` có đúng 5 tab tiếng Việt: Công ty, Template, Nội dung chuẩn, Case study, Tiêu chí Bid/No-bid. Các tab đọc/lưu qua `/api/settings`, hỗ trợ payload object/list, chỉnh sửa case study, nội dung vi/en/ja và validation tổng trọng số đúng 100%.
- B: `ApprovalsPage` nối bid qualification, deal stage và proposal versions. Hiển thị điểm gợi ý là tham khảo, yêu cầu người xác nhận, lưu quyết định, tạo phiên bản, đánh dấu đã gửi và ngày gửi.
- C: `ProposalPage` bắt buộc chọn ngôn ngữ trước khi soạn, render translations theo section, báo fallback khi thiếu bản dịch, gọi endpoint dịch và có tài liệu A4 gồm bìa, mục lục, nội dung và nút in.

## File chính

- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/pages/ApprovalsPage.tsx`
- `frontend/src/pages/ProposalPage.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/api/types.ts`
- `frontend/src/index.css`
- `frontend/src/App.test.tsx`

## Verification

- `cd frontend && npm run build`: PASS.
- `cd frontend && npm test -- --run`: **14 passed**.
- Không gọi LLM thật; UI dùng API root-relative.
- QA đã xác minh trên Preview qua API: settings contract, validation Bid/No-bid, deal stage hợp lệ, chuỗi version `1.0 → 1.1 → 2.0`, sent date/note, translation và metadata A4. CRUD trực quan, fallback từng section và thao tác in vẫn chưa thể xác nhận vì thiếu browser executable.

## Rủi ro và trạng thái QA

- `SettingsPage` lưu payload bằng JSON string theo contract `yaml_content`; API settings đã được kiểm tra trả đúng object/list payload, nhưng thao tác UI CRUD chưa thể xác nhận do thiếu browser.
- `ApprovalsPage` gọi `getHistory({ bid_id: id })` để tải lịch sử của hồ sơ hiện tại; API Preview đã được gọi theo scope này.
- Proposal translation dùng API client chung; endpoint translation đã trả đủ section `en`; cập nhật cache và nút dịch trên UI chưa thể xác nhận do thiếu browser.
- Ghi chú phiên bản gửi khách đã có `sent_at` và `sent_note`; API đã xác minh lưu/trả đúng, hiển thị UI chưa thể xác nhận do thiếu browser.

## Bổ sung sau review

- Phiên bản gửi khách hiện lưu/trả `sent_at` và `sent_note`; UI có ô nhập ghi chú và hiển thị ghi chú đã lưu.
- API client có `translateProposal`; Proposal chỉ cho sửa ngôn ngữ gốc để tránh PUT ghi đè bản dịch khi backend chưa có endpoint sửa translation riêng.
- `getHistory` truyền `bid_id` để chỉ tải lịch sử của hồ sơ hiện tại.

## DONE

Frontend A/B/C compile và test sạch; QA đã kiểm tra API Preview và ghi kết quả tại `docs/ui/dot11_check.md`; kiểm chứng browser vẫn bị Blocked do thiếu browser executable.
