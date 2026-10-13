# Báo cáo kiểm thử — M6 Đính kèm và ma trận đáp ứng

| Thuộc tính | Giá trị |
|---|---|
| Vai trò | QA / Test |
| Ngày | 2026-10-10 |
| Môi trường | Preview compose, backend và frontend Up, LLM mock |
| Tài liệu test | `docs/slices/M6/test_cases.md` |
| Phạm vi | M6 attachment, parser, confirm gate, evaluation matrix và AGENTS rules liên quan |

## 1. Tóm tắt

| Kết quả | Số lượng |
|---|---:|
| PASS | 4 |
| FAIL | 0 |
| BLOCKED | 12 |
| Tổng test case UI | 12 |

Bốn kiểm tra nền tảng/API đã PASS: health check, nạp sample qua API, `make test` và `make quality-gate`. Mười hai ca click-through được thiết kế và đã cố gắng chạy bằng Playwright, nhưng bị BLOCKED trước bước điều hướng vì Chromium executable không tồn tại trong cache của phiên. Không sửa source để làm test pass.

## 2. Acceptance shell commands

| Command | Exit/result | Key output |
|---|---|---|
| `cd backend && pytest -q tests/test_file_reader.py` | Exit 5; không đạt gate | `No tests collected`; file test không tồn tại |
| `cd backend && pytest -q tests/test_excel_multisheet.py` | Exit 5; không đạt gate | `No tests collected`; file test không tồn tại |
| `cd backend && pytest -q tests/test_internal_req_code.py` | Exit 5; không đạt gate | `No tests collected`; file test không tồn tại |
| `cd backend && pytest -q tests/test_data_profile.py` | Exit 5; không đạt gate | `No tests collected`; file test không tồn tại |
| `cd backend && pytest -q tests/test_evaluation_batches.py` | Exit 5; không đạt gate | `No tests collected`; file test không tồn tại |
| `cd backend && pytest -q tests/test_unique_req_codes.py` | Exit 5; không đạt gate | `No tests collected`; file test không tồn tại |
| `cd backend && LLM_PROVIDER=mock pytest -q tests/test_evaluation_retry.py` | Exit 5; không đạt gate | `No tests collected`; file test không tồn tại |
| `cd backend && pytest -q` qua `make test` | PASS | Backend suite: `158 passed` |
| `cd frontend && npm run build` | PASS | TypeScript check và Vite build thành công |
| `make test` | PASS | Backend `158 passed`, frontend `6 passed`, build PASS |
| `make quality-gate` | PASS | Root-relative URL scan OK; credential scan OK; `QUALITY GATE PASSED` |

Các npm warning về config không xác định và Starlette deprecation warning không làm command thất bại.

## 3. Preview/API smoke evidence

| ID | Thao tác | Kết quả | Evidence |
|---|---|---|---|
| SMOKE-01 | Kiểm tra compose status | PASS; backend/frontend đều `Up`, frontend publish port 5173 | output `podman-compose ... ps` |
| SMOKE-02 | `GET /api/health` | PASS; `status=ok`, `database=ok`, `llm_provider=mock` | response health JSON |
| SMOKE-03 | `POST /api/bids/sample` với sample giả lập | PASS; trả bid `id=82`, `status=draft`, `budget_amount=null` | response sample JSON |
| SMOKE-04 | Mở `/openapi.json` qua frontend preview | FAIL/không phải M6 blocker; response không phải JSON nên không liệt kê route được qua proxy hiện tại | command JSON decode error |

## 4. Kết quả từng test case

| TC-ID | Steps / expected | Actual | Verdict | Evidence |
|---|---|---|---|---|
| TC-M6-001 | Nạp hồ sơ mẫu; draft và dữ liệu giả lập | Chưa thể click UI vì browser không khởi động | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-002 | Upload 3 file; detect type; quota 3/10 | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-003 | Upload file thứ 11; `TOO_MANY_FILES`; giữ 10 file | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-004 | 20 MB nhận; 20 MB + 1 byte `FILE_TOO_LARGE` | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-005 | Extension/XSS bị chặn hoặc encode | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-006 | Parse hai sheet; mã duy nhất; trace sheet/row | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-007 | Sửa mapping; parse lại không nhân đôi | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-008 | Profile row/type/empty/PII; readiness medium | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-009 | Chưa confirm thì UI/API chặn pipeline | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-010 | 235 dòng, batch ≤40, matrix/stats | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-011 | Retry missing/duplicate/unknown; warnings | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |
| TC-M6-012 | Không có Excel; `no_requirement_file`; ẩn matrix | Chưa chạy được UI | BLOCKED | `Playwright BrowserType.launch` |

## 5. Failures và blockers

### B-001 — Playwright không có Chromium executable

- Mức độ: Blocker môi trường kiểm thử UI.
- Reproduction: chạy script Playwright với `chromium.launch(headless=True)`.
- Actual: `Executable doesn't exist at /home/user/.cache/ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell`.
- Expected: Chromium khởi động, mở Preview và thực thi từng TC độc lập.
- Ảnh screenshot: không tạo được vì browser fail trước khi tạo page/context.
- Suspected file: không phải lỗi source ứng dụng; cache browser của môi trường QA.
- Khuyến nghị cho Test/Review kế tiếp: cung cấp browser executable trong môi trường chạy Playwright rồi rerun toàn bộ TC-M6-001..012.

### B-002 — Các file acceptance test theo tên trong spec chưa tồn tại

- Mức độ: Thiếu coverage tự động theo file-level contract.
- Reproduction: chạy bảy command đầu trong §2.
- Actual: `No tests collected`.
- Expected: các file `tests/test_file_reader.py`, `test_excel_multisheet.py`, `test_internal_req_code.py`, `test_data_profile.py`, `test_evaluation_batches.py`, `test_unique_req_codes.py`, `test_evaluation_retry.py` được thu thập và exit 0.
- Suspected area: `backend/tests/` thiếu các file test acceptance nêu trong `docs/slices/M6/spec.md`.

## 6. Kết luận bàn giao

- Automated regression gate hiện có PASS: backend 158, frontend 6, build và quality gate.
- Preview backend health và sample API PASS với mock LLM.
- Chưa đủ bằng chứng để kết luận M6 acceptance hoàn tất vì 12 ca UI bị BLOCKED và bảy file acceptance theo spec chưa tồn tại.
- Không phát hiện FAIL chức năng từ click-through vì chưa qua được bước khởi động browser; không được coi BLOCKED là PASS.

**QA Test step complete. Awaiting Test/Review environment with Chromium for rerun.**
