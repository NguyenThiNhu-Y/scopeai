# Handoff — Solution Architect → Build (M4 WBS 3 cấp + master schedule)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Solution Architect |
| Cho | Backend Dev, Frontend Dev (bước tiếp theo) |
| Ngày | 2026-10-10 |
| Nguồn | `docs/slices/M4/spec.md`, `docs/04_architecture/` (4 file — đã cập nhật ADR-006), `docs/05_roadmap/roadmap.md` §6, `docs/slices/M3/review.md`, `docs/slices/M3/test_report.md`, `AGENTS.md` |

## 1. Deliverables bắt buộc

1. Tạo `reference/holidays.yaml` (nghỉ lễ VN/Nhật 2026) và `reference/payment.yaml` (mốc thanh toán mặc định) — số **giả lập do BA/PM phê duyệt**, có version.
2. Tạo schema `WbsStructure` (B5) + fixture mock; schema **không có** man-day/effort/ngày (BR-01); `extra="forbid"`.
3. Tạo `WbsEngine` (gán man-day lá ≤ 10 từ midpoint bảng chuẩn theo phase), `CheckEngine` (±20%, PM/QA mỗi phase, không vòng, lá ≤ 10), `ScheduleEngine` (WBS × headcount + nghỉ lễ + buffer + mốc thanh toán + cảnh báo hạn nộp) — thuần code, deterministic, unit-test được.
4. Tạo model `wbs_items` (3 cấp: `parent_code`, `depends_on`, role/weight/man_day lá-only), `wbs_snapshots`, `schedules` (+ `by_role`, `tasks_json`, `holidays_applied`).
5. Tạo service/router: `GET/PUT /api/bids/{id}/wbs`, `POST /api/bids/{id}/wbs/snapshot`, `GET/PUT /api/bids/{id}/schedule` — đúng contract §8.1/8.2/8.3/8.4/8.4a.
6. Kích hoạt B4 (`solution`) + B5 (`wbs`) trong `orchestrator.run()`; `runner.resume(from_step="wbs")` tự snapshot WBS cũ, giữ `evaluate`/`solution`.
7. Tạo UI: bảng WBS 3 cấp sửa được (thêm/sửa/xóa) + Gantt + form tham số lịch; sửa xong tổng + lịch tự tính lại, **không gọi AI**.
8. Chạy toàn bộ acceptance commands trong `spec.md` §5, kiểm tra Preview và ghi test evidence.

## 2. Luật không được vi phạm

- **Điều kiện tiên quyết:** M3 phải được fix + approve trước (M3-REV-001..005). Không build M4 trên nền M3 chưa vững.
- Không để LLM sinh/sửa man-day, giá, ngày. B5 chỉ trả cấu trúc + trọng số; **code gán man-day lá** (≤ 10).
- Không gọi LLM trong `WbsEngine`, `CheckEngine`, `ScheduleEngine`, `PUT /wbs`, `PUT /schedule` — test assert `mock.call_count` không tăng.
- Mọi output LLM qua `LLMClient.complete_with_retry`, retry ≤ 2, test/CI dùng `LLM_PROVIDER=mock`.
- Danh tính audit lấy từ header `X-Role`/`X-User` (không tin `by` từ body — M3-REV-001); mọi mutation chặn `locked` → `409` (M3-REV-002).
- Override ±20% bắt buộc `note` (BR-12); thiếu → 400.
- Không tính lại số ở frontend; không hardcode `http://localhost` trong `frontend/src`.
- Không triển khai approval/quotation/export (M5/M7); `recalculated.quotation` bỏ trống.
- Tạo **đúng tên file test** trong acceptance commands (bài học GAP-M3-001: không gộp test vào file khác).

## 3. Contract cần khóa trong implementation

- WBS **3 cấp**: `parent_code` (depth ≤ 3), `depends_on` (không vòng), `role`/`weight`/`man_day` chỉ trên **task lá**, lá `man_day ≤ 10`; nhóm/task cha man_day = Σ con.
- `GET /wbs` trả `items` (kèm `level`, `is_leaf`), `totals`, `check` (`within_20pct`, `pm_qa_ok`, `cycle_free`, `leaf_within_limit`, `warning`), `trace`.
- `PUT /wbs` nhận `changes` (add/update/remove), trả WBS mới + `recalculated.schedule`; override ngoài ±20% bắt buộc `note`.
- `GET /schedule` trả `tasks[]` (Gantt), `by_role`, `holidays_applied`, `payment_milestones` (kèm `due_date`), `end_date`, `deadline_violation`, `warning`, `trace`.
- `PUT /schedule` nhận `start_date`, `buffer_days`, `working_calendar` (vn/jp/both), `team_allocation`, `payment_milestones` (tùy chọn) → tính lại ngay; role trong WBS thiếu headcount ≥ 1 → `400 VALIDATION_ERROR` + `details.missing_roles`.
- Error envelope chuẩn; message tiếng Việt; FE base root-relative `/api`.
- Mô hình lịch MVP: phase tuần tự `poc → mvp → production`; task tuần tự theo thứ tự topo `depends_on`; duration = `ceil(man_day ÷ headcount[role])` ngày làm việc (trừ T7/CN + nghỉ lễ); buffer ở cuối.

## 4. Test gate

```bash
cd backend && pytest -q tests/test_wbs.py
cd backend && pytest -q tests/test_wbs_pm_qa.py
cd backend && pytest -q tests/test_schedule.py
cd backend && pytest -q tests/test_schedule_holidays.py
cd backend && pytest -q tests/test_deadline_warning.py
cd backend && pytest -q tests/test_wbs_snapshot.py
cd backend && pytest -q tests/test_wbs_cycles.py
cd backend && pytest -q tests/test_wbs_edit_recalc.py
cd backend && pytest -q tests/test_schedule_update.py
cd backend && pytest -q tests/test_wbs_lock.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_llm_schema_no_numbers.py
make test
cd backend && pytest -q
cd frontend && npm run build
make quality-gate
```

Preview phải chứng minh: WBS 3 cấp đủ PM/QA mỗi phase, tổng ±20%, không vòng, lá ≤ 10; Gantt theo WBS × số người có mốc thanh toán; giảm headcount / thêm task → tổng + lịch tính lại không gọi AI; snapshot + rerun từ WBS giữ evaluate/solution; vượt hạn nộp → cảnh báo; locked → 409.

## 5. Handoff tiếp theo

Sau khi build/test M4 hoàn tất, ghi test report và chuyển cho role Test/Review. Nêu rõ: version `holidays.yaml`/`payment.yaml` đã dùng và ai phê duyệt, kết quả các acceptance commands (đúng tên file), mọi blocker. Bàn giao cho M5: WBS 3 cấp + man-day lá là đầu vào rate card; `schedules.payment_milestones`/`team_allocation` là đầu vào báo giá; guard `locked` sẵn sàng cho duyệt giá. Không bắt đầu triển khai M5 trong bước này.

**Task Slice Spec M4 complete. Awaiting prompt for the next role.**