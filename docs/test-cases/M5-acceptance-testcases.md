# Test Cases — M5 Proposal + báo giá + cổng duyệt (Acceptance)

| Thuộc tính | Giá trị |
|---|---|
| Milestone | M5 — Proposal, báo giá và hai cấp duyệt |
| Chuẩn template | IPA (mặc định — mirror `docs/test-cases/M4-acceptance-testcases.md`) |
| Định dạng | Markdown |
| Nguồn | `docs/slices/M5/spec.md` §5.1/§5.2/§5.3, `docs/slices/M5/handoff_to_test.md`, `AGENTS.md` |
| Môi trường | Preview :5173, proxy `/api`, `LLM_PROVIDER=mock` |
| Ngày | 2026-10-10 |

## A. Acceptance shell commands

| TC-ID | 観点 | Test Item | Procedure | Expected Result |
|---|---|---|---|---|
| TC-M5-001 | 正常系 | Pricing engine suite | Chạy `cd backend && pytest -q tests/test_pricing.py` | Exit 0; công thức rate × MD, overhead, contingency, FX được kiểm tra |
| TC-M5-002 | 正常系 | Mitsumorisho suite | Chạy `cd backend && pytest -q tests/test_pricing_mitsumorisho.py` | Exit 0; 見積有効期限, 税抜/税込, 内訳, rounding được kiểm tra |
| TC-M5-003 | Security | Price gate suite | Chạy `cd backend && pytest -q tests/test_price_gate.py` | Exit 0; trước duyệt không lộ currency + digits |
| TC-M5-004 | 異常系 | Approval suite | Chạy `cd backend && pytest -q tests/test_approval.py` | Exit 0; SoD, reject, transition, lock được kiểm tra |
| TC-M5-005 | 異常系 | Pre-approval checks | Chạy `cd backend && pytest -q tests/test_pre_approval_checks.py` | Exit 0; pass/warning/fail và deferred M6 được kiểm tra |
| TC-M5-006 | 準正常系 | Snapshot immutability | Chạy `cd backend && pytest -q tests/test_immutability_snapshot.py` | Exit 0; đổi YAML không đổi quotation đã snapshot |
| TC-M5-007 | Security | Proposal schema | Chạy `LLM_PROVIDER=mock pytest -q tests/test_proposal_schema.py` | Exit 0; schema chặn tiền, man-day, ngày và field lạ |
| TC-M5-008 | 異常系 | Proposal pipeline | Chạy `LLM_PROVIDER=mock pytest -q tests/test_proposal_pipeline.py` | Exit 0; retry tối đa 2, persist draft, ngôn ngữ và mock gateway đúng |
| TC-M5-009 | 正常系 | Full backend suite | Chạy `cd backend && pytest -q` | Exit 0 |
| TC-M5-010 | 正常系 | Frontend build | Chạy `cd frontend && npm run build` | Exit 0; TypeScript và Vite build thành công |
| TC-M5-011 | 正常系 | Full project test | Chạy `make test` | Exit 0; backend, frontend tests và build pass |
| TC-M5-012 | Security | Quality gate | Chạy `make quality-gate` | Exit 0; BR-06 và BR-10 pass |

## B. Preview manual acceptance

### TC-M5-013: Health và sample bid qua Preview

| Field | Content |
|---|---|
| **TC-ID** | TC-M5-013 |
| **機能名** | Preview health/sample |
| **画面** | `/`, `/api/health`, `/api/bids/sample` |
| **観点** | 正常系 |
| **事前条件** | Preview frontend/backend đang chạy; mock LLM |
| **テスト手順** | 1. Mở `/` 2. Gọi health qua UI/API 3. Tạo hồ sơ sample |
| **期待結果** | Frontend render không lỗi; health 200 với `status=ok`, `database=ok`, `llm_provider=mock`; sample trả bid id |
| **備考** | spec §5.2, handoff §3 |

### TC-M5-014: Báo giá có trace và price gate

| Field | Content |
|---|---|
| **TC-ID** | TC-M5-014 |
| **機能名** | Quotation display |
| **画面** | `/bids/{id}/quotation` |
| **観点** | 正常系 / Security |
| **事前条件** | Bid sample có WBS/schedule |
| **テスト手順** | 1. Mở Báo giá 2. Đọc by-role, overhead, contingency, FX, tax, trace |
| **期待結果** | Dữ liệu do backend trả; có formula/rate card/snapshot/rounding; trước price approval proposal chỉ có `[Presales điền]`, không có currency + digits |
| **備考** | spec §2.1, §5.2-1, AGENTS rule 1/5 |

### TC-M5-015: Proposal Markdown theo ngôn ngữ khách và lưu chỉnh sửa

| Field | Content |
|---|---|
| **TC-ID** | TC-M5-015 |
| **機能名** | Proposal editor |
| **画面** | `/bids/{id}/proposal` |
| **観点** | 正常系 / 準正常系 |
| **事前条件** | Proposal draft đã sinh bằng mock LLM |
| **テスト手順** | 1. Mở Proposal 2. Xác nhận Introduction/Approach/Risks/Assumptions 3. Sửa một section bằng text hợp lệ 4. Lưu 5. Reload |
| **期待結果** | Proposal đúng ngôn ngữ khách; có Giả định/Rủi ro; section sửa được giữ; assumptions/scope-out và price gate không bị client ghi đè |
| **備考** | spec §2.5, §3.2 |

### TC-M5-016: Duyệt kỹ thuật đúng role, sai role và reject reason

| Field | Content |
|---|---|
| **TC-ID** | TC-M5-016 |
| **機能名** | Technical approval |
| **画面** | `/bids/{id}/approvals` |
| **観点** | 正常系 / 異常系 |
| **事前条件** | Bid ở `waiting_tech_approval` |
| **テスト手順** | 1. Thử approve không có `X-Role: ai_developer` 2. Reject không comment 3. Approve bằng `ai_developer` |
| **期待結果** | Sai role bị chặn; reject thiếu lý do bị chặn; approve hợp lệ chuyển `waiting_price_approval`, có checks/audit |
| **備考** | spec §2.2, §5.2-5 |

### TC-M5-017: SoD price approval và lock sau duyệt

| Field | Content |
|---|---|
| **TC-ID** | TC-M5-017 |
| **機能名** | Price approval |
| **画面** | `/bids/{id}/approvals` |
| **観点** | 正常系 / 異常系 |
| **事前条件** | Tech approval thành công; created_by khác manager |
| **テスト手順** | 1. Dùng creator duyệt giá 2. Dùng manager duyệt giá 3. Đọc bid/proposal |
| **期待結果** | Creator nhận 409 `STATE_CONFLICT`; manager approval chuyển `price_approved`, `locked=true`, snapshot/checks được lưu; proposal render giá chính thức |
| **備考** | spec §2.3, AGENTS rule 5 |

### TC-M5-018: Unlock manager có reason và re-approval

| Field | Content |
|---|---|
| **TC-ID** | TC-M5-018 |
| **機能名** | Unlock and re-approval |
| **画面** | `/bids/{id}/approvals`, WBS/quotation |
| **観点** | 準正常系 / 異常系 |
| **事前条件** | Bid `price_approved`, `locked=true` |
| **テスト手順** | 1. Unlock không phải manager 2. Manager unlock thiếu reason 3. Manager unlock có reason 4. Thử sửa và đọc trạng thái |
| **期待結果** | Hai trường hợp đầu bị chặn; unlock hợp lệ trả `locked=false`, `waiting_price_approval`; thay đổi sau đó yêu cầu quotation/snapshot và duyệt lại |
| **備考** | spec §2.4, §5.2-9 |

### TC-M5-019: Input validation và XSS/SQLi trong proposal

| Field | Content |
|---|---|
| **TC-ID** | TC-M5-019 |
| **機能名** | Proposal validation/security |
| **画面** | PUT `/api/bids/{id}/proposal` |
| **観点** | 境界値 / Security |
| **事前条件** | Proposal draft tồn tại |
| **テスト手順** | 1. Gửi section rỗng/whitespace 2. Gửi `<script>alert(1)</script>` 3. Gửi SQLi `'); DROP TABLE bids;--` 4. Gửi field `amount`/`man_day` |
| **期待結果** | Input không hợp lệ trả validation envelope hoặc được encode an toàn; không thực thi script; không lỗi 500; field số bị từ chối và assumptions/scope-out không bị ghi đè |
| **備考** | spec §2.5, AGENTS rule 5/6 |
