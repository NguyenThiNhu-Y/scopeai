# Báo cáo kiểm thử QA

> Cập nhật cuối: 2026-10-13. Các số liệu cũ trong báo cáo này đã được thay
> bằng kết quả trực tiếp của lần review Tokai Minato.

## Phạm vi

- Hành trình mục tiêu: RFP tiếng Nhật hư cấu → trả lời câu hỏi làm rõ → effort/WBS/schedule → duyệt giá → proposal hiển thị giá sau duyệt → export.
- Chế độ LLM local/CI: mock. Real OpenRouter smoke được chạy riêng và vẫn bị
  chặn trước request khi process không nhận `LLM_PROVIDER=openai_compat`.

## Kết quả tự động

| Hạng mục | Kết quả | Bằng chứng |
|---|---|---|
| Backend test suite | PASS | `cd backend && python3 -m pytest -q`; 263 passed |
| Frontend unit tests | PASS | `cd frontend && npm run test -- --run`; 16 tests passed |
| Frontend build | PASS | `cd frontend && npm run build` thành công |
| Quality gate script | PASS | `bash scripts/quality_gate.sh`; backend/build/BR-10/BR-06 đều pass |

## E2E

| ID | Kết quả | Bằng chứng / giới hạn |
|---|---|---|
| TC-E2E-01 | BLOCKED | Playwright không có browser executable; không tạo screenshot/DOM giả |
| TC-E2E-02 | BLOCKED | Chưa thể điều hướng để gửi RFP tiếng Nhật và trả lời câu hỏi làm rõ vì TC-E2E-01 bị chặn |
| TC-E2E-03 | BLOCKED | Chưa thể xác nhận effort, WBS và schedule trong trình duyệt |
| TC-E2E-04 | BLOCKED | Chưa thể xác nhận price gate và proposal chỉ hiện giá sau approval |
| TC-E2E-05 | BLOCKED | Chưa thể mở và xác nhận các file export |

## Kết luận QA

- Preview/API evidence đã xác nhận health, tạo bid, parse/confirm, pipeline start,
  proposal, price-gate conflict và not-found envelope.
- Browser E2E vẫn BLOCKED vì thiếu browser executable; unit test/build/API không
  được dùng thay thế bằng chứng browser.
- Backend verification cuối: `python3 -m pytest -q` chạy trực tiếp hoàn tất
  **263 passed**, với một cảnh báo deprecation Starlette/httpx.
- Output `rtk pytest` báo `No tests collected` không phải kết quả authoritative.
