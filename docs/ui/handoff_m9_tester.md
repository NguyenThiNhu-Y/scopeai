# Handoff Màn 9 — Tester

## Boundary

- Vai trò: QA/tester, Đợt 3.
- Chỉ kiểm tra Màn 9 trên Preview và ghi nhận evidence.
- Không sửa frontend/backend, không xử lý các màn khác, không chạy final flow hoặc reviewer.
- Không dùng git command.

## Đã kiểm tra

- Đọc `AGENTS.md`, `docs/ui/review_ui_tung_man.md` và `docs/ui/handoff_m9_frontend.md` trước khi kiểm tra.
- Preview health đạt `status=ok`, `database=ok`, `llm_provider=mock`.
- Tạo hồ sơ mẫu Nhật `#97` qua `POST /api/bids/sample` với sample key `ja_email`; hồ sơ tạo ở trạng thái `draft` với file RFP `.docx` và Excel requirement.
- Parse và confirm hồ sơ Nhật: đọc được `36` requirement; cả hai attachment có trạng thái `ok`.
- Chạy pipeline mock và trả lời hai vòng câu hỏi tiếng Nhật; hồ sơ Nhật đạt trạng thái `waiting_tech_approval`.
- Kiểm tra thực tế các API summary cho hồ sơ Nhật `#97`: bid, evaluations, effort, schedule, questions, quotation và history.
- Kết quả hồ sơ Nhật: `36/36` requirement evaluated, effort midpoint `434.7`, currency `JPY`, quotation grand total `8,085,806`, schedule warning vượt hạn.
- Kiểm tra gate giá trên hồ sơ Nhật: gọi duyệt giá trước duyệt kỹ thuật trả HTTP `409 STATE_CONFLICT` với thông báo `Hồ sơ chưa qua duyệt kỹ thuật`.
- Kiểm tra validation nhận xét trên hồ sơ Nhật: gửi technical rejection với nhận xét rỗng trả HTTP `400 VALIDATION_ERROR`, thông báo `Từ chối duyệt kỹ thuật phải có lý do`; không làm thay đổi trạng thái hồ sơ.
- Dùng vibegraph MCP trước khi tra cứu symbol/source; xác nhận `ApprovalsPage`, `approveTech`, `approvePrice`, route approval và sample route.

## Browser / screenshot status

- Playwright được thử chạy theo webapp-testing skill nhưng Chromium không khả dụng:
  `BrowserType.launch: Executable doesn't exist ... chromium_headless_shell-1187`.
- Không có screenshot thật, không có DOM/click evidence, không có console runtime evidence.
- Không tạo ảnh giả hoặc tuyên bố visual pass.

## Deliverable

- `docs/ui/compare_09_quy_trinh_duyet.md`
  - Ghi bảng kết quả theo CAO/TB/THẤP.
  - Ghi evidence API thật và blocker browser.
  - Ghi rõ gate giá đạt ở backend nhưng browser disabled state chưa xác nhận.
  - Ghi gap phiên bản gửi khách và giới hạn validation nhận xét.

## Handoff status

**Màn 9 tester complete with BLOCKED visual/browser evidence.** Hồ sơ Nhật đã được đưa tới trạng thái chờ duyệt kỹ thuật; API contract, gate duyệt giá và validation nhận xét đã được kiểm tra đúng hồ sơ. Cần chạy lại browser QA trong môi trường có Chromium để xác nhận ảnh mẫu, layout, click flow, thuộc tính validation trên UI và console. Dừng tại boundary tester.
