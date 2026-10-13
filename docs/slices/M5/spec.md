# Slice Spec — M5 Proposal + báo giá + cổng duyệt

| Thuộc tính | Giá trị |
|---|---|
| Tên tài liệu | Đặc tả milestone M5 — Proposal, báo giá và hai cấp duyệt |
| Phiên bản | 1.0 |
| Ngày | 2026-10-10 |
| Trạng thái | Sẵn sàng cho bước Build |
| Vai trò | Solution Architect |
| Nguồn | `AGENTS.md`, `docs/05_roadmap/roadmap.md` §7, `docs/04_architecture/` (4 file), `docs/slices/M4/spec.md`, `docs/slices/M4/handoff_to_build.md`, `docs/03_requirements/srs.md` FR-040/042/043/044 |

> **Điều kiện trước khi build:** M4 phải có WBS 3 cấp, schedule và `locked` guard đã được test. Bộ số rate card,
> overhead, tỉ giá, dự phòng và quy tắc làm tròn là **dữ liệu giả lập**, phải được BA/PM xác nhận trước khi dùng
> trong fixture. Mọi số trong tài liệu này chỉ mô tả contract/công thức; không phải báo giá thật.

## 1. Phạm vi

### 1.1 Slice này giao

M5 cung cấp vertical slice từ WBS/schedule M4 đến proposal có giá và luồng duyệt:

1. Đọc rate card YAML hiệu lực và tính báo giá bằng code theo vai trò, offshore/onsite, overhead PM/BrSE,
   mô hình hợp đồng, dự phòng, chi phí vận hành, tỉ giá có ngày hiệu lực, thuế và làm tròn.
2. Hiển thị dấu vết tính toán, `內訳`, thời hạn hiệu lực 見積書 và so sánh với ngân sách khách nếu có.
3. Kích hoạt B6 để LLM viết proposal Markdown theo `vi`/`en`/`ja`, có mục Giả định và Rủi ro; LLM không
   được viết tiền, man-day hay ngày lịch.
4. Cho presales xem và sửa các trường văn bản proposal trên web; backend giữ các mục giả định/phạm vi và
   toàn bộ số liệu do code render.
5. Chạy kiểm tra trước duyệt bằng code: schema proposal, WBS ±20%, PM/QA, và trạng thái kiểm tra requirement
   (M5 ghi rõ chưa có ma trận đầy đủ; M6 nối kiểm tra không-sót).
6. Duyệt kỹ thuật bởi `ai_developer`, sau đó duyệt giá bởi `manager`; chặn tự duyệt, bắt buộc lý do khi
   từ chối, ghi audit log.
7. Khi duyệt giá thành công, snapshot số liệu và bảng chuẩn, chuyển `price_approved`, khóa hồ sơ; mở khóa phải
   do manager ghi lý do và bắt buộc duyệt lại.
8. Price gate: proposal chưa duyệt giá luôn hiển thị `[Presales điền]`, không render bất kỳ số tiền nào.

### 1.2 Không thuộc M5

- Không đọc Excel/PDF và không xây ma trận đáp ứng đầy đủ (M6); M5 chỉ tiêu thụ dữ liệu M4 và báo cáo rõ phần
  `no_requirement_file`/kiểm tra chưa khả dụng.
- Không xuất Word/PDF/Excel (M7); proposal M5 là draft Markdown xem/sửa trên web.
- Không xây trang chỉnh YAML runtime và không cho người dùng sửa rate card (M8); M5 chỉ đọc YAML/override hiệu lực.
- Không để LLM tính giá, effort, lịch, tỉ giá, thuế, dự phòng hoặc viết số tiền.
- Không thêm auth server, queue, vector DB, payment gateway hay tích hợp ERP.

## 2. Frozen API contract subset

Nguồn duy nhất là `docs/04_architecture/api_contract.md`. Trong bước chuẩn bị M5, §10.0 đã được bổ sung và ghi
nhận ở đầu contract để hoàn tất FR-050.4; không tự thêm endpoint khác.

### 2.1 `GET /api/bids/{id}/quotation` — báo giá do code tính

Response 200 phải có:

```json
{
  "contract_model": "fixed_price",
  "contingency_percent": 20.0,
  "fx_rate": {"value": 1.0, "date": "2026-10-01", "pair": "VND/VND"},
  "valid_until": "2026-11-08",
  "tax_mode": "tax_excluded",
  "totals": {
    "by_role": {"backend": {"man_day": 20.0, "rate": 3500000, "amount": 70000000}},
    "overhead": {"pm": 7000000, "brse": 0},
    "contingency_amount": 15400000,
    "operating_cost": 0,
    "subtotal": 92400000,
    "tax_excluded": 92400000,
    "tax_included": 101640000,
    "grand_total": 92400000
  },
  "budget": {"amount": 50000000, "currency": "JPY", "difference": null},
  "trace": {
    "formula": "Σ(man_day × rate) + overhead + contingency",
    "rate_card_version": 1,
    "reference_snapshot_id": 1,
    "rounding": "configured rule"
  }
}
```

- `budget` chỉ có `difference` khi hồ sơ có ngân sách; quy đổi dùng tỉ giá snapshot có ngày hiệu lực.
- Số trên là hình dạng contract minh họa, không phải fixture bắt buộc. Fixture phải ghi rõ giả lập.
- Lỗi: `404 NOT_FOUND`; `409 STATE_CONFLICT` khi chưa có WBS/schedule hoặc trạng thái không hợp lệ.

### 2.2 `POST /api/bids/{id}/approvals/tech` — duyệt kỹ thuật

Request/response đóng băng theo §9.1:

```json
{
  "decision": "approved",
  "by": "ai_developer",
  "comment": "Đã kiểm tra WBS và lịch",
  "skip_with_reason": null
}
```

- `decision` là `approved|rejected|skip`; `rejected` cần `comment`; `skip` cần `skip_with_reason`.
- Danh tính authoritative lấy từ `X-Role`/`X-User`, không tin `by` trong body.
- Thành công chuyển hồ sơ sang `waiting_price_approval`; từ chối chuyển `rejected`.

### 2.3 `POST /api/bids/{id}/approvals/price` — duyệt giá

Request:

```json
{
  "decision": "approved",
  "by": "manager_linh",
  "contract_model": "fixed_price",
  "contingency_percent": 20.0,
  "comment": "Đồng ý mức giá"
}
```

- `contract_model`: `fixed_price|lab_type|hybrid`; đổi mô hình phải tính lại báo giá bằng code trước khi duyệt.
- `by == bids.created_by` trả `409 STATE_CONFLICT`; kiểm tra ở service layer.
- Chạy pre-approval checks trước quyết định; có `fail` trả `422 CHECK_FAILED`, không khóa.
- `rejected` cần comment và chuyển `rejected`; proposal vẫn giữ placeholder.
- `approved` trả `status=price_approved`, `locked=true`, `checks_report[]`; lưu approval, snapshot và changelog.

### 2.4 `POST /api/bids/{id}/unlock` — mở khóa

Request `{ "reason": "Khách thay đổi phạm vi", "by": "manager_linh" }`.
Chỉ manager; reason bắt buộc; trả `{ "locked": false, "status": "waiting_price_approval" }`.
Mọi thay đổi WBS/effort/giá sau đó phải tạo quotation mới và duyệt lại.

### 2.5 `GET/PUT /api/bids/{id}/proposal` — draft proposal trên web

Endpoint này được bổ sung trong `api_contract.md` §10.0 và là phần frozen của M5.

GET response:

```json
{
  "bid_id": 1,
  "sections": {
    "introduction": "...",
    "solution_overview": "...",
    "approach": "...",
    "risks": "...",
    "conclusion": "..."
  },
  "assumptions_phrased": ["..."],
  "scope_out_phrased": ["..."],
  "price_gate": "placeholder",
  "editable": true,
  "updated_at": "2026-10-10T10:00:00Z"
}
```

PUT nhận `{sections: {...}, by: "presales"}`. Section không rỗng; không nhận giá/man-day/date; các mục
`assumptions_phrased` và `scope_out_phrased` không bị client ghi đè. Số liệu render từ quotation/schedule
server-side. Lỗi dùng envelope chuẩn `VALIDATION_ERROR`, `NOT_FOUND`, `STATE_CONFLICT`.

## 3. LLM steps chạm tới

### 3.1 B4/B5 và input M4

M5 không thay đổi schema B4/B5. M5 nhận `solution_choices`, WBS và schedule đã persist; mọi số được truyền
cho module code, không đưa cho LLM dưới dạng quyền ghi.

### 3.2 B6 — Proposal Markdown

**Input context:** hướng giải pháp và lý do, kiến trúc/rủi ro, tóm tắt WBS không chứa số thô, danh sách giả định,

**Output JSON schema** giữ đúng `llm_pipeline.md` §7:

```json
{
  "sections": {
    "introduction": "string — theo ngôn ngữ khách",
    "solution_overview": "string — theo ngôn ngữ khách",
    "approach": "string — theo ngôn ngữ khách",
    "risks": "string — theo ngôn ngữ khách",
    "conclusion": "string — theo ngôn ngữ khách"
  },
  "assumptions_phrased": ["string — theo ngôn ngữ khách"],
  "scope_out_phrased": ["string — theo ngôn ngữ khách"]
}
```

Validation bắt buộc: `extra="forbid"`; section không rỗng; đủ số mục giả định/phạm vi theo input; không chứa
tiền tệ + chữ số, từ khóa `man-day`, `person-day`, `MD`, hoặc ngày lịch. Sai schema/vi phạm price-number rule
retry tối đa 2, sau đó `PIPELINE_ERROR` với `details.step=proposal`; không tự sửa bằng heuristic.

**Mock responses cần có:**

| Fixture | Mục đích |
|---|---|
| `proposal_vi_good` | proposal tiếng Việt đủ section, giả định/rủi ro |
| `proposal_en_good` | kiểm tra ngôn ngữ khách en |
| `proposal_ja_good` | kiểm tra ngôn ngữ khách ja, có 前提条件/スコープ外 |
| `proposal_with_money` | chứa `¥`, `$`, `₫` + chữ số → retry rồi fail |
| `proposal_with_man_day` | chứa man-day/MD → retry rồi fail |
| `proposal_missing_assumption` | thiếu giả định → cảnh báo/retry theo contract |
| `proposal_bad_schema` | thiếu section/field lạ → retry ≤ 2 rồi fail rõ |

Mọi fixture 100% hư cấu, không chứa email/SĐT thật. Gateway duy nhất là `LLMClient`; test/CI dùng `mock`.
Không gọi LLM khi sửa draft, tính quotation, chạy checks, duyệt hoặc mở khóa.

## 4. Backend và frontend tasks

### 4.1 Backend

| File | Hành động | Nội dung |
|---|---|---|
| `backend/app/reference/rate_card.yaml` | Tạo | Đơn giá vai trò offshore/onsite, overhead, FX có ngày hiệu lực, tax/rounding, operating cost; ghi `giả lập` + version |
| `backend/app/models/quotation.py` | Tạo | Bảng `quotations` theo data model §11, lưu totals và snapshot |
| `backend/app/models/approval.py` | Tạo | Bảng `approvals`, checks report, trạng thái và lý do |
| `backend/app/models/proposal_draft.py` | Tạo | Bảng `proposal_drafts`, sections, assumptions/scope-out |
| `backend/app/models/reference_snapshot.py` | Tạo | Snapshot effective YAML dùng cho bất biến giá |
| `backend/app/models/__init__.py` | Cập nhật | Import các model mới |
| `backend/app/services/reference_service.py` | Cập nhật | `load_rate_card()` và validate vai trò, currency, FX, rounding |
| `backend/app/services/quotation_engine.py` | Tạo | Tính totals, overhead trên phần offshore, contingency theo contract, tax, FX, rounding; thuần code |
| `backend/app/services/check_engine.py` | Cập nhật | Checks schema, ±20%, PM/QA; giữ placeholder không có ma trận M6 |
| `backend/app/services/approval_service.py` | Tạo | SoD, tech/price transition, reject, checks, audit |
| `backend/app/services/lock_service.py` | Cập nhật | khóa sau duyệt, manager unlock, reason, snapshot/re-approval |
| `backend/app/services/proposal_service.py` | Tạo | đọc/sửa draft, render price gate, giữ assumptions/scope-out |
| `backend/app/api/routers/quotation.py` | Tạo | `GET /quotation` |
| `backend/app/api/routers/approvals.py` | Tạo | tech/price/unlock endpoints |
| `backend/app/api/routers/proposal.py` | Tạo | `GET/PUT /proposal` |
| `backend/app/api/routers/__init__.py` | Cập nhật | include M5 routers |
| `backend/app/schemas/api_schemas/quotation.py` | Tạo | Quotation response/trace/budget |
| `backend/app/schemas/api_schemas/approval.py` | Tạo | request/response/check report |
| `backend/app/schemas/api_schemas/proposal.py` | Tạo | draft GET/PUT; không có field tiền/man-day/date trong input |
| `backend/app/schemas/llm_schemas/proposal.py` | Tạo | B6 schema, `extra=forbid`, validators không số |
| `backend/app/pipeline/steps/b6_proposal.py` | Tạo | prompt → gateway → validation → persist draft; retry ≤2 |
| `backend/app/pipeline/orchestrator.py` | Cập nhật | kích hoạt B6 sau WBS; finalize về `waiting_tech_approval` |
| `backend/app/reference/*.yaml` | Đọc | effort/factors/payment/snapshot đầu vào; không sửa bởi M5 |

### 4.2 Frontend

| File | Hành động | Nội dung |
|---|---|---|
| `frontend/src/api/types.ts` | Cập nhật | Quotation, Approval, CheckReport, ProposalDraft, PriceGate types |
| `frontend/src/api/client.ts` | Cập nhật | `getQuotation`, `getProposal`, `updateProposal`, `approveTech`, `approvePrice`, `unlockBid` |
| `frontend/src/pages/QuotationPage.tsx` | Tạo | Nội suy báo giá, nội dung theo vai trò, overhead, FX, dự phòng, ngân sách/chênh lệch, trace |
| `frontend/src/pages/ProposalPage.tsx` | Tạo | Markdown preview/editor, Giả định/Rủi ro, price gate rõ ràng |
| `frontend/src/pages/ApprovalsPage.tsx` | Tạo | kiểm tra trước duyệt, duyệt kỹ thuật/giá, reject reason, trạng thái khóa |
| `frontend/src/components/QuotationTrace.tsx` | Tạo | render trace do backend trả, không tính lại |
| `frontend/src/components/PriceGateNotice.tsx` | Tạo | `[Presales điền]` khi chưa approved; không hiển thị số tiền |
| `frontend/src/App.tsx` | Cập nhật | route proposal/quotation/approvals |
| `frontend/src/pages/BidDetailPage.tsx` | Cập nhật | link M5 theo trạng thái M4 và approval |

### 4.3 Shared contract

- Backend là nguồn duy nhất của quotation totals, FX, tax, rounding, checks, lock và trạng thái.
- Frontend chỉ render response; không có công thức giá, không tự so sánh ngân sách, không tự quyết định gate.
- Header `X-Role`/`X-User` là danh tính audit; body `by` chỉ để tương thích contract, không authoritative.
- Proposal editor chỉ gửi section text; server giữ/ghép giả định, scope-out và price gate.
- Tất cả request dùng `/api`; lỗi theo envelope tiếng Việt.

## 5. Acceptance criteria

### 5.1 Shell commands phải exit 0

Các lệnh roadmap M5 là bắt buộc; thêm test B6/proposal và quality gate để chứng minh FR-050.4:

```bash
cd backend && pytest -q tests/test_pricing.py
cd backend && pytest -q tests/test_pricing_mitsumorisho.py
cd backend && pytest -q tests/test_price_gate.py
cd backend && pytest -q tests/test_approval.py
cd backend && pytest -q tests/test_pre_approval_checks.py
cd backend && pytest -q tests/test_immutability_snapshot.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_proposal_schema.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_proposal_pipeline.py
cd backend && pytest -q
cd frontend && npm run build
make test
make quality-gate
```

`test_pricing.py` phải chứng minh công thức rate card + overhead + contingency + FX. `test_pricing_mitsumorisho.py`
phải chứng minh `見積有効期限`, 税抜/税込, 内訳 và làm tròn yen. Không dùng số literal của fixture như giá thật;
fixture phải ghi `DỮ LIỆU GIẢ LẬP`.

### 5.2 Kịch bản thủ công trên Preview

1. Mở hồ sơ M4 đã có WBS/schedule và chọn **Báo giá**. Kết quả: quotation do backend tính, có by-role,
   overhead, dự phòng, FX/ngày hiệu lực, 見積有効期限, tax mode, `内訳` và trace; UI không tự tính.
2. Chọn khách Nhật. Kết quả: tiền tệ hiển thị JPY, BrSE overhead theo rate card tự bật, yen được làm tròn,
   proposal có nhãn/section `前提条件` và `スコープ外` khi phù hợp.
3. Hồ sơ có ngân sách khách → thấy chênh lệch; bỏ ngân sách → cột chênh lệch biến mất.
4. Mở Proposal. Kết quả: proposal Markdown theo ngôn ngữ khách, có Giả định và Rủi ro; trước duyệt hiển thị
   `[Presales điền]` và **không có số tiền**. Sửa một section, lưu, tải lại → văn bản vẫn giữ.
5. Chọn **Duyệt kỹ thuật** bằng `X-Role: ai_developer`. Kết quả: checks pass/warning/fail; fail chặn chuyển tiếp;
   skip yêu cầu lý do.
6. Thử duyệt giá bằng cùng người tạo hồ sơ → backend trả `409`, thông báo tiếng Việt; đổi sang manager → tiếp tục.
7. Manager chỉnh mô hình hợp đồng/dự phòng → quotation tự tính lại bằng code; bấm duyệt. Kết quả: approval ghi
   checks, bid `price_approved`, `locked=true`, snapshot được lưu, proposal hiện số chính thức.
8. Với hồ sơ chưa duyệt hoặc bị từ chối → proposal vẫn placeholder, không lộ số tiền; reject bắt buộc lý do và
   cho phép sửa/gửi lại.
9. Sau khi approved, thử sửa WBS/schedule/quotation → `409 STATE_CONFLICT`; manager unlock có reason → status
   `waiting_price_approval`; sửa và duyệt lại tạo snapshot mới.

### 5.3 Test các rule AGENTS.md liên quan M5

| Rule | Test bắt buộc | Assert |
|---|---|---|
| 1 — No invented numbers | `test_pricing.py`, `test_proposal_schema.py`, `test_price_gate.py` | Giá/overhead/FX do engine; B6 không có tiền/man-day/ngày; chưa duyệt không có số tiền |
| 2 — Structured LLM | `test_proposal_pipeline.py` | schema sai hoặc proposal có số retry tối đa 2 rồi lỗi rõ |
| 3 — One gateway | mock gateway call-count test | B6 là nơi duy nhất gọi LLM; quotation/check/approval/edit draft không tăng call count |
| 4 — Ask instead of guess | pre-approval test | thiếu dữ liệu/điều kiện M4 không đoán; check fail hoặc trạng thái chặn, không tự tạo giá |
| 5 — Price gate | `test_price_gate.py` | placeholder không chứa currency + digits, kể cả proposal Markdown |
| 6 — Privacy | proposal gateway test | prompt B6 đã mask email/SĐT; fixture không có dữ liệu thật; không log key |
| 7 — Languages | `test_proposal_language.py` | vi/en/ja đúng ngôn ngữ; UI/lý do kiểm tra tiếng Việt |
| 8 — Done proven | toàn bộ §5.1 + Preview §5.2 | test và Preview đều pass |
| 9 — Keep simple | review dependency | không queue/auth server/vector DB; proposal Markdown editor nhẹ |
| 10 — Root-relative API | frontend build/guard | không hardcode host; mọi gọi API qua `/api` |

## 6. Test data

Không tạo dữ liệu khách thật. Các file cần thêm/cập nhật:

| File | Nội dung |
|---|---|
| `backend/app/reference/rate_card.yaml` | Rate card giả lập, version, vai trò offshore/onsite, overhead PM/BrSE, FX VND/JPY/USD, tax/rounding, contingency theo contract |
| `backend/tests/fixtures/pricing_cases.yaml` | Ca fixed/lab/hybrid, khách vi/en/ja, có/không ngân sách, FX khác ngày, tax và rounding |
| `backend/tests/fixtures/proposal_samples.py` | B6 good vi/en/ja và fixture sai số/thiếu giả định/schema |
| `backend/tests/test_pricing.py` | Unit test engine, không gọi LLM |
| `backend/tests/test_pricing_mitsumorisho.py` | Unit test quy ước Nhật |
| `backend/tests/test_price_gate.py` | Regex/assert không lộ tiền trước duyệt |
| `backend/tests/test_approval.py` | SoD, reject, transition, lock |
| `backend/tests/test_pre_approval_checks.py` | pass/warning/fail, chưa có matrix M6 |
| `backend/tests/test_immutability_snapshot.py` | đổi YAML sau approved không đổi quotation snapshot |
| `backend/tests/test_proposal_schema.py` | schema B6 cấm số tiền/man-day/ngày |
| `backend/tests/test_proposal_pipeline.py` | retry, persist draft, ngôn ngữ, mock gateway |
| `samples/m5_bid_fixture.json` | Hồ sơ M4 hư cấu có WBS, schedule, ngân sách tùy chọn; ghi rõ `DỮ LIỆU GIẢ LẬP` |

## 7. Rủi ro và bàn giao M6/M7

- M5 không thể kiểm tra đầy đủ “không sót requirement” trước khi M6 có requirements/evaluations; report phải ghi
  `deferred_to_m6=true` hoặc thông điệp tương đương, không giả pass.
- Rate card phải có version và snapshot; thay YAML không được làm thay đổi hồ sơ đã `price_approved`.
- Proposal B6 chỉ sinh văn bản; mọi số phải do renderer code chèn theo price gate. M7 sẽ tái sử dụng draft này để
  xuất Word/PDF/Excel.
- M5 bàn giao cho M6 trạng thái approval/check contract; bàn giao cho M7 `proposal_drafts`, quotation snapshot,
  price gate và `export_logs` expected state.

**Task Slice Spec M5 complete. Handoff cho Build ở `docs/slices/M5/handoff_to_build.md`.**
