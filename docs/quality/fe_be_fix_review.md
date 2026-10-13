# Review — Fix FE↔BE (bước Verify)

Ngày: 2026-10-11
Người thực hiện: Code Reviewer (bước Verify — workflow rà soát & fix lỗi FE gọi BE)
Nguồn: `docs/quality/fe_be_audit.md` (F-01..F-05) + `docs/quality/handoff_fe_be_fix.md` + handoff 2 nhánh
Phạm vi: CODE REVIEW — chỉ đọc/phân tích, không sửa code.

---

## Kết luận

**APPROVED** ✅ — cho phạm vi audit F-01 (CRITICAL) và F-02 (MEDIUM). Fix giải quyết đúng root cause, đúng lớp đọc (BR-09), không đổi hành vi dữ liệu hợp lệ, toàn bộ test/build pass khi chạy lại độc lập. Kèm **2 warning follow-up** (không chặn): export path vẫn đọc `sections` thô (cùng root cause F-01 nhưng ngoài phạm vi audit), và 1 lỗ hổng nhỏ về cast kiểu trong `_normalize_sections`.

Bằng chứng chạy lại độc lập (bước Verify):

| Kiểm chứng | Lệnh | Kết quả |
|---|---|---|
| Backend pytest (toàn bộ) | `python3 -c "import sys,pytest; sys.exit(pytest.main(['-q','-rN']))"` (từ `backend/`) | **exit 0 — 245 passed** (72+72+72+29) |
| Regression mới | `pytest tests/test_proposal_legacy_normalize.py` | **4 passed** |
| Frontend test | `npm test` (từ `frontend/`) | **11 passed** |
| Frontend build | `npm run build` | **PASS** (tsc -b && vite build) |
| Dữ liệu legacy thật | SELECT read-only `proposal_drafts` + chạy `_normalize_sections` lên 15 row | 14 row 5 mục (đúng audit), 1 row 8 mục; **0 row fail normalize** |

Lưu ý: repo gần như toàn bộ là file untracked nên `git diff` rỗng — review theo cách đọc trực tiếp file đã sửa và đối chiếu với audit/handoff.

---

## 1. Tính đúng đắn — fix có giải quyết đúng root cause không?

### 1.1 Root cause được xác nhận lại trên dữ liệu thật ✅

Đọc read-only `backend/data/bidding.db` (không ghi đè gì): đúng **14 hồ sơ** (bid 80, 81, 83, 88, 89, 90, 91, 92, 96, 97, 104, 105, 106, 110) lưu `proposal_drafts.sections` **5 mục** kèm key thừa `conclusion`; bid 112 đã ở schema 8 mục — khớp chính xác mô tả F-01 trong audit.

### 1.2 `_normalize_sections` xử lý đúng mọi trường hợp ✅

`backend/app/services/proposal_service.py:14-31`:
- Điền đủ 8 key theo `SECTION_NAMES`; key thiếu → `[Đang chờ proposal]` (PLACEHOLDER).
- Giá trị rỗng/whitespace → PLACEHOLDER (tránh vi phạm `ProposalSections.min_length=1` → tránh 500).
- Loại key thừa (`conclusion`) — không xuất hiện trong output.
- Chạy thử lên **toàn bộ 15 row thật** trong DB: 15/15 trả đủ 8 key, không key rỗng, không còn `conclusion` → `ProposalOut` validate được (hết 500).

### 1.3 Fix ở lớp đọc — không ghi đè DB (BR-09) ✅

- `to_out()` (`proposal_service.py:63`) và `translate()` (`:78`) gọi `_normalize_sections`/`_normalize_translations` **chỉ để tạo response**; không gán ngược vào `row.sections`.
- DB chỉ bị ghi khi: (a) user `PUT` — `update()` `:70` lưu `data.sections.model_dump()` (body đã validate đủ 8 mục), (b) tạo row mới — `get_or_create()` `:46` dùng `DEFAULT_SECTIONS` 8 mục. Không có migrate DB — đúng BR-09.

### 1.4 Không đổi hành vi dữ liệu hợp lệ ✅

- Với row 8 mục hợp lệ: `str(value)` với value là `str` là phép đồng nhất → giá trị giữ nguyên, thứ tự key theo `SECTION_NAMES` (không đổi nội dung).
- Logic thay `{{QUOTATION}}` bằng `quotation_markdown` trong `to_out` (`:63`) giữ nguyên so với trước fix (trước: thay trên `row.sections.items()`; sau: thay trên dict đã normalize) — hành vi với dữ liệu hợp lệ không đổi.
- `document.table_of_contents` = `list(sections)` → đủ 8 mục (FE render headings từ đây nếu dùng).

### 1.5 CORS F-02 — hai phía đều được xử lý ✅

- `backend/app/main.py:40`: `allow_headers` = `["Content-Type", "Accept", "X-Actor", "X-Role", "X-User"]` — đúng đề xuất audit.
- `frontend/src/api/client.ts`: đã bỏ `X-Role` khỏi cả 4 request (`updateSetting` :169-175, `approveTech` :421-426, `approvePrice` :428-433, `unlockBid` :435-439); grep toàn `frontend/src` → **0** match `X-Role`. Giữ `X-User` (backend `deps.py:35-40` có đọc). Header FE hiện gửi (`Content-Type`, `X-User`) đều nằm trong allow_headers → preflight cross-origin không fail.
- Ghi chú đúng: `X-Role` không được backend đọc — nay FE không còn gửi, backend vẫn cho phép (vô hại, đúng handoff).

---

## 2. Tuân thủ AGENTS.md (constitution)

| Rule | Đánh giá | Bằng chứng |
|---|---|---|
| BR-01 — không bịa số liệu | ✅ | Normalize chỉ điền placeholder chữ `[Đang chờ proposal]`, không sinh effort/man-day/giá/ngày. |
| BR-10 — không hardcode URL tuyệt đối | ✅ | `client.ts:49` `API_BASE = '/api'`; grep `localhost\|127.0.0.1\|http://\|https://` trong `frontend/src` → 0 match. |
| BR-06 — không lộ secret | ✅ | Không có secret/key trong 5 file đã sửa. |
| Envelope lỗi giữ nguyên | ✅ | `main.py` exception handlers (`register_exception_handlers`) không đụng tới. |
| BR-03 — mock LLM trong test | ✅ | `conftest.py:11` ép `LLM_PROVIDER=mock`; test mới không gọi LLM (chỉ DB + API). |
| BR-09 — không migrate DB | ✅ | Xem mục 1.3. |

---

## 3. Độ phủ — regression test có bắt đúng lỗi không?

`backend/tests/test_proposal_legacy_normalize.py` — **4 test, đều pass khi chạy lại độc lập**:

1. `test_legacy_5_sections_get_returns_8` — **bắt đúng lỗi gốc**: trước fix, GET row 5 mục → `ProposalOut` validate fail → 500 → test fail; sau fix → 200, đủ 8 key, không `conclusion`, placeholder cho key thiếu, `document.table_of_contents` đủ 8. Đây chính là test chặn hồi quy F-01.
2. `test_legacy_empty_values_filled_with_placeholder` — giá trị rỗng/whitespace → placeholder (bắt đúng nhánh `min_length=1`).
3. `test_legacy_translate_does_not_500` — endpoint translate với row legacy, không truyền sections → 200, translations đủ 8 key.
4. `test_update_persists_8_sections_and_db_is_fixed` — PUT ghi đủ 8 mục xuống DB, không còn key thừa (đúng "chỉ ghi đè khi user PUT").

Cô lập DB tốt: `conftest.py:23-33` `_tmp_db` monkeypatch `db.SessionLocal`/`db.engine` sang SQLite tạm mỗi test → `_seed_legacy_row` (dùng `db.SessionLocal()`) ghi đúng cùng DB với TestClient, không đụng `data/bidding.db` thật. Fixture `client` + helper `create_bid` tạo bid qua API thật (HTTP 201).

**Lỗ hổng phủ (Minor, không chặn):**
- Chưa có test cho `translations` legacy **đã tồn tại trong DB** (chỉ test luồng translate tạo mới với translations rỗng). `_normalize_translations` (`:34-38`) đơn giản nhưng chưa được kiểm chứng với shape cũ thật.
- Chưa có test khóa hợp đồng `PUT` với body 5 mục → 422 (schema vẫn enforce — hành vi mong muốn, chỉ là chưa lock).

---

## 4. FE còn chỗ nào crash với dữ liệu thiếu key không?

### 4.1 ProposalPage.tsx — 3 site đọc sections đều đã guard ✅

- `:51` — `(sections[key] ?? '').split('{{QUOTATION}}')` (chính là dòng crash `Cannot read properties of undefined (reading 'split')` trong runtime report — đã được vá).
- `:59` — `Object.values(sections).some((value) => value?.includes('{{QUOTATION}}'))`.
- `:141` — textarea `value={sections[key] ?? ''}` (tránh controlled-input undefined).
- Grep toàn `frontend/src` cho `sections[`/`.sections`: chỉ 3 site trong ProposalPage.tsx, đều đã guard — khớp handoff frontend-dev.

### 4.2 Các trang khác đọc sections/quotation — không phát hiện crash ✅

- `BidDetailPage.tsx:346-347, 494-506` — đọc `totals.grand_total/contingency_amount/operating_cost` đều nằm trong ternary `quotationQuery.data ? ...` → an toàn khi thiếu dữ liệu.
- `BidPlanTab.tsx:134` — early-return `Empty` khi `!quotation`; `:138` `PaymentTable` dùng fallback `quotation.totals.payment_plan ?? quotation.payment_milestones` (đúng ghi chú F-03); `odc_fte_months` có guard `!= null`.
- `ApprovalsPage.tsx:114-121` — ternary guard `quotation.data ? ...`.
- `QuotationPage.tsx:13-14` — early-return khi pending/error/thiếu data trước khi đọc `q.totals`.
- F-03 (quotation totals thiếu key ở row cũ) không thuộc phạm vi fix, FE đã có fallback — giữ nguyên, không chặn.

---

## Warnings (follow-up — không chặn APPROVED)

### Warning 1 — Export path vẫn đọc `sections` thô (cùng root cause F-01, ngoài phạm vi audit)
- **Vị trí**: `backend/app/services/export_service.py:35` — `sections = {key: value.replace(...) for key, value in draft.sections.items()}` (và `:28` truyền `draft.sections` thô vào `check_japanese`).
- **Mô tả**: Fix F-01 chỉ áp dụng ở lớp đọc của `proposal_service`; riêng luồng export (`GET /bids/{id}/exports/*`) vẫn đọc thẳng JSON từ DB. Với 14 hồ sơ legacy (bid 80–110), file DOCX/PDF/XLSX xuất ra sẽ **chỉ có 5 mục** và kèm heading thừa `conclusion` (vì `render_proposal` — `proposal_docx.py:10-16` — iterate đúng key có sẵn, `labels.get(key, key)` không có nhãn `conclusion`). Không crash, nhưng tài liệu xuất ra lệch hợp đồng 8 mục.
- **Đề xuất**: tái sử dụng `_normalize_sections` trong `export_service.artifacts` (và `_data` cho `check_japanese`) để export cũng ra đủ 8 mục — nên đưa vào backlog/follow-up, không thuộc điều kiện chấp nhận của audit F-01.

### Warning 2 — Cast kiểu trong `_normalize_sections` (Minor)
- **Vị trí**: `proposal_service.py:30` — `out[key] = str(value)`.
- **Mô tả**: Nếu một row legacy chứa giá trị không phải string (vd list/dict do dữ liệu hỏng), `str()` sẽ render Python repr (vd `"['a', 'b']"`) vào proposal — không crash nhưng xấu. Với dữ liệu thật hiện tại không gặp (đã kiểm 15/15 row), nên chỉ là phòng thủ.
- **Đề xuất**: `out[key] = value if isinstance(value, str) else PLACEHOLDER`.

---

## Suggestions (nice-to-have)

- Thêm test `translations` legacy trong DB (đóng lỗ hổng mục 3).
- `translate()` (`:79`) lưu bản dịch đã normalize cho ngôn ngữ được yêu cầu nhưng để nguyên bản dịch legacy của ngôn ngữ khác trong DB — nhất quán với BR-09 (đọc là chuẩn hóa), không cần sửa.

---

## Positive highlights

- Fix đúng root cause, đúng lớp đọc, không migrate DB, không đổi hành vi dữ liệu hợp lệ — đúng tinh thần BR-09.
- Regression test bắt đúng lỗi gốc (sẽ fail trước fix), cô lập DB tạm sạch, không đụng DB thật.
- FE guard tối thiểu, đúng 3 site, không đổi hành vi; grep xác nhận không còn chỗ đọc thiếu fallback.
- Cả hai hướng của F-02 đều được xử lý (backend allow + FE bỏ header thừa) — không còn header "ma" gây hiểu nhầm phân quyền.
- Toàn bộ bằng chứng (245 pytest, 11 vitest, build, probe normalize trên DB thật) được chạy lại độc lập ở bước Verify, khớp handoff.

---

## Điều kiện chấp nhận audit (§7) — đối chiếu

| Điều kiện | Kết quả |
|---|---|
| `GET /api/bids/110/proposal` trả 200 đủ 8 mục | ✅ (handoff + mô phỏng normalize trên row 110 thật → 8 key, không `conclusion`) |
| Không crash tab Proposal với hồ sơ cũ | ✅ (guard FE 3 site + backend trả đủ key) |
| Backend pytest toàn bộ | ✅ 245 passed |
| Frontend test + build | ✅ 11 passed + build PASS |