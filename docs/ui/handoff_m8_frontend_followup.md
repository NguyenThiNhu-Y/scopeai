# Handoff Màn 8 — Frontend follow-up

## Trạng thái

**Frontend follow-up đã sửa các mục CAO/TB có thể xử lý bằng code; browser QA vẫn BLOCKED do Chromium unavailable.**

## Đã đọc và đối chiếu

- Đã đọc `AGENTS.md`, `docs/ui/compare_08_proposal.md`, `docs/ui/review_ui_tung_man.md` và handoff Màn 8 trước khi sửa.
- Đã dùng vibegraph MCP trước khi đọc source để tìm `ProposalPage`, `MarkdownView` và `ExportButtons`.
- Giữ đúng phạm vi Màn 8; không sửa Màn 7, Màn 9, Màn 2, Màn 10 hoặc backend.

## Thay đổi

- `frontend/src/pages/ProposalPage.tsx`
  - Cải thiện `MarkdownBlock` để heading có thể chứa đoạn văn, danh sách hoặc bảng mà không làm mất cấu trúc render.
  - Render `[Presales điền]` thành nhãn vàng semantic bằng `mark`, không thay đổi dữ liệu hoặc price gate.
  - Thêm trạng thái `markdownDownloading`, khóa nút `.md` trong lúc tạo file và hiển thị `Đang chuẩn bị…`.
  - Reset trạng thái thông báo Copy trước mỗi lần thử để phản ánh đúng kết quả lần thao tác hiện tại.
- Không thêm dữ liệu proposal, giá, bản dịch hoặc API contract mới.
- Không phát sinh API gap mới; gap bản dịch nhiều ngôn ngữ vẫn ghi tại `docs/ui/api_gaps.md`.

## Kiểm chứng

- `frontend`: `npm run build` — PASS.
- `frontend`: `npm run test` — PASS, 1 test file, 6 tests passed.
- Preview stack đã rebuild; backend và frontend ở trạng thái Up.
- Preview stack đã rebuild lại sau bổ sung nhãn vàng placeholder; backend và frontend vẫn ở trạng thái Up.
- Preview log trước lần rebuild cuối xác nhận `GET /api/bids/96/proposal` trả `200 OK`; lần rebuild cuối không có browser để tạo assertion mới.
- Chromium vẫn unavailable (`BrowserType.launch: Executable doesn't exist`), vì vậy chưa có screenshot current, DOM runtime assertion, click/input assertion, clipboard/download assertion hoặc browser console capture.
- Không tạo screenshot giả và không đánh dấu browser-dependent items là Pass.

## Cập nhật QA

- Đã cập nhật `docs/ui/compare_08_proposal.md`:
  - cột `Đã sửa` của QA08-01 và QA08-02 phản ánh đúng các code fix, gồm cả nhãn vàng placeholder;
  - giữ rõ blocker browser cho Markdown render, edit live preview, copy, download, language tabs, placeholder styling và console;
  - kết luận vẫn là `CHANGES REQUIRED / QA BLOCKED` cho phần nghiệm thu browser, không phải source failure.

## Ranh giới

- Không bắt đầu tester, Màn 9, Màn 2, Màn 10, backend-dev hoặc reviewer.
- Dừng tại boundary frontend follow-up Màn 8.
