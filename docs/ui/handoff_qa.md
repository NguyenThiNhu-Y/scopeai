# Handoff: QA — kiểm thử Preview và đối chiếu UI

## Phạm vi

- Đã đọc `docs/ui/ui_spec.md` và mục R-08 trong `docs/reviews/review_G4.md`.
- Đã khởi động Preview với LLM mock.
- Đã chạy backend pytest, frontend build và frontend unit tests.
- Đã thử chạy Playwright để kiểm tra UI, console và request lỗi.

## Kết quả

- Backend: **PASS — 198 passed** (`python -m pytest -q` chạy trực tiếp, không qua wrapper).
- Frontend build: **PASS** (`npm run build`).
- Frontend unit tests: **PASS — 6 tests**.
- Preview health: **PASS — HTTP 200**, `llm_provider=mock`, `database=ok`.
- Playwright/browser E2E: **BLOCKED** trước khi điều hướng vì môi trường thiếu
  executable `chromium_headless_shell-1187`.
- QA script syntax: **PASS** (`python -m py_compile scripts/ui_qa_playwright.py`).

## Deliverables

- `docs/quality/test_report.md`: cập nhật kết quả test và TC-E2E-01..05 là BLOCKED.
- `docs/quality/gate_summary.md`: giữ GATE-01 là `Chấp nhận rủi ro: ngoài phạm vi MVP`;
  ghi nhận E2E là BLOCKED.
- `docs/ui/ui_compare.md`: có bảng đối chiếu 10 trang/tab ở 1440×900 và 1280×900;
  chưa có ảnh runtime vì browser không khởi động được.
- `docs/ui_current/`: chưa có screenshot runtime. Không tạo ảnh giả thay cho bằng chứng.
- `scripts/ui_qa_playwright.py`: đã mở rộng để chụp 10 trang/tab ở cả `1440x900` và
  `1280x900`, kiểm tra console, request lỗi và một số kiểm tra accessibility cơ bản;
  chưa thể thực thi vì thiếu Chromium.

## Handoff và giới hạn

- Không sửa app source để làm test pass.
- Không thêm authentication/authorization server; `X-Actor` vẫn chỉ phục vụ audit log.
- GATE-01 được ghi nhận là chấp nhận rủi ro ngoài phạm vi MVP.
- Cần một môi trường có Chromium để chạy lại từng tab, lưu screenshot tại
  `docs/ui_current/`, kiểm tra console/network/accessibility và xác nhận export binary.

## Audit completeness cuối

- Đã thử cài Chromium một lần; executable vẫn không tồn tại, nên không giả mạo ảnh
  hoặc kết quả browser.
- `docs/ui_current/` có `README.md` mô tả blocker; chưa có screenshot runtime.
- `docs/ui/ui_compare.md` có bảng đủ 10 trang/tab ở hai viewport và phân loại
  `BLOCKED — thiếu Chromium`.
- Không còn claim cũ rằng browser E2E đã PASS.
- GATE-01 vẫn đúng nguyên văn: `Chấp nhận rủi ro: ngoài phạm vi MVP`.
- Lần chạy trực tiếp cuối cùng không có failure; các output wrapper báo `No tests collected`
  được loại khỏi bằng chứng kiểm thử.
