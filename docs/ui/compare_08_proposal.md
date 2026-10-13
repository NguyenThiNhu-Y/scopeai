# QA Màn 8 — Proposal & hồ sơ

## Phạm vi và môi trường

- Ngày kiểm tra: 2026-10-11.
- Môi trường: Preview stack trong workspace, `LLM_PROVIDER=mock`.
- Hồ sơ mẫu: hồ sơ Nhật hư cấu từ endpoint preview, `customer_language=ja`, `display_currency=JPY`.
- Bằng chứng API: `GET /api/bids/92/proposal` trả 5 section tiếng Nhật, `price_gate=placeholder`, `editable=true`, `quotation_markdown=[Presales điền]`, cùng `assumptions_phrased` và `scope_out_phrased`.
- Bằng chứng source: `frontend/src/pages/ProposalPage.tsx` đã được tra qua vibegraph; component có `MarkdownView`, tab ngôn ngữ, export Markdown, edit preview hai cột và cảnh báo thiếu `{{QUOTATION}}`.
- Follow-up frontend cuối: renderer Markdown đã xử lý heading kèm block list/bảng/đoạn văn, placeholder `[Presales điền]` được render thành nhãn vàng, nút tải `.md` có trạng thái đang chuẩn bị và khóa trong lúc tải, trạng thái Copy được reset trước mỗi lần thử.
- Browser: **BLOCKED**. Playwright không khởi động được vì Chromium executable không tồn tại trong môi trường (`BrowserType.launch: Executable doesn't exist ... chromium_headless_shell...`). Không tạo ảnh giả.
- Ảnh đối chiếu current: **không có** vì browser bị Blocked; không dùng ảnh source/API để thay thế ảnh current và không tạo ảnh giả. Ảnh reference được nêu trong spec là `ui_reference/08_proposal_ho_so.png`.

## Kết quả tổng hợp

| Hạng mục | Đối chiếu reference/current | Kết quả | Mức độ | Evidence |
|---|---|---|---|---|
| Hàng tải file | Reference yêu cầu Word, Excel ước tính, PDF, Excel requirement, ZIP đồng kiểu và `.md` là thẻ/nút cùng kiểu. Source có `ExportButtons` và thẻ `Proposal Markdown`. | **Blocked**: chưa click/quan sát trực tiếp trên browser. | TB | `ProposalPage.tsx:108-113`; browser blocked |
| Markdown render | Reference yêu cầu heading, bảng, danh sách, nền giấy trắng; source dùng `MarkdownView` trong article `Nội dung Markdown`. Follow-up đã sửa parser để không yêu cầu cả block phải cùng loại khi heading chứa list/bảng/đoạn văn. | **Source fix complete; browser verification blocked**: chưa xác nhận DOM sau React render. | CAO | `ProposalPage.tsx:160-176`; API response; Chromium unavailable |
| Placeholder quotation | Reference yêu cầu `{{QUOTATION}}` hiện bảng giá hoặc nhãn vàng `[Presales điền]`. API/source có fallback; follow-up render marker bằng `mark` với màu amber. Chưa có gate approved để kiểm tra bảng giá. | **Source fix complete; browser verification blocked**: màu nhãn đã có trong source nhưng chưa thể xác nhận DOM/pixel runtime. | TB | `ProposalPage.tsx:43-44`, `181-192`; API response; Chromium unavailable |
| Language tabs | Reference yêu cầu tab gốc/dịch. Source có `vi`, `en`, `ja`, nhưng component tự đổi nhãn mục và hiển thị cảnh báo rằng API chỉ trả một bản nội dung. API trả section tiếng Nhật duy nhất. | **Partial**: hành vi không giả lập bản dịch là đúng contract; click tab chưa chạy được. | TB | API response; `ProposalPage.tsx:124-127` |
| Copy | Reference yêu cầu nút Copy. Source có nút `Copy Markdown`, dùng `navigator.clipboard`, reset notice trước lần thử và có trạng thái thành công/thất bại. | **Source fix complete; browser verification blocked**: chưa click để kiểm tra clipboard và thông báo runtime. | TB | `ProposalPage.tsx:74-81`, `124-126`; Chromium unavailable |
| Edit mode | Reference yêu cầu 2 cột soạn Markdown và xem trước, cảnh báo nếu xóa `{{QUOTATION}}`. Source có grid `lg:grid-cols-2`, textarea, `Xem trước`, cảnh báo và khóa lưu. | **Source contract complete; browser verification blocked**: chưa thao tác click/input để xác nhận live update và khóa nút. | CAO | `ProposalPage.tsx:132-148`; Chromium unavailable |
| Assumptions / out of scope | Reference yêu cầu đưa vào thân proposal, bỏ thẻ riêng. API có hai mảng; source nối thành heading và bullet trong `proposalMarkdown`. | **Blocked**: chưa xác nhận nội dung hiển thị sau render. | TB | API response; `ProposalPage.tsx:45-50` |
| Loading / empty / error | Source có `query.isPending` và `query.isError` với thông báo tiếng Việt. Chưa có browser/API fault injection để kiểm tra trạng thái. | **Blocked** | TB | `ProposalPage.tsx:54-55`; chưa có runtime evidence |
| Console | Không thể mở browser để thu console. Backend preview log cho thấy request proposal thành công và frontend build thành công; đây không thay thế browser console evidence. | **Blocked** | TB | frontend preview log; Playwright error |
| Download | Source tạo object URL cho `.md` và export backend, revoke sau timeout. Follow-up khóa nút `.md` trong lúc tạo blob và hiển thị `Đang chuẩn bị…`; chưa thể dùng `expect_download` vì browser không khởi động. | **Source fix complete; browser verification blocked** | TB | `ProposalPage.tsx:63-74`, `83-100`; Chromium unavailable |

## Reference/current review

- **Đạt ở mức source/API:** component đã bỏ tiêu đề Proposal lồng, có Markdown renderer, thẻ Markdown đồng nhóm export, quotation fallback, nội dung assumptions/out-of-scope trong proposal, edit preview hai cột và guard cho placeholder.
- **Chưa có evidence current/browser runtime:** không có screenshot current 1440×900; chưa thể xác nhận pixel/layout, bảng/list render thật, tab language, trạng thái disabled, live preview khi gõ, copy/clipboard, download filename, hoặc console.
- **API limitation:** proposal API chỉ trả một `sections`; việc đổi tab ngôn ngữ không thể được coi là bản dịch. UI đã hiển thị giới hạn này, phù hợp với `docs/ui/api_gaps.md`.

## Mục CAO/TB/THẤP

| ID | Mức | Phát hiện | Đã sửa |
|---|---|---|---|
| QA08-01 | CAO | Không thể xác nhận Markdown render và edit preview trên browser do Chromium unavailable. | Đã sửa parser Markdown và giữ edit guard; còn blocker nghiệm thu browser, cần chạy lại trên Preview với browser khả dụng. |
| QA08-02 | TB | Không thể xác nhận copy, download, language tabs, placeholder styling và console. | Đã bổ sung trạng thái/reset cho copy, trạng thái/khóa khi tải Markdown và nhãn vàng placeholder; language tabs, console và click runtime vẫn cần browser. |
| QA08-03 | THẤP | Không có screenshot thật trong `docs/ui_v3/` vì browser bị Blocked. | Không áp dụng; không tạo ảnh giả. |

## Kết luận

**CHANGES REQUIRED / QA BLOCKED** cho browser verification. Các thay đổi frontend follow-up cuối đã build/test và Preview rebuild thành công, nhưng chưa đủ evidence để đánh dấu DONE theo yêu cầu workflow vì Chromium không khởi động được. API gap bản dịch vẫn giữ nguyên trong `docs/ui/api_gaps.md`; không phát sinh gap mới.
