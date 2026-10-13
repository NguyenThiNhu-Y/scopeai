# Handoff QA Bước 1 — Màn Tạo hồ sơ

## Trạng thái

**CHANGES REQUIRED — phần UI end-to-end bị BLOCKED, chưa đủ bằng chứng để công nhận Bước 1 đạt.**

Đây là kết luận QA của bước này, không phải kết luận rằng mã nguồn chắc chắn có lỗi. Cần chạy lại browser trên Preview trước khi đổi thành PASS.

Preview đã chạy lại sạch với `LLM_PROVIDER=mock`, nhưng môi trường QA không có Chromium executable nên không thể thao tác giao diện bằng browser và không thể tạo screenshot thật. Không tạo ảnh giả.

## Phạm vi kiểm tra

Tiêu chí cần kiểm tra theo `docs/ui/review_ui_tung_man.md`:

`Dùng bộ này` (mẫu Nhật) → thấy 3 file → `Phân tích` → tự sang trang hồ sơ → đọc 36 requirement → pipeline tới `Chờ làm rõ` mà không bấm thêm nút nào.

Ngoài ra cần kiểm tra loading/rỗng/lỗi và thử lại không tạo hồ sơ trùng.

## Bằng chứng Preview thực tế

- Stack Preview được khởi động lại bằng `podman-compose.preview.vibeflow.yaml` sau khi phát hiện container trước đó đang chạy backend cũ.
- Services sau khi khởi động lại: backend và frontend đều `Up`; frontend phục vụ trên port Preview nội bộ `3000`.
- `GET /api/health`: **HTTP 200**; response xác nhận `status: ok`, database `ok`, `llm_provider: mock`.
- `GET /api/bids/sample/preview`: **HTTP 200**.
- Preview API trả đúng 3 file mẫu Nhật:
  - `ja_email.md` — loại `rfp`
  - `ja_rfp.docx` — loại `rfp`
  - `ja_requirements.xlsx` — loại `requirement`
- Response preview có `customer_language: ja` và `display_currency: JPY`.
- Kiểm tra trước/sau `GET /api/bids`: tổng đều là `92`, chứng minh gọi preview không tạo hồ sơ.
- `GET /api/bids/sample/preview?sample_key=invalid`: **HTTP 400**, mã `VALIDATION_ERROR`.
- Không gọi endpoint tạo hồ sơ, upload, parse, confirm hoặc start pipeline trong kiểm tra HTTP này; không dùng API mutation để giả lập thao tác UI.

## Ma trận verdict

| ID | Yêu cầu | Verdict | Bằng chứng / lý do |
|---|---|---|---|
| QA-01 | Preview chạy với LLM mock | PASS | `/api/health` trả `status: ok`, `llm_provider: mock`, `database: ok`. |
| QA-02 | Preview mẫu Nhật trả đúng 3 file | PASS | HTTP 200; `ja_email.md`, `ja_rfp.docx`, `ja_requirements.xlsx`. |
| QA-03 | Preview không tạo hồ sơ | PASS | Tổng hồ sơ trước và sau đều `92`. |
| QA-04 | Sample key không hợp lệ báo lỗi có cấu trúc | PASS | HTTP 400, `VALIDATION_ERROR`. |
| QA-05 | `Dùng bộ này` điền form và hiện 3 file trong khu đính kèm | BLOCKED | Không có Chromium executable để thao tác browser. |
| QA-06 | Loading tiến trình `Tạo hồ sơ → Tải file → Đọc file → Bắt đầu phân tích` | BLOCKED | Chưa thể chạy UI; không dùng API để thay thế bằng chứng thao tác. |
| QA-07 | Bấm `Phân tích` một lần tự chuyển sang trang hồ sơ | BLOCKED | Chưa thể chạy UI. |
| QA-08 | Đọc đúng 36 requirement | BLOCKED | Chưa thể chạy luồng parse/pipeline qua UI. |
| QA-09 | Pipeline tự tới `Chờ làm rõ` không bấm thêm | BLOCKED | Chưa thể theo dõi trạng thái UI/runtime sau khi bắt đầu pipeline. |
| QA-10 | Loading/rỗng/lỗi và retry giữ dữ liệu, không tạo hồ sơ trùng | BLOCKED | Chưa thể thao tác và tạo tình huống lỗi trên browser. |
| QA-11 | Screenshot thật và console browser | BLOCKED | Playwright không khởi tạo được browser; không tạo ảnh giả. |

## Kiểm tra bị chặn

- Playwright không khởi tạo được browser: thiếu executable tại `/home/user/.cache/ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell`.
- Không có Chromium binary thay thế trong PATH.
- Vì không có browser, chưa thể xác nhận bằng chứng thật cho:
  - Nút **Dùng bộ này** điền form và hiển thị 3 file trong khu đính kèm.
  - Nút **Phân tích** và trạng thái loading từng bước.
  - Tự chuyển sang trang hồ sơ.
  - Đọc đúng 36 requirement.
  - Pipeline tự chạy tới **Chờ làm rõ** không cần bấm thêm.
  - Trạng thái rỗng/lỗi và retry không tạo hồ sơ trùng.
  - Screenshot hoặc lỗi console trong browser.

Lỗi khởi tạo browser được thử lại sau khi Preview restart và vẫn tái hiện; không tiếp tục lặp lại lệnh.

## Ghi chú sự cố Preview

Lần kiểm tra đầu, container backend đang phục vụ image/runtime cũ và route preview trả `404`. Đã restart toàn bộ Preview stack theo compose; sau đó route preview trả `200` và OpenAPI/runtime có dữ liệu bộ mẫu đúng yêu cầu. Đây là lý do cần chạy lại phần browser khi có executable.

## Kết luận và chuyển giao

Kết luận hiện tại: **CHANGES REQUIRED** do QA chưa có bằng chứng browser cho các tiêu chí chính, dù các kiểm tra API preview độc lập đều PASS. Tester tiếp theo hoặc người vận hành có browser cần chạy lại toàn bộ luồng UI trên Preview, chụp bằng chứng thật nếu khả dụng, rồi cập nhật ma trận này. Không chuyển sang Bước 2 trong handoff này.
