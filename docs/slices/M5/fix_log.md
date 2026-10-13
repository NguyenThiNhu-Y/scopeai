# Fix Log — M5 Acceptance Failures

| Thuộc tính | Giá trị |
|---|---|
| Slice | M5 — Proposal + báo giá + cổng duyệt |
| Ngày | 2026-10-10 |
| Vai trò | Backend Developer |

## FAIL đã xử lý

### F-M5-001 — Các acceptance module M5 chưa tồn tại

**Root cause:** Các lệnh trong `docs/slices/M5/spec.md` §5.1 tham chiếu tới tám file test nhưng các file đó chưa được tạo, nên pytest báo `No tests collected`. Đây là thiếu test coverage, không phải lỗi của tiêu chí acceptance.

**Fix:** Bổ sung các module test backend sau, bám theo contract M5 và dùng mock/test database:

- `backend/tests/test_pricing.py`
- `backend/tests/test_pricing_mitsumorisho.py`
- `backend/tests/test_price_gate.py`
- `backend/tests/test_approval.py`
- `backend/tests/test_pre_approval_checks.py`
- `backend/tests/test_immutability_snapshot.py`
- `backend/tests/test_proposal_schema.py`
- `backend/tests/test_proposal_pipeline.py`

Các test kiểm tra rate/overhead/contingency/trace, tax/rounding, placeholder price gate, SoD approval, checks report, snapshot reference, schema extra-field và proposal edit/number guard. Không có test nào gọi LLM thật.

### F-M5-002 — Preview trả 404 cho router M5

**Root cause:** Router M5 đã tồn tại và đã được include trong `backend/app/api/routers/__init__.py`; source code không thiếu route. Preview đang giữ backend container cũ, vì `podman-compose up --build -d` không recreate container đang chạy. Do đó runtime không chứa router M5 dù source hiện tại đã có.

**Fix:** Không thay đổi contract hoặc nới lỏng route. Recreate Preview stack bằng `podman-compose down` rồi `podman-compose up --build -d`. Sau khi recreate:

- `GET /api/bids/{id}/proposal` trả `200` với draft placeholder.
- `GET /api/bids/{id}/quotation` trả `409 STATE_CONFLICT` đúng khi bid chưa có WBS.
- `POST /api/bids/{id}/approvals/tech` trả `409 STATE_CONFLICT` đúng khi bid chưa ở trạng thái duyệt kỹ thuật.
- Health trả `200`, database `ok`, `llm_provider=mock`.

## Verification

| Command | Result |
|---|---|
| `cd backend && pytest -q tests/test_pricing.py` | PASS, 2 tests |
| `cd backend && pytest -q tests/test_pricing_mitsumorisho.py` | PASS, 1 test |
| `cd backend && pytest -q tests/test_price_gate.py` | PASS, 1 test |
| `cd backend && pytest -q tests/test_approval.py` | PASS, 2 tests |
| `cd backend && pytest -q tests/test_pre_approval_checks.py` | PASS, 1 test |
| `cd backend && pytest -q tests/test_immutability_snapshot.py` | PASS, 1 test |
| `cd backend && LLM_PROVIDER=mock pytest -q tests/test_proposal_schema.py` | PASS, 2 tests |
| `cd backend && LLM_PROVIDER=mock pytest -q tests/test_proposal_pipeline.py` | PASS, 2 tests |
| `cd backend && pytest -q` | PASS, 148 tests |
| `cd frontend && npm run build` | PASS |
| `make test` | PASS; frontend Vitest 6 tests and build pass |
| `make quality-gate` | PASS; BR-06 and BR-10 pass |
| Preview route smoke after recreate | PASS; routes no longer return 404 |

## Không sửa trong bước này

- Playwright UI execution vẫn bị Blocked do Chromium executable không có trong môi trường test; không sửa application source để che giấu blocker.
- Cảnh báo `StarletteDeprecationWarning` từ TestClient không làm fail test và không thuộc acceptance failure M5.

## Handoff

Mọi FAIL có thể sửa trong báo cáo QA đã được xử lý hoặc giải thích. Acceptance shell commands hiện exit 0 và Preview đã được recreate với backend hiện tại.

**Task Fix Failures complete. Awaiting prompt for the next role.**

## Bổ sung remediation sau review Preview M5

### F-M5-003 — Currency/FX và budget comparison chưa được tính theo hồ sơ

**Root cause:** `Bid` không nhận/persist `display_currency`; quotation engine luôn chọn rate offshore, FX `1.0` và `VND/VND`; budget difference luôn `null`.

**Fix:** Bổ sung `display_currency` vào input/model flow, FX pair theo currency, rounding theo currency, JPY onsite rate cho hồ sơ Nhật, PM/BrSE overhead, snapshot version và budget difference sau quy đổi. Bổ sung regression test cho JPY và budget.

### F-M5-004 — Proposal sau price approval chưa có server-rendered quotation

**Root cause:** `proposal_service.to_out()` chỉ trả cờ `price_gate`, không tạo output quotation sau khi bid locked.

**Fix:** Bổ sung `quotation_markdown` do backend dựng từ quotation snapshot; trước approval giữ `[Presales điền]`, sau approval render currency, grand total và validity. Bổ sung test proposal sau approval.

### F-M5-005 — Pre-approval checks kiểm tra không đầy đủ

**Root cause:** `_checks()` chỉ kiểm tra tổng man-day khác 0 và item tồn tại, không dùng `check_engine.check_wbs()`.

**Fix:** Dùng `check_wbs()` để kiểm tra ±20%, PM/QA, cycle và leaf limit; map từng kết quả vào `checks_report`, fail chặn price approval. Bổ sung test WBS thiếu PM/QA.

### F-M5-006 — Mock proposal không theo ngôn ngữ customer

**Root cause:** fixture `ProposalOutput` dùng cùng nội dung tiếng Việt cho mọi customer language.

**Fix:** Bổ sung fixture tiếng Anh và tiếng Nhật; registry chọn fixture theo `customer_language` context. Không gọi LLM thật.

## Verification sau remediation

| Command | Result |
|---|---|
| `pytest -q tests/test_pricing.py` | PASS |
| `pytest -q tests/test_pricing_mitsumorisho.py` | PASS |
| `pytest -q tests/test_price_gate.py` | PASS |
| `pytest -q tests/test_approval.py` | PASS |
| `pytest -q tests/test_pre_approval_checks.py` | PASS |
| `pytest -q tests/test_immutability_snapshot.py` | PASS |
| `LLM_PROVIDER=mock pytest -q tests/test_proposal_schema.py` | PASS |
| `LLM_PROVIDER=mock pytest -q tests/test_proposal_pipeline.py` | PASS |
| `pytest -q` | PASS, 160 tests |
| `cd frontend && npm run build` | PASS |
| `make test` | PASS; backend, Vitest 6 tests và frontend build |
| `make quality-gate` | PASS; BR-06 và BR-10 |

Tất cả TC-M5-001 đến TC-M5-012 đã exit `0` trong lần chạy cuối. Cảnh báo `StarletteDeprecationWarning` và npm config warnings không làm fail acceptance.

## Handoff bổ sung

Các finding HIGH trong review đã được xử lý và regression coverage đã được bổ sung. Preview cần được recreate/rebuild trước khi đánh giá lại UI customer-facing để xác nhận bản build mới chứa renderer quotation và fixture ngôn ngữ mới.
