# Handoff QA Bước 2 — Khung trang hồ sơ

## Trạng thái

**CHANGES REQUIRED — kiểm tra UI end-to-end bị BLOCKED do môi trường không có Chromium; chưa đủ bằng chứng để công nhận Bước 2 đạt.**

Tester không sửa source code và không tạo screenshot giả. Các kiểm tra API dưới đây chỉ xác nhận trạng thái Preview/runtime, không thay thế được kiểm thử DOM và thao tác browser.

## Phạm vi

Kiểm tra hồ sơ mẫu Nhật đang ở trạng thái `Chờ làm rõ` theo tiêu chí Bước 2 trong `docs/ui/review_ui_tung_man.md`:

- Ở độ cao 900px thấy đầu trang, dòng tiến trình, thanh tab và ít nhất 2 thẻ nội dung.
- Banner Chờ làm rõ dẫn tới tab câu hỏi.
- Không còn bước `Bỏ qua` sai hoặc step giả.
- Tab có số đếm requirement/câu hỏi.
- Nút hành động và trạng thái pipeline.
- Trạng thái rỗng/lỗi.
- Không tạo hồ sơ trùng khi thử lại.

## Bằng chứng Preview thực tế

- `podman-compose.preview.vibeflow.yaml ps`: backend và frontend đều `Up`; frontend publish port Preview `3000`.
- `GET /api/health`: **HTTP 200**, `status: ok`, `database: ok`, `llm_provider: mock`.
- `GET /api/bids/sample/preview`: **HTTP 200**, mẫu Nhật gồm đúng 3 file:
  - `ja_email.md`
  - `ja_rfp.docx`
  - `ja_requirements.xlsx`
- `GET /api/bids`: tổng hồ sơ hiện tại `92`. Không gọi mutation trong lượt QA này, nên không tạo hồ sơ mới.
- `GET /api/bids/83`: hồ sơ mẫu Nhật ở trạng thái `waiting_clarification`, `display_currency: JPY`.
- `GET /api/bids/83/questions`: **HTTP 200**, có 5 câu hỏi trạng thái `awaiting_answer`.
- Chi tiết `pipeline_progress` của hồ sơ 83 trả trạng thái `completed`, `waiting_clarification`, `pending`, `pending`, `pending`, `pending`; đây là dữ liệu backend để UI render và cần browser xác nhận cách hiển thị.
- `GET /api/bids/83/pipeline`: **HTTP 404**; endpoint này không được dùng làm căn cứ kết luận UI, vì trạng thái pipeline đã có trong response chi tiết hồ sơ.

## Ma trận verdict

| ID | Tiêu chí | Verdict | Bằng chứng / lý do |
|---|---|---|---|
| QA2-01 | Preview chạy với LLM mock | PASS | `/api/health` trả HTTP 200, `llm_provider: mock`, database `ok`. |
| QA2-02 | Hồ sơ mẫu Nhật ở trạng thái Chờ làm rõ | PASS | `/api/bids/83` trả `status: waiting_clarification`, `waiting_clarification: true`. |
| QA2-03 | Có câu hỏi chưa trả lời để banner điều hướng | PASS | `/api/bids/83/questions` trả 5 câu hỏi `awaiting_answer`. |
| QA2-04 | Độ cao 900px thấy đầu trang, tiến trình, tab và ít nhất 2 thẻ | BLOCKED | Không khởi tạo được browser để đo/quan sát viewport thật. |
| QA2-05 | Đầu trang gọn, breadcrumb, meta, currency và 3 nút hành động | BLOCKED | Chưa thể xác nhận DOM, nội dung hiển thị hoặc khả năng click. |
| QA2-06 | Dòng tiến trình mảnh chỉ hiển thị step backend thật | BLOCKED | API có dữ liệu step nhưng không thể xác nhận giao diện không tự render step sai. |
| QA2-07 | Không còn bước `Bỏ qua` sai | BLOCKED | Chưa thể quan sát rendered progress; không suy diễn từ source/API. |
| QA2-08 | Tab có số đếm requirement/câu hỏi và chấm vàng khi chờ làm rõ | BLOCKED | Chưa thể kiểm tra text, badge và trạng thái active trên UI. |
| QA2-09 | Banner Chờ làm rõ dẫn tới câu hỏi | BLOCKED | Chưa thể click banner hoặc xác nhận tab/scroll đích. |
| QA2-10 | Nút Phân tích/Chạy lại và hành động Duyệt/Yêu cầu sửa | BLOCKED | Chưa thể xác nhận label, disabled reason, điều hướng và lỗi runtime. |
| QA2-11 | Trạng thái pipeline loading/xong/lỗi/rỗng | BLOCKED | Chưa thể tạo/quan sát các trạng thái trên browser; không dùng mutation để giả lập. |
| QA2-12 | Trạng thái rỗng thân thiện, lỗi đỏ chỉ khi API lỗi thật | BLOCKED | Chưa thể mở tab và kiểm tra DOM trực quan. |
| QA2-13 | Retry không tạo hồ sơ trùng | BLOCKED | Không thực hiện thao tác UI; danh sách hiện tại chỉ là snapshot read-only. |
| QA2-14 | Screenshot thật và console browser | BLOCKED | Playwright launch lỗi vì thiếu executable Chromium; không tạo ảnh giả. |

## Blocker

Playwright báo:

`BrowserType.launch: Executable doesn't exist at /home/user/.cache/ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell`

Không có Chromium binary thay thế khả dụng trong PATH. Vì vậy chưa có screenshot, DOM assertion, click evidence hoặc console evidence thật cho Bước 2.

## Kết luận và chuyển giao

Kết luận QA Bước 2: **CHANGES REQUIRED** do các tiêu chí UI chính bị `BLOCKED`, không phải kết luận source chắc chắn sai. Cần chạy lại trên môi trường có browser, chụp screenshot thật ở 1440×900 hoặc 1280×800, kiểm tra banner/tab/nút/trạng thái và cập nhật ma trận này trước khi reviewer kết luận Đợt 1.
