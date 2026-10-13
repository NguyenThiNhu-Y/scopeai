# Audit FE ↔ BE — Lỗi khi Frontend gọi Backend

Ngày: 2026-10-11
Người thực hiện: Solution Architect (bước Analyze — workflow rà soát & fix lỗi FE gọi BE)
Phạm vi: `frontend/src/api/client.ts` + `frontend/src/api/events.ts` ↔ `backend/app/api/routers/*` + schemas

---

## 1. Tóm tắt

Người dùng báo **có lỗi giữa việc FE gọi BE**. Sau khi rà soát toàn diện, xác nhận **1 lỗi CRITICAL** (proposal legacy data làm vỡ luồng proposal FE↔BE), **1 lỗi MEDIUM** (CORS allow_headers lệch với header FE gửi), và một số ghi chú LOW / thông tin. Toàn bộ endpoint đã được đối chiếu 1-1 với client; không có mismatch path/method ở mức route (mọi đường dẫn FE gọi đều tồn tại ở backend). Lỗi nằm ở **shape dữ liệu** (schema cũ còn sót trong DB) chứ không phải đường dẫn.

Kết quả kiểm chứng runtime:

| Kiểm chứng | Kết quả |
|---|---|
| Backend pytest (toàn bộ) | PASS — 241 tests |
| Frontend vitest | PASS — 11 tests |
| Frontend `npm run build` | PASS |
| `GET /api/bids/110/proposal` (backend thật, LLM_PROVIDER=mock) | **HTTP 500** (ResponseValidationError) |
| Tab Proposal trong runtime report (`docs/ui_current/runtime_report.json`) | **Crash** `TypeError: Cannot read properties of undefined (reading 'split')`, headings rỗng |

---

## 2. Phương pháp

1. Dùng vibegraph-mcp (`get_architecture`, `search_graph`) để lập bản đồ module/route trước khi grep.
2. Liệt kê toàn bộ decorator route trong `backend/app/api/routers/*.py` và toàn bộ hàm gọi API trong `frontend/src/api/client.ts` + `events.ts`, đối chiếu từng cặp (method, path, request/response shape).
3. Kiểm tra dữ liệu thật trong SQLite (`backend/data/bidding.db`) cho các bảng JSON: `proposal_drafts`, `proposal_versions`, `quotations`, `schedules`, `wbs_items`.
4. Chạy backend thật (uvicorn, LLM_PROVIDER=mock) và gọi endpoint nghi vấn.
5. Chạy test thật: backend qua `python3 -c "import sys,pytest; sys.exit(pytest.main(['-q']))"` (wrapper `rtk` làm sai output `Pytest: No tests collected` — không dùng); frontend `npm test` + `npm run build`.
6. Đối chiếu với `docs/ui_current/runtime_report.json` (console error + failed requests + headings rỗng).

---

## 3. Bảng đối chiếu endpoint ↔ client

Ký hiệu: ✅ khớp · ⚠️ có vấn đề · ➖ backend có endpoint nhưng FE không gọi (ghi chú)

### 3.1 Module Bids / Pipeline / Questions

| Backend route | Client function | Kết quả |
|---|---|---|
| `GET /health` | `getHealth` | ✅ |
| `POST /bids` | `createBid` | ✅ |
| `GET /bids` | `listBids` | ✅ |
| `GET /bids/{id}` | `getBid` | ✅ |
| `POST /bids/sample` | `loadSample` | ✅ |
| `GET /bids/sample/preview` | `getSamplePreview` | ✅ |
| `PUT /bids/{id}/deal-stage` | — | ➖ FE không gọi (chỉ dùng `deal_stage` làm filter danh sách) |
| `POST /bids/{id}/pipeline/start` | `startPipeline` | ✅ |
| `GET /bids/{id}/pipeline/events` | `subscribePipelineEvents` (SSE) | ✅ |
| `POST /bids/{id}/rerun` | `rerunPipeline`, `rerunPipelineFromWbs` | ✅ |
| `GET /bids/{id}/questions` | `getQuestions` | ✅ |
| `GET /bids/{id}/questions/export` | `downloadQuestions` | ✅ |
| `POST /bids/{id}/questions/import` | `importQuestions` | ✅ |
| `POST /bids/{id}/questions/email-draft` | `createEmailDraft` | ✅ |
| `POST /bids/{id}/questions/{round}/answers` | `submitAnswers` | ✅ |

### 3.2 Module Solution / Effort / Attachments / Parse

| Backend route | Client function | Kết quả |
|---|---|---|
| `POST /bids/{id}/solution` | `chooseSolution` | ✅ |
| `GET /bids/{id}/solution` | — | ➖ FE không gọi (dùng dữ liệu từ `/evaluations`) |
| `GET /bids/{id}/effort` | `getEffort` | ✅ |
| `GET /bids/{id}/evaluations` | `getEvaluations` | ✅ |
| `POST /bids/{id}/attachments` | `uploadAttachment` | ✅ |
| `GET /bids/{id}/attachments` | `listAttachments` | ✅ |
| `PUT /bids/{id}/attachments/{aid}` | `updateAttachment` | ✅ |
| `POST /bids/{id}/parse` | `parseAttachments` | ✅ |
| `PUT /bids/{id}/parse/confirm` | `confirmParse` | ✅ |

### 3.3 Module WBS / Schedule

| Backend route | Client function | Kết quả |
|---|---|---|
| `GET /bids/{id}/wbs` | `getWbs` | ✅ |
| `PUT /bids/{id}/wbs` | `updateWbs` | ✅ |
| `POST /bids/{id}/wbs/snapshot` | `snapshotWbs` | ✅ |
| `GET /bids/{id}/schedule` | `getSchedule` | ✅ |
| `PUT /bids/{id}/schedule` | `updateSchedule` | ✅ |

### 3.4 Module Quotation / Proposal / Approval / Export / Settings

| Backend route | Client function | Kết quả |
|---|---|---|
| `GET /bids/{id}/quotation` | `getQuotation` | ✅ |
| `PUT /bids/{id}/quotation` | `updateQuotation` | ✅ |
| `GET /bids/{id}/proposal` | `getProposal` | ⚠️ **CRITICAL — legacy data → 500 / FE crash** (Finding F-01) |
| `PUT /bids/{id}/proposal` | `updateProposal` | ⚠️ cùng rủi ro F-01 (body yêu cầu đủ 8 mục; nếu FE gửi thiếu → 422) |
| `POST /bids/{id}/proposal/translate` | — | ➖ FE không gọi |
| `GET/POST /bids/{id}/proposal/versions`, `PUT .../sent` | — | ➖ FE không gọi |
| `POST /bids/{id}/approvals/tech` | `approveTech` | ✅ (header X-Role/X-User — xem F-02) |
| `POST /bids/{id}/approvals/price` | `approvePrice` | ✅ (header X-Role/X-User — xem F-02) |
| `POST /bids/{id}/unlock` | `unlockBid` | ✅ (header X-Role/X-User — xem F-02) |
| `GET /bids/{id}/exports/{docx,xlsx,pdf,bundle,requirements}` | `downloadExport` | ✅ |
| `GET /settings` | `getSettings` | ✅ |
| `PUT /settings/{key}` | `updateSetting` | ✅ (header X-Role — xem F-02) |
| `GET /history` | `getHistory` | ✅ |
| `GET/PUT /bids/{id}/bid-qualification` | — | ➖ FE không gọi |

**Kết luận đối chiếu:** không có lỗi path/method. Toàn bộ lỗi nằm ở **shape/kiểu dữ liệu** và **header**.

### 3.5 Kiểm tra shape request/response (endpoint mutation)

| Endpoint | Body FE gửi | Schema BE nhận | Kết quả |
|---|---|---|---|
| `PUT /bids/{id}/schedule` | `ScheduleUpdateRequest` (`types.ts:619`): `start_date`, `buffer_days`, `working_calendar`, `team_allocation`, `payment_milestones?`, `go_no_go_gap_working_days?`, `gantt_break_interval?`, `by` | `ScheduleUpdateIn` (`schedule.py:68`): bắt buộc `start_date`, `team_allocation`; phần còn lại optional | ✅ khớp |
| `PUT /bids/{id}/wbs` | `{changes, by, note}` (`client.ts:344-354`) | `WbsEditIn` (`wbs.py:78`): `changes` (min 1), `by?`, `note?` | ✅ khớp |
| `POST /bids/{id}/questions/{round}/answers` | `{answers: AnswerItem[]}` | `AnswersIn` (`question.py:30`): `answers: list[AnswerItemIn]` | ✅ khớp |
| `PUT /bids/{id}/quotation` | `Record<string, unknown>` (loose) | `QuotationSettingsIn` (`quotation.py:9`): toàn bộ field optional, có range validate | ✅ tương thích |
| `PUT /bids/{id}/proposal` | `{sections, by}` | `ProposalUpdateIn` (`proposal.py:15`): `sections` bắt buộc đủ 8 mục | ⚠️ ràng buộc 8 mục — liên quan F-01 |

Các response shape quan trọng khác (proposal 8 mục, quotation totals, schedule) đã kiểm tra ở mục Findings.

---

## 4. Findings

### F-01 — CRITICAL: Proposal legacy data (schema cũ 5 mục) làm vỡ luồng proposal FE↔BE

**Vị trí:**
- Dữ liệu: bảng `proposal_drafts.sections` (JSON) — `backend/app/models/proposal_draft.py:10`
- Backend: `backend/app/services/proposal_service.py:33` (`to_out` iterate `row.sections.items()`), schema yêu cầu 8 mục — `backend/app/schemas/api_schemas/proposal.py:5-14`
- Frontend: `frontend/src/pages/ProposalPage.tsx:51` (`sections[key].split('{{QUOTATION}}')`), `:59` (`Object.values(sections).some(v => v.includes(...))`)

**Bằng chứng:**
1. DB còn **14 hồ sơ (bid 80..110)** lưu sections theo schema cũ **5 mục**:
   ```json
   {"introduction": "...", "solution_overview": "...", "approach": "...", "risks": "...", "conclusion": "..."}
   ```
   Thiếu `requirements_understanding`, `schedule`, `team`, `assumptions_and_scope`; có key thừa `conclusion`. (Bid 112 đã ở schema mới 8 mục.)
2. `GET /api/bids/110/proposal` (backend thật, LLM_PROVIDER=mock) → **HTTP 500** do `ProposalOut` (response_model) không validate được sections thiếu key.
3. `docs/ui_current/runtime_report.json`: tab `08_proposal` có `"headings": []` (rỗng) kèm console error:
   `TypeError: Cannot read properties of undefined (reading 'split')` tại `assets/index-BeA8-9mv.js:69` → chính là `sections[key].split("{{QUOTATION}}")` trong `proposalMarkdown` useMemo (đã xác minh bằng cách giải mã dòng 69 của bundle minified).
4. `proposal_versions`: 0 rows; `translations`: rỗng → chưa bị ảnh hưởng nhưng cùng rủi ro nếu có dữ liệu cũ.

**Cách tái hiện:** mở hồ sơ có proposal row schema cũ (bid 80–110) → tab Proposal. Bản build hiện tại: tab trắng / lỗi tải. Bản build cũ: crash toàn trang.

**Đề xuất fix (cho bước Implement):**
- Backend: normalize sections khi đọc trong `proposal_service.get_or_create`/`to_out`: điền đủ 8 key theo `SECTION_NAMES` (thiếu → `[Đang chờ proposal]`), loại bỏ key thừa (`conclusion`). Áp dụng tương tự cho `translations` nếu cần. Không cần migrate DB thủ công (fix ở lớp đọc — BR-09).
- Frontend: phòng thủ trong `ProposalPage.tsx` — không crash khi `sections[key]` undefined (`sections[key] ?? ''`), và `Object.values(sections).some(v => v?.includes(...))`.
- Regression test backend: proposal row 5 mục cũ → GET trả 200 đủ 8 mục.

### F-02 — MEDIUM: CORS `allow_headers` lệch với header FE gửi

**Vị trí:**
- `backend/app/main.py:36-42` — `allow_headers=["Content-Type", "Accept", "X-Actor"]`
- FE gửi `X-Role` và `X-User`: `frontend/src/api/client.ts:172` (updateSetting → `X-Role: manager`), `:424` (approveTech → `X-Role` + `X-User`), `:431` (approvePrice), `:438` (unlockBid)
- Backend đọc: `backend/app/api/deps.py:35-40` (`get_identity` chỉ đọc `X-Actor`/`X-User`; **không đọc `X-Role`**)

**Ảnh hưởng:** hiện chưa chặn vì Preview/dev dùng proxy cùng origin (trình duyệt không ép CORS). Nhưng nếu truy cập cross-origin (hoặc đổi cấu hình proxy), preflight sẽ fail vì `X-Role`/`X-User` không nằm trong `Access-Control-Allow-Headers`.

**Đề xuất fix:**
- Thêm `X-Role`, `X-User` vào `allow_headers` trong `main.py` (nếu FE còn gửi), **hoặc** bỏ header không dùng ở FE.
- `X-Role` không được backend đọc → nên bỏ khỏi client.ts hoặc ghi rõ là header dự phòng (tránh hiểu nhầm là cơ chế phân quyền — GATE-01 đã ghi chú đây là mô hình header giả lập).

### F-03 — LOW: `quotations.totals` có biến thể thiếu key ở row cũ

**Vị trí:** `backend/app/services/quotation_engine.py` (quotation_to_out) — quotation id 8, 9 (bid 104, 105) thiếu `payment_plan`, `odc_fte_months` trong `totals`; quotation id 10 (bid 112) có đủ.

**Ảnh hưởng:** FE đã có fallback (`docs/WORKSTREAM_A_HANDOFF.md`: fallback `payment_milestones` khi thiếu `payment_plan`; `BidPlanTab.tsx` guard `!= null` cho `odc_fte_months`) → không crash. Ghi nhận để bước Implement cân nhắc chuẩn hoá nếu muốn nhất quán.

### F-04 — INFO: 409 state conflict trên bid 110 (effort/schedule/quotation/wbs)

`docs/ui_current/runtime_report.json` liệt kê nhiều request 409 cho `/effort`, `/schedule`, `/quotation`, `/wbs` của bid 110. Đây là **hành vi đúng theo thiết kế** (`state_conflict` — pipeline chưa tới bước tương ứng), không phải lỗi FE↔BE. Không cần sửa.

### F-05 — INFO: SSE qua proxy Preview

`GET /bids/{id}/pipeline/events` (SSE) đi qua `vite.preview.config.ts` proxy `/api → backend:8000`. Backend set `X-Accel-Buffering: no`; proxy http-proxy của Vite không buffer SSE. Không phát hiện lỗi.

---

## 5. Baseline test (bằng chứng thật)

| Hạng mục | Lệnh | Kết quả |
|---|---|---|
| Backend | `python3 -c "import sys,pytest; sys.exit(pytest.main(['-q']))"` (từ `backend/`) | **241 passed** |
| Frontend | `npm test` (từ `frontend/`) | **11 passed** |
| Frontend build | `npm run build` (từ `frontend/`) | **PASS** (2.91s) |
| Runtime probe | uvicorn + `GET /api/bids/110/proposal` | **HTTP 500** |

Lưu ý môi trường: wrapper `rtk` nuốt output pytest (`Pytest: No tests collected`) — mọi lệnh pytest phải chạy qua `python3 -c "import sys,pytest; sys.exit(pytest.main(['-q']))"` để có kết quả thật.

---

## 6. Đề xuất thứ tự fix (cho bước Implement)

1. **(CRITICAL)** Backend: normalize proposal sections legacy 5 mục → 8 mục ở `proposal_service`; thêm regression test.
2. **(CRITICAL)** Frontend: phòng thủ `ProposalPage.tsx` khỏi `sections[key]` undefined.
3. **(MEDIUM)** CORS: thêm `X-Role`, `X-User` vào `allow_headers` (hoặc bỏ header thừa ở FE); ghi chú `X-Role` không được backend đọc.
4. **(LOW)** Cân nhắc chuẩn hoá `quotations.totals` cũ (không bắt buộc).

---

## 7. Handoff

Bàn giao cho bước **Fix** (backend-dev + frontend-dev song song) theo Findings F-01, F-02, F-03 ở trên. Báo cáo này là nguồn duy nhất cho việc sửa; sau khi fix, bước Verify phải chạy lại toàn bộ test + probe runtime `GET /api/bids/110/proposal` trả 200 đủ 8 mục.