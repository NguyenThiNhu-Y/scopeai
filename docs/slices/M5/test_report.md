# Báo cáo Acceptance Test — M5

| Thuộc tính | Giá trị |
|---|---|
| Slice | M5 — Proposal + báo giá + cổng duyệt |
| Ngày | 2026-10-10 |
| Môi trường | Preview frontend `:5173`, proxy `/api`, `LLM_PROVIDER=mock` |
| Test cases | `docs/test-cases/M5-acceptance-testcases.md` |
| Người thực hiện | QA Tester |

## Tóm tắt

| Trạng thái | Số lượng |
|---|---:|
| PASS | 6 |
| FAIL | 3 |
| BLOCKED | 15 |
| Tổng | 24 |

## 1. Acceptance shell commands

| TC-ID | Lệnh | Exit/result | Actual |
|---|---|---|---|
| TC-M5-001 | `cd backend && pytest -q tests/test_pricing.py` | FAIL / no tests collected | File test không tồn tại hoặc không có test được collect |
| TC-M5-002 | `cd backend && pytest -q tests/test_pricing_mitsumorisho.py` | FAIL / no tests collected | Không có test được collect |
| TC-M5-003 | `cd backend && pytest -q tests/test_price_gate.py` | FAIL / no tests collected | Không có test được collect |
| TC-M5-004 | `cd backend && pytest -q tests/test_approval.py` | FAIL / no tests collected | Không có test được collect |
| TC-M5-005 | `cd backend && pytest -q tests/test_pre_approval_checks.py` | FAIL / no tests collected | Không có test được collect |
| TC-M5-006 | `cd backend && pytest -q tests/test_immutability_snapshot.py` | FAIL / no tests collected | Không có test được collect |
| TC-M5-007 | `cd backend && LLM_PROVIDER=mock pytest -q tests/test_proposal_schema.py` | FAIL / no tests collected | Không có test được collect |
| TC-M5-008 | `cd backend && LLM_PROVIDER=mock pytest -q tests/test_proposal_pipeline.py` | FAIL / no tests collected | Không có test được collect |
| TC-M5-009 | `cd backend && pytest -q` | PASS | Backend suite pass: 139 tests |
| TC-M5-010 | `cd frontend && npm run build` | PASS | TypeScript/Vite build thành công |
| TC-M5-011 | `make test` | PASS | Backend pass, frontend Vitest 6 tests pass, frontend build pass |
| TC-M5-012 | `make quality-gate` | PASS | Backend, frontend build, BR-10 và BR-06 đều pass |

Ghi chú: Các lệnh TC-M5-001 đến TC-M5-008 được yêu cầu trong spec nhưng các test module tương ứng chưa tồn tại/không collect, đúng với known gap trong handoff. Đây là failure của acceptance gate, không phải lỗi do test runner.

## 2. Preview/API smoke

| TC-ID | Steps | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|
| TC-M5-013 | GET `/`; GET `/api/health`; POST `/api/bids/sample` | UI render; health 200/mock; sample tạo bid | Root trả 200 HTML; health trả 200 với `status=ok`, `database=ok`, `llm_provider=mock`; sample trả 201 với bid id 78 | PASS | Health/API output trong execution log |
| TC-M5-014 | GET `/api/bids/78/quotation`; mở quotation UI | Quotation có totals/trace | API trả 404 `{"detail":"Not Found"}`; không thể xác nhận quotation UI | FAIL | API response trong execution log |
| TC-M5-015 | GET `/api/bids/78/proposal`; sửa/lưu/reload proposal | Proposal draft hiển thị và lưu được | API trả 404 `{"detail":"Not Found"}`; không thể xác nhận editor | FAIL | API response trong execution log |
| TC-M5-016 | POST tech approval với/sai role | Sai role/reject thiếu reason bị chặn; đúng role chuyển state | API endpoint `/api/bids/78/approvals/tech` trả 404; không thực hiện được | FAIL | API response trong execution log |
| TC-M5-017 | POST price approval với creator/manager | SoD 409; manager duyệt và lock | Không thực hiện được do endpoint M5 trả 404 | BLOCKED | Phụ thuộc TC-M5-016/endpoint |
| TC-M5-018 | Unlock với/sai role và reason | Manager có reason unlock, bắt buộc re-approval | Không thực hiện được do endpoint M5 chưa truy cập được | BLOCKED | Phụ thuộc endpoint M5 |
| TC-M5-019 | PUT proposal với empty/XSS/SQLi/field tiền | Validation/encoding an toàn, không 500, không ghi đè gate | Không thực hiện được vì proposal endpoint trả 404 | BLOCKED | Phụ thuộc endpoint M5 |

## 3. Playwright execution

Đã chạy reconnaissance script theo `webapp-testing` sau khi kiểm tra Preview. Playwright không khởi động được Chromium vì executable không tồn tại tại:

`/home/user/.cache/ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell`

Lỗi runtime yêu cầu cài browser. Theo nguyên tắc QA, các case UI không được chuyển thành PASS bằng cách suy đoán. Không có screenshot failure vì browser chưa khởi động được.

Các case bị Blocked do không có browser:

- TC-M5-013 UI portion
- TC-M5-014 through TC-M5-019 UI execution

## 4. Failures

### F-M5-001 — Acceptance test modules không tồn tại/không collect

- Affected: TC-M5-001 through TC-M5-008.
- Expected: Mỗi command exit 0 và chạy được test suite tương ứng.
- Actual: Pytest báo `No tests collected` cho từng command.
- Suspected location: `backend/tests/`, các file được liệt kê tại `docs/slices/M5/spec.md` §6.
- Reproduction: chạy đúng các lệnh trong bảng §1.
- Impact: Không chứng minh độc lập các yêu cầu pricing, price gate, approval, snapshot và proposal pipeline.

### F-M5-002 — M5 API routes trả 404 trên Preview

- Affected: TC-M5-014, TC-M5-015, TC-M5-016 và các case phụ thuộc.
- Expected: Các endpoint frozen hoạt động dưới `/api/bids/{id}/quotation`, `/proposal`, `/approvals/tech`, `/approvals/price`, `/unlock`.
- Actual: Với bid sample `78`, các request proposal, quotation và tech/price approval đều trả `404 Not Found`.
- Suspected location: router registration/mounting trong `backend/app/api/routers/__init__.py` hoặc application include routers; graph có symbol `get_quotation`, `get_proposal`, `approve_price` nhưng Preview route không expose chúng.
- Reproduction: tạo sample bằng `POST /api/bids/sample`, sau đó GET/POST các endpoint trên.
- Evidence: response `{"detail":"Not Found"}` trong execution log.

### F-M5-003 — Browser automation bị Blocked

- Affected: toàn bộ manual UI execution.
- Expected: Playwright mở Preview, thao tác UI và chụp screenshot cho từng case.
- Actual: Chromium executable không tồn tại; Playwright không launch được.
- Suspected location: môi trường test/Playwright browser installation, không kết luận là lỗi app.
- Impact: Chưa thể xác nhận DOM, button flow, proposal editor, quotation rendering và approval UI bằng browser.

## 5. Handoff note

- Backend regression suite hiện pass 139 tests; frontend build và quality gate pass.
- Acceptance suite M5 riêng còn thiếu và phải được bổ sung trước khi kết luận M5 đạt.
- Cần kiểm tra việc include/mount các M5 routers trong Preview image/runtime; QA không sửa source.
- Cần cung cấp browser executable hoặc môi trường Playwright hoàn chỉnh để chạy lại manual UI cases.
- Báo cáo này là điểm dừng của QA step; không thực hiện remediation trong bước này.

**Task Acceptance Test complete. Awaiting prompt for the next role.**
