# Handoff Màn 8 — Tester

## Trạng thái

**Step tester Màn 8 hoàn tất với kết quả QA BLOCKED / CHANGES REQUIRED.**

## Đã kiểm tra

- Đã đọc `AGENTS.md`, `docs/ui/review_ui_tung_man.md` và `docs/ui/handoff_m8_frontend.md` trước khi kiểm tra.
- Đã dùng vibegraph MCP trước khi truy cập source để xác định `ProposalPage` và call chain liên quan.
- Preview stack đang chạy; backend log có request thành công tới `GET /api/bids/92/proposal`.
- Hồ sơ mẫu Nhật hư cấu được xác nhận qua Preview API: `customer_language=ja`, `display_currency=JPY`, nội dung proposal gồm các section tiếng Nhật, có `assumptions_phrased`, `scope_out_phrased`, `editable=true` và placeholder giá.
- Đã đối chiếu các yêu cầu: Markdown render, placeholder quotation, language tabs, download/edit controls, assumptions/out-of-scope, loading/empty/error và console.
- Báo cáo chi tiết nằm tại `docs/ui/compare_08_proposal.md`.

## Blocker và evidence

- Playwright không khởi động được vì Chromium executable không tồn tại trong môi trường.
- Vì vậy không có screenshot thật, DOM runtime assertion, click interaction, download assertion hoặc browser console capture.
- Không tạo screenshot giả và không sửa app source để làm test pass.
- Evidence source/API được ghi riêng và không thay thế cho browser evidence.
- Không có ảnh current để đối chiếu trực quan với `ui_reference/08_proposal_ho_so.png`; báo cáo đã ghi rõ giới hạn này thay vì coi source/API là ảnh hiện tại.

## Mục cần xử lý ở bước tiếp theo

- Chạy lại QA trên Preview khi browser khả dụng ở 1440×900.
- Xác nhận trực tiếp Markdown headings/lists/tables, nhãn `[Presales điền]`, tab language, edit two-column live preview, cảnh báo và khóa lưu khi xóa `{{QUOTATION}}`, các nút download/copy, loading/error và console; chụp current screenshot 1440×900 để đối chiếu reference.
- Giữ nguyên API gap: API hiện chỉ trả một bộ `sections`, không được coi tab ngôn ngữ là bản dịch.

## Ranh giới

- Không sửa code frontend/backend.
- Không bắt đầu Màn 9, Màn 2, Màn 10, backend-dev, final tester hoặc reviewer.
- Dừng tại boundary của node tester Màn 8.
