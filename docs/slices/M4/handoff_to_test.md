# Handoff — Build → Test (M4 WBS 3 cấp + master schedule)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Parallel Dispatch Coordinator (Build M4) |
| Cho | Test/Review |
| Ngày | 2026-10-10 |
| Slice | M4 |
| Nguồn | `docs/slices/M4/spec.md`, `docs/slices/M4/handoff_to_build.md`, báo cáo 2 subagent (backend-dev, frontend-dev), kết quả reconcile + E2E |

## Cách chạy (một lệnh)

```bash
make preview        # Preview qua podman-compose (LLM_PROVIDER=mock, không gọi LLM thật)
make test           # Toàn bộ test: backend pytest + frontend vitest + build
make quality-gate   # CI-style: test + build + grep guards BR-06/BR-10
```

Luồng thử thủ công: **Tạo hồ sơ** (hoặc "Nạp mẫu tiếng Nhật/tiếng Việt") → trả lời câu hỏi làm rõ (tối đa 2 vòng) → **Rà soát hướng giải pháp** → **WBS & lịch trình** (bảng WBS 3 cấp sửa được + Gantt + mốc thanh toán).

## Đã xây dựng

### Backend (141 test pass, 0 failures — `python3 -m pytest tests`, exit 0)
- `reference/holidays.yaml` (nghỉ lễ VN+Nhật 2026, version 1, nhãn "DỮ LIỆU GIẢ LẬP"), `reference/payment.yaml` (4 mốc mặc định, tổng 100%) — **chờ BA/PM phê duyệt**.
- Schema LLM `WbsStructure` (3 cấp, `extra="forbid"`, KHÔNG có man-day/effort/ngày — BR-01; role+weight bắt buộc trên lá; depth ≤ 3).
- Schema API `wbs.py`/`schedule.py` đúng contract §8.1/8.2/8.3/8.4/8.4a.
- Model `wbs_items` (parent_code, depends_on, role/weight/man_day lá-only), `wbs_snapshots`, `schedules` (+ by_role/tasks_json/holidays_applied), `changelog`.
- `WbsEngine` (gán man-day lá từ midpoint phase × trọng số chuẩn hóa, ≤ 10, round 1dp, cân bằng làm tròn; nhóm = Σ con), `CheckEngine` (±20%, PM/QA mỗi phase, DFS vòng, lá ≤ 10), `ScheduleEngine` (phase tuần tự, topo depends_on, duration = ceil(man_day ÷ headcount) ngày làm việc trừ T7/CN + nghỉ lễ, buffer, mốc thanh toán due_date, deadline_violation).
- `WbsService` (CRUD + sub-tree + dọn depends_on; override ±20% bắt buộc note → 400; locked → 409; changelog; tính lại lịch không gọi AI), `ScheduleService` (missing_roles → 400 kèm details; mặc định payment.yaml), `LockService`.
- B5 `run_wbs`: prompt Việt cấm số/ngày → gateway → validate → gán man-day → check ngữ nghĩa retry ≤ 2 → cảnh báo → persist. Orchestrator kích hoạt `solution` + `wbs`; `runner.resume(from_step="wbs")` tự snapshot WBS cũ, giữ evaluate/solution.
- Router `wbs.py` + `schedule.py`; danh tính audit từ header `X-Role`/`X-User` (M3-REV-001).
- Mock fixtures `WbsStructure`: good/rag_3level, good/flat_ok, missing_pm, missing_qa, cycle, leaf_too_heavy, bad_schema, with_man_day.

### Frontend (6 vitest pass, `npm run build` pass)
- `WbsPage` (bảng 3 cấp sửa được + Thêm/Sửa/Xóa + snapshot + "Chạy lại từ WBS" + diff + tóm tắt lịch sau sửa), `SchedulePage` (form tham số + Gantt + mốc thanh toán + cảnh báo hạn nộp + missing_roles).
- Components: `WbsTreeTable`, `WbsRowEditor` (role chỉ khi lá, man-day ≤ 10, cha ≤ depth 2, note bắt buộc BR-12), `CheckWarnings`, `GanttChart` (CSS/div, không thư viện nặng — BR-09), `ScheduleForm`, `PaymentMilestonesView`.
- `api/client.ts` + `types.ts` mở rộng (getWbs/updateWbs/snapshotWbs/getSchedule/updateSchedule/rerunPipelineFromWbs) — base root-relative `/api` (BR-10), error envelope tiếng Việt.
- Routes `/bids/:id/wbs`, `/bids/:id/schedule`; nút điều hướng từ BidDetailPage; UI tiếng Việt.

## Reconcile backend ↔ frontend (kết quả)

- **Path/method khớp 100%**: GET/PUT `/api/bids/{id}/wbs`, POST `/api/bids/{id}/wbs/snapshot`, GET/PUT `/api/bids/{id}/schedule`, POST `/api/bids/{id}/rerun` (from_step='wbs') — đối chiếu trực tiếp `client.ts` ↔ `routers/wbs.py` + `routers/schedule.py`.
- **Field name khớp**: `WbsItem` (task_code/name_vi/phase/parent_code/level/role/weight/man_day/depends_on/sort_order/is_leaf), `check` (midpoint/deviation_pct/within_20pct/pm_qa_ok/cycle_free/leaf_max_man_day/leaf_within_limit/warning), `ScheduleResponse` (start_date/buffer_days/working_calendar/team_allocation/payment_milestones/by_role/tasks/holidays_applied/end_date/deadline_violation/warning/trace) — đối chiếu `types.ts` ↔ schema Pydantic.
- **Error shape khớp**: envelope `{error:{code,message,details}}`; FE hiển thị `message` tiếng Việt; `details.missing_roles` được ScheduleForm hiển thị.
- **Không có mismatch** cần sửa; không cần dispatch follow-up.

## E2E đã chạy (Preview, mock LLM, qua proxy :5173)

1. `GET /api/health` → `{"llm_provider":"mock","database":"ok"}` ✓
2. `POST /api/bids/sample` → bid 74 (CRM Nhật, giả lập) ✓
3. Pipeline: intake → gap (2 vòng hỏi làm rõ — BR-04) → **solution=completed, wbs=completed** ✓
4. `GET /wbs`: 27 items, 3 cấp (levels 1/2/3), totals 57.6 = midpoint (deviation 0%), `pm_qa_ok=true`, `cycle_free=true`, `leaf_within_limit=true` (lá max 6.0 md), mọi phase có PM+QA ✓
5. `PUT /schedule` thiếu role `infra` → **400 VALIDATION_ERROR** `details.missing_roles=["infra"]` (message tiếng Việt) ✓
6. `PUT /schedule` đủ role → 200: end_date 2027-02-01, `deadline_violation=true` + warning tiếng Việt, `holidays_applied=["2026-11-03"]` (Ngày Văn hóa Nhật), 18 tasks có start/end (Gantt), 4 mốc thanh toán có due_date ✓
7. `PUT /wbs` thêm task QA 5 md → totals 57.6 → 62.6 (+5), `recalculated.schedule` có end_date mới, `recalculated.quotation=null` (M5) ✓; xóa → về 57.6 ✓
8. Browser (Playwright headless): SPA tải, trang `/bids/74/wbs` render bảng WBS 3 cấp với dữ liệu backend thật; bundle dùng `/api`, **0** hit localhost (BR-10) ✓ (2 lỗi console là cert Google Fonts của headless chromium, không phải lỗi app)

## Known gaps / điểm cần lưu ý

1. **Số giả lập chờ phê duyệt**: `holidays.yaml`/`payment.yaml` version 1 (nghỉ lễ VN/Nhật 2026, mốc thanh toán mặc định) — cần BA/PM xác nhận trước khi dùng cho hồ sơ thật (BR-06).
2. **Test M2/M3 cũ được cập nhật đúng spec M4** (kích hoạt solution+wbs): `test_pipeline_resume.py`, `test_pipeline_sse.py` — không phải regression.
3. **`evaluate` (B3) chưa triển khai** — nằm ngoài phạm vi M4 (output_json ghi "chưa triển khai ở M4"); `proposal`/`ja_check` cũng pending (M6/M7).
4. **`recalculated.schedule` = null khi chưa gọi PUT /schedule**; `recalculated.quotation` luôn null (M5).
5. **Mô hình lịch tuần tự (MVP)**: phase nối tiếp, task tuần tự theo topo — chưa tận dụng song song thực tế (ADR-006, chấp nhận cho MVP).
6. **Diff snapshot** tính so với snapshot trước (snapshot đầu → `diff_summary: null`).
7. **Flake timing**: một lần chạy suite chậm do máy chia sẻ với agent song song — đã tăng `wait_until` timeout mặc định lên 10s; 3 lần chạy liên tiếp đều pass.
8. **B5 semantic retry**: fixture xấu (missing_pm/cycle/leaf_too_heavy) → 3 lần gọi LLM → cảnh báo, không chặn; bad_schema → 3 lần → bước failed rõ.
9. **Lưu ý chạy pytest**: dùng `python3 -m pytest tests` (wrapper `pytest` có thể bị nén output sai "No tests collected" — kết quả thật: 141 passed, exit 0).

## Gợi ý kịch bản Test/Review (Preview)

1. Chạy pipeline → bước WBS completed → mở WBS: 3 cấp, đủ PM/QA mỗi phase, lá ≤ 10, tổng ±20% (hoặc cảnh báo rõ).
2. Master schedule: điền tham số → Gantt; giảm headcount 2→1 → lịch dài hơn, không gọi AI (log/mock call count).
3. Sửa WBS: thêm 5 md → tổng +5, lịch cập nhật; xóa nhóm → sub-tree biến mất; tạo vòng phụ thuộc → 400 tiếng Việt; vượt hạn nộp → cảnh báo.
4. Snapshot → "Chạy lại từ WBS" → WBS mới, giữ evaluate/solution; xem diff trước/sau.
5. Hồ sơ `locked=true` (set qua DB) → PUT /wbs, PUT /schedule, POST snapshot → 409 STATE_CONFLICT.

**Task Build M4 complete. Awaiting prompt for the next role.**