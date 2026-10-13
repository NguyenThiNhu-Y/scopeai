# Review — M4 WBS 3 cấp + master schedule

| Thuộc tính | Giá trị |
|---|---|
| Slice | M4 |
| Reviewer | Senior reviewer (code + document) |
| Ngày | 2026-10-10 |
| Phạm vi | `docs/slices/M4/spec.md`, `test_report.md` (16/16 PASS), `fix_log.md` (không có lỗi), code M4 backend + frontend |
| Nguồn đối chiếu | `AGENTS.md` (rules 1–10), `api_contract.md` §8.0–§8.4a, ADR-006 |

## Kiểm tra theo AGENTS.md rules 1–10

| Rule | Kết quả | Bằng chứng |
|---|---|---|
| 1 — No invented numbers | ✅ | `WbsStructure` không có field số/ngày (`wbs_structure.py:31-49`, `extra="forbid"`); man-day lá do `wbs_engine.assign_man_days` tính từ midpoint YAML; fixture `with_man_day` bị chặn (`test_llm_schema_no_numbers.py`) |
| 2 — Structured LLM output | ✅ | Schema sai → `LLMSchemaError` → retry ≤ 2 → fail rõ; lỗi ngữ nghĩa (thiếu PM/QA, vòng, lá > 10) → retry ≤ 2 → cảnh báo, không persist sai (`b5_wbs.py:80-98`) |
| 3 — One LLM gateway | ✅ | `wbs_engine`/`check_engine`/`schedule_engine`/`schedule_service`/`wbs_service` không import gateway; test assert `mock.call_count` không tăng khi sửa WBS/lịch (`test_wbs_edit_recalc.py:51`, `test_schedule_update.py:27`) |
| 4 — Ask instead of guess | ✅ | Thiếu headcount cho role trong WBS → 400 `missing_roles` (`schedule_service.py:96-102`); pipeline chặn khi còn câu hỏi làm rõ |
| 5 — Price gate | ✅ | `recalculated.quotation` luôn `None` (`api_schemas/wbs.py:86`); không có số tiền nào ở M4 |
| 6 — Privacy | ✅ | Prompt B5 nhận context đã mask PII; dữ liệu mẫu hư cấu |
| 7 — Languages | ✅ | Message lỗi tiếng Việt; nhãn UI tiếng Việt; `customer_language` chỉ ảnh hưởng lịch nghỉ mặc định, không đổi số |
| 8 — Done means proven | ✅ | 16/16 test case PASS trên Preview (mock LLM); 141 test backend + 6 vitest + build exit 0 |
| 9 — Keep it simple | ✅ | Gantt bằng CSS/div (`GanttChart.tsx`), không thư viện chart; không queue/vector DB/auth server |
| 10 — Frontend networking | ✅ | `API_BASE='/api'` (`client.ts:29`); 0 hit localhost/http trong `frontend/src` |

## Contract conformance

- ✅ `GET/PUT /wbs`, `POST /wbs/snapshot`, `GET/PUT /schedule` khớp §8.1/§8.2/§8.3/§8.4/§8.4a (fields, errors, `missing_roles`, `recalculated`).
- ✅ Guard `locked → 409` trên mọi mutation M4 (`lock_service.ensure_unlocked` — M3-REV-002).
- ✅ Danh tính authoritative từ header `X-Role`/`X-User`, không tin `by` body (M3-REV-001) — `deps.py:37-44`, changelog ghi actor từ header.
- ✅ `rerun from_step="wbs"` tự snapshot WBS cũ, giữ `evaluate`/`solution`, reset `wbs` + downstream (`runner.py:114-170`).
- ✅ Depth ≤ 3, lá ≤ 10 md, phụ thuộc không vòng, mỗi phase có PM+QA — kiểm tra cả ở schema (`wbs_structure.py`) lẫn service (`wbs_service._validate_structure`).
- ✅ Override ngoài ±20% / thiếu PM-QA bắt buộc `note` (BR-12) → 400 (`wbs_service.py:398-406`).

## Findings

### MEDIUM

**M4-REV-001 — `PUT /wbs` op `update` nhận `fields` không kiểu → 500 thay vì 400**
- Vị trí: `backend/app/schemas/api_schemas/wbs.py:75` (`fields: dict[str, Any]`), áp dụng bằng `setattr` tại `backend/app/services/wbs_service.py:326-327`.
- Vấn đề: giá trị `fields` không được validate kiểu. Ví dụ:
  - `{"man_day": "abc"}` → `"abc" < 0` (`wbs_service.py:313`) hoặc `"abc" > 10` (`:201`) → `TypeError` → 500.
  - `{"phase": "bogus"}` → vượt qua validation, `session.commit()` vi phạm `ck_wbs_items_phase` → `IntegrityError` → 500.
  - `{"sort_order": "x"}` → `int("x")` trong `enrich_items` → `ValueError` → 500.
- Không có test nào phủ ca malformed (`test_wbs_edit_recalc.py` chỉ dùng giá trị hợp lệ).
- Fix đề xuất: tạo schema có kiểu `WbsUpdateFields` (mirror `WbsTaskIn`: `phase: Literal[...]`, `role: Literal[...] | None`, `man_day: float | None` (ge=0, le=10), `depends_on: list[str]`, `sort_order: int`) và validate trước khi `setattr`; hoặc validate kiểu trong `_apply_update` và trả `validation_error` (400).

**M4-REV-002 — `depends_on` trên task nhóm (non-leaf) được chấp nhận nhưng bị bỏ qua khi tính lịch**
- Vị trí: `backend/app/services/schedule_engine.py:114` (`leaves = [i for i in items if i["is_leaf"]...]`) + `topo_order` (`:63-95`, chỉ đưa lá vào `indegree`).
- Vấn đề: schema và `_validate_structure` cho phép `depends_on` trên mọi task (kể cả nhóm); UI `WbsRowEditor` cũng cho chọn mọi task làm phụ thuộc. Nhưng scheduler chỉ xếp thứ tự **lá**, nên task lá phụ thuộc một nhóm sẽ bị bỏ dependency → lịch có thể bắt đầu trước khi nhóm đó xong (vi phạm phụ thuộc đã khai). `check_engine.cycle_free` có phát hiện vòng qua nhóm, nhưng thứ tự lịch thì không phản ánh.
- Fix đề xuất (chọn 1): (a) chặn `depends_on` trên non-leaf ở `_validate_structure` + schema + UI (đơn giản, đúng MVP); hoặc (b) đưa end của nhóm (= max end của con, tính đệ quy) vào `end_map` để task phụ thuộc nhóm chờ đúng.

### LOW

**M4-REV-003 — `recalc_schedule` giữ lịch cũ (stale) khi thiếu headcount cho role mới**
- Vị trí: `backend/app/services/wbs_service.py:434-438`.
- Vấn đề: thêm task với role chưa có trong `team_allocation` → `recalculated.schedule = None` nhưng lịch cũ trong DB vẫn còn → `GET /schedule` trả dữ liệu tính trên WBS cũ (không khớp WBS hiện tại) cho tới khi người dùng tự `PUT /schedule`.
- Fix đề xuất: gọi `delete_schedule` thay vì trả `None` (lịch cũ không còn đúng), hoặc giữ lịch cũ kèm `warning` rõ.

**M4-REV-004 — `holidays_applied` bỏ sót ngày nghỉ ở đầu dải**
- Vị trí: `backend/app/services/schedule_engine.py:126` (`cursor = to_working_day(start_date, ...)` không ghi nhận ngày nghỉ bị skip).
- Vấn đề: nếu `start_date` rơi vào ngày nghỉ, ngày đó không xuất hiện trong `holidays_applied` (cosmetic — Gantt vẫn đúng vì `tasks[].start_date` đã nhảy qua).
- Fix đề xuất: ghi nhận ngày nghỉ bị skip khi `to_working_day` đầu tiên.

**M4-REV-005 — Danh tính giả lập mặc định `presales` khi thiếu header**
- Vị trí: `backend/app/api/deps.py:42`.
- Vấn đề: caller không gửi `X-Role`/`X-User` vẫn có quyền sửa WBS/lịch/snapshot/rerun. Đúng thiết kế demo hiện tại (không auth server — AGENTS.md rule 9, contract §1.5), chỉ ghi nhận để M5 (duyệt giá) cân nhắc siết quyền.

### INFO

- `_is_descendant` O(n²) (`wbs_service.py:171-181`) — với ≤ 100 task không đáng kể.
- `_apply_update` đổi cha kiểm tra vòng cây bằng `_is_descendant` + `_depth_of` — đúng, chỉ là hiệu năng nhỏ.

## Điểm tốt

- Tách bạch LLM/code rất sạch: engines không import gateway; retry ngữ nghĩa có feedback prompt; cảnh báo không chặn pipeline.
- Diff snapshot tính ở mức item (gồm `parent_code`, `depends_on`, `man_day`) — đúng §8.3.
- FE chỉ render dữ liệu backend, không tự tính tổng/lịch; Gantt vẽ đúng `tasks[]`.
- Test API-level đầy đủ (141 test), phủ các kịch bản xấu (vòng, thiếu PM/QA, locked, missing_roles, BR-01).

## Verdict

**PASS** — không có finding CRITICAL/HIGH. 2 finding MEDIUM (M4-REV-001, M4-REV-002) và 3 LOW (M4-REV-003..005) nên được xử lý ở milestone sau hoặc trong một lượt sửa nhỏ; không chặn merge M4 vì toàn bộ acceptance criteria exit 0 và 16/16 test case PASS.

## Phụ lục — đánh giá trực tiếp trên Preview

Đã chạy Preview với hồ sơ mẫu CRM giả lập `#76`, `LLM_PROVIDER=mock`:

- Pipeline dừng đúng để hỏi làm rõ; sau khi trả lời đủ 2 vòng, các bước `intake`, `gap`, `solution`, `wbs` hoàn tất và hồ sơ chuyển `waiting_tech_approval`.
- WBS hiển thị 27 item, 3 cấp, tổng 57.6 man-day; đủ PM/QA theo phase, không vòng, task lá lớn nhất 6.0.
- Master schedule trả 18 task bars, áp dụng ngày nghỉ Nhật `2026-11-03`, có mốc thanh toán và cảnh báo deadline. Với start `2026-11-02`, buffer 5, Backend=2, lịch kết thúc `2027-02-01`, vượt hạn nộp `2026-12-15`; cảnh báo hiển thị rõ trên UI.
- `/api/bids/76/quotation`, `/api/bids/76/proposal`, `/api/bids/76/requirements` không tồn tại (404). Đây là kết quả phù hợp scope M4: quotation thuộc M5, proposal/M7 và requirement matrix thuộc milestone sau; không coi là lỗi M4.
- UI hiển thị hướng RAG và effort backend; không thấy giá hoặc proposal customer-facing được phát hành trước price approval.
- Một request trả lời clarification sai `round=1` khi backend đang chờ vòng 2 trả `400 VALIDATION_ERROR` tiếng Việt, không làm hỏng trạng thái; gửi đúng vòng 2 tiếp tục thành công.

Chi tiết đánh giá sản phẩm và bằng chứng Preview: `docs/reviews/M4-preview-evaluation.md`.

**Task Review complete. Awaiting prompt for the next role.**
