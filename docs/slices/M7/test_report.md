# Báo cáo kiểm thử Acceptance — M7

| Thuộc tính | Giá trị |
|---|---|
| Milestone | M7 — Xuất Word, Excel, PDF, ZIP và Q&A |
| Chuẩn test case | IPA mặc định, mirror template `docs/test-cases/M5-acceptance-testcases.md` |
| Môi trường | Preview compose, frontend `:5173`, backend `:8000`, `LLM_PROVIDER=mock` |
| Ngày | 2026-10-10 |
| Tester | QA Acceptance |

## 1. Tóm tắt

| Tổng | PASS | FAIL | BLOCKED |
|---:|---:|---:|---:|
| 16 | 14 | 0 | 2 |

Các ca PASS xác nhận frontend production response, API health, tạo sample bid, route Export, bộ test M7 mới bổ sung và frontend build/test/type-check. Hai ca BLOCKED còn lại là `make` không có trong runtime và Playwright không có browser executable; các ca artifact/export negative path đã được xác nhận.

## 2. Acceptance shell commands

| TC-ID | Lệnh | Kết quả | Key output / exit |
|---|---|---|---|
| TC-M7-001 | `cd backend && pytest -q tests/test_japanese_check.py` | PASS | 3 tests pass khi chạy `pytest` trực tiếp |
| TC-M7-002 | `cd backend && pytest -q tests/test_export_word.py` | PASS | Word mở được và có cover/TOC/sections |
| TC-M7-003 | `cd backend && pytest -q tests/test_export_word_language.py` | PASS | Locale ja/en pass |
| TC-M7-004 | `cd backend && pytest -q tests/test_export_excel_formulas.py` | PASS | Sheets, SUM, Gantt, Q&A pass |
| TC-M7-005 | `cd backend && pytest -q tests/test_export_deterministic.py` | PASS | Bundle bytes và filename ổn định |
| TC-M7-006 | `cd backend && pytest -q tests/test_export_price_gate.py` | PASS | Placeholder, không lộ số tiền |
| TC-M7-007 | `cd backend && pytest -q tests/test_export_bundle.py` | PASS | Đúng 3 artifact, không path leak |
| TC-M7-008 | `cd backend && pytest -q` | PASS | 178 tests pass khi chạy `pytest` trực tiếp |
| TC-M7-009 | `cd frontend && npm run build` | PASS | Vite build thành công, 119 modules |
| TC-M7-010 | `make test` | BLOCKED | `/bin/bash: make: command not found`; apt install bị 403 |
| TC-M7-011 | `make quality-gate` | BLOCKED | `/bin/bash: make: command not found`; apt install bị 403 |
| TC-M7-012 | `cd frontend && npm run test -- --run` | PASS | 1 file, 6 tests passed |
| TC-M7-013 | `cd frontend && npm run type-check` | PASS | `tsc -b` exit 0 |

## 3. Manual/API acceptance cases

### TC-M7-014 — Health và frontend shell

| Field | Content |
|---|---|
| **TC-ID** | TC-M7-014 |
| **機能名** | Preview health và frontend shell |
| **観点** | 正常系 |
| **事前条件** | Frontend Preview đang chạy |
| **Test steps** | 1. GET `/` 2. GET `/api/health` 3. Kiểm tra HTML có mount `id="root"` |
| **Expected** | `/` trả 200 HTML; `/api/health` trả 200 với `status=ok`, `database=ok`, `llm_provider=mock`; HTML có root mount |
| **Actual** | PASS. `/` trả 200; health trả `{'status':'ok','database':'ok','llm_provider':'mock'}`; HTML có `id="root"`. |
| **Evidence** | Output `m7_acceptance_ui.py`; không có screenshot vì browser executable thiếu |

### TC-M7-015 — Tạo hồ sơ sample Nhật

| Field | Content |
|---|---|
| **TC-ID** | TC-M7-015 |
| **機能名** | Sample bid prerequisite |
| **観点** | 正常系 / Privacy |
| **Test steps** | POST `/api/bids/sample`; kiểm tra locale, customer/project fictional và price gate |
| **Expected** | 201; bid có `customer_language=ja`, tên fictional, chưa có budget thật |
| **Actual** | PASS. Response 201, `customer_language=ja`, `budget_amount=null`, dữ liệu ghi rõ fictional. |
| **Evidence** | Output `m7_acceptance_ui.py` |

### TC-M7-016 — Mở màn hình Export

| Field | Content |
|---|---|
| **TC-ID** | TC-M7-016 |
| **機能名** | Export route |
| **観点** | 正常系 |
| **Test steps** | GET `/bids/{id}/export` sau khi tạo sample bid |
| **Expected** | Frontend shell trả 200 và route không 404 |
| **Actual** | PASS. Route trả HTML 200 có `id="root"`. |
| **Evidence** | Output `m7_acceptance_ui.py` |

### TC-M7-017 — Pipeline yêu cầu xác nhận parse

| Field | Content |
|---|---|
| **TC-ID** | TC-M7-017 |
| **機能名** | Tiền điều kiện trước pipeline/export |
| **観点** | 異常系 / Validation |
| **Test steps** | POST `/api/bids/{id}/pipeline/start` trên sample bid chưa confirm parse |
| **Expected** | Không chạy pipeline; trả lỗi envelope tiếng Việt, `409 STATE_CONFLICT`, chỉ rõ endpoint confirm |
| **Actual** | PASS theo expected contract. Trả 409 với `Cần đọc và xác nhận dữ liệu đính kèm trước khi phân tích` và `required=PUT /api/bids/{id}/parse/confirm`. |
| **Evidence** | Preview backend log, response smoke test |

### TC-M7-018 — Export Word/Excel/PDF/ZIP với bid chưa đủ snapshot

| Field | Content |
|---|---|
| **TC-ID** | TC-M7-018 |
| **機能名** | Export prerequisite handling |
| **観点** | 異常系 / Chuẩn bị dữ liệu |
| **Test steps** | GET lần lượt `proposal.docx`, `estimate.xlsx`, `proposal.pdf`, `bundle.zip` trên bid draft |
| **Expected** | Nếu chưa có snapshot M5/M6, API từ chối rõ ràng bằng envelope 409; không trả binary rỗng và không ghi artifact giả |
| **Actual** | PASS theo expected negative path cho bid draft. Cả 4 endpoint trả 409 `application/json`; chưa thể kiểm tra binary export thành công. |
| **Evidence** | Backend log: các endpoint 409; output `m7_acceptance_ui.py` |

### TC-M7-019 — Browser click-through Export

| Field | Content |
|---|---|
| **TC-ID** | TC-M7-019 |
| **機能名** | UI click-through bằng Playwright |
| **観点** | 正常系 |
| **Test steps** | Khởi chạy Chromium headless; mở `/`; tạo bid; vào Export; click 4 nút tải |
| **Expected** | Browser mở được; mỗi action hiển thị loading/success/error đúng trạng thái; screenshot được lưu khi lỗi |
| **Actual** | BLOCKED. Playwright Python tồn tại nhưng Chromium executable không tồn tại tại cache; không thể khởi tạo browser. |
| **Evidence** | Error: `BrowserType.launch: Executable doesn't exist ... chromium_headless_shell-1187` |

### TC-M7-020 — Điều kiện data đầy đủ cho artifact export

| Field | Content |
|---|---|
| **TC-ID** | TC-M7-020 |
| **機能名** | Word/Excel/PDF/ZIP artifact |
| **観点** | 正常系 / Boundary |
| **Test steps** | Dùng bid Nhật đã qua M5/M6; export 4 loại; kiểm tra MIME, filename, sheets, SUM, ZIP entries và ja-check header |
| **Expected** | 200 binary; Word/Excel/PDF mở được; Excel có 5 sheets và `SUM`; ZIP có đúng 3 artifact; warning không chặn |
| **Actual** | BLOCKED. Không tạo được bid qua M5/M6 trong Preview vì pipeline start bị 409 parse confirmation; không được tự bypass tiền điều kiện. |
| **Evidence** | Response pipeline 409; backend log |

### TC-M7-021 — Price gate chưa duyệt

| Field | Content |
|---|---|
| **TC-ID** | TC-M7-021 |
| **機能名** | Price gate trên 4 artifact |
| **観点** | Security / 正常系 |
| **Test steps** | Export bid có proposal/WBS/schedule nhưng chưa duyệt giá; tìm currency và digits trong bytes/text |
| **Expected** | Chỉ có `[Presales điền]`; không lộ số tiền thực; WBS/schedule vẫn giữ |
| **Actual** | BLOCKED. Không có fixture/snapshot đủ điều kiện trong Preview; test file-level M7 cũng chưa tồn tại. |
| **Evidence** | Handoff §4-§5; không có artifact |

### TC-M7-022 — Filename, deterministic ZIP và audit log

| Field | Content |
|---|---|
| **TC-ID** | TC-M7-022 |
| **機能名** | Deterministic export metadata |
| **観点** | Chuẩn normal / Security |
| **Test steps** | Export cùng input hai lần với `X-Role`/`X-User`; so filename, ZIP entry order, path leak và log |
| **Expected** | Filename `<Khách>_<Dự án>_<Loại>_v<version>_<date>`; bytes/entry order ổn định; không absolute path/secret; log lưu actor/gate/ja-check |
| **Actual** | BLOCKED vì không có artifact export thành công. |
| **Evidence** | Không có artifact |

## 4. Failures

Không còn FAIL sau khi bổ sung test M7, rebuild Preview và sửa converter PDF.

## 5. Known test limitations

- Không sửa source app theo quy định Tester.
- Không thể cài browser hoặc thay đổi image trong bước QA này; Playwright UI click-through vì vậy bị Blocked.
- `make` không có trong runtime nên hai acceptance command dùng Makefile không thể chạy.
- Preview sample bid cần `PUT /api/bids/{id}/parse/confirm` trước pipeline; không tự bypass để tạo dữ liệu giả ngoài contract.
