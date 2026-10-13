# Test Report — M4 WBS 3 cấp + master schedule

| Thuộc tính | Giá trị |
|---|---|
| Slice | M4 |
| Tester | QA acceptance |
| Ngày | 2026-10-10 |
| Nguồn | `AGENTS.md`, `docs/slices/M4/spec.md` §5.1–§5.3, `docs/slices/M4/handoff_to_test.md`, `docs/test-cases/M4-acceptance-testcases.md` |
| Môi trường | Preview podman-compose (origin `http://localhost:5173`, proxy `/api` → backend :8000), `LLM_PROVIDER=mock` |
| Template | IPA mặc định theo template M2/M3 trong repo; output Markdown |

## Acceptance commands (spec §5.1)

| Command | Exit | Ghi nhận |
|---|---:|---|
| `cd backend && pytest -q tests/test_wbs.py` | 0 | 8 test — gán man-day, tổng phase, cân bằng làm tròn, lá ≤ 10, depth ≤ 3 |
| `cd backend && pytest -q tests/test_wbs_pm_qa.py` | 0 | 6 test — thiếu PM/QA → retry → cảnh báo; đủ → pass |
| `cd backend && pytest -q tests/test_schedule.py` | 0 | 7 test — lịch theo WBS × headcount, phase tuần tự, buffer, mốc thanh toán |
| `cd backend && pytest -q tests/test_schedule_holidays.py` | 0 | 6 test — nghỉ lễ Nhật (2026-11-03, 2026-11-23) trừ đúng ngày LV |
| `cd backend && pytest -q tests/test_deadline_warning.py` | 0 | 4 test — end > deadline → violation + warning; tăng người → hết |
| `cd backend && pytest -q tests/test_wbs_snapshot.py` | 0 | 5 test — snapshot + diff_summary |
| `cd backend && pytest -q tests/test_wbs_cycles.py` | 0 | vòng phụ thuộc (DFS), tự tham chiếu, mã lạ |
| `cd backend && pytest -q tests/test_wbs_edit_recalc.py` | 0 | thêm 5 md → tổng +5, lịch đổi, `mock.call_count` không tăng (BR-03); override thiếu note → 400 |
| `cd backend && pytest -q tests/test_schedule_update.py` | 0 | headcount 2→1 → duration/end đổi, không gọi AI; missing_roles → 400; locked → 409 |
| `cd backend && pytest -q tests/test_wbs_lock.py` | 0 | PUT /wbs, PUT /schedule, POST snapshot trên locked → 409 |
| `cd backend && LLM_PROVIDER=mock pytest -q tests/test_llm_schema_no_numbers.py` | 0 | 9 test — `WbsStructure` cấm field số/ngày (BR-01); fixture `with_man_day` bị chặn |
| `cd backend && pytest -q` | 0 | **141 test collected, 0 failures** (dùng `python3 -m pytest tests` — wrapper `pytest` nén output sai) |
| `cd frontend && npm run build` | 0 | `tsc -b` + Vite production build pass |
| `make test` | 0 | Backend pass + frontend vitest 6 passed + build pass |
| `make quality-gate` | 0 | Test + build + grep guards BR-06/BR-10 pass |

## Test cases (Preview, mock LLM)

| TC-ID | Function / Screen | Viewpoint | Preconditions | Procedure | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|---|---|---|
| TC-M4-001 | Xem WBS (`/bids/74/wbs`) | Normal | Pipeline `wbs=completed` | Mở trang WBS, đếm hàng, đọc tổng | 3 cấp (1/2/3), lá ≤ 10, tổng do backend trả | 27 hàng; levels 1,2,3; tổng 57.6; lá lớn nhất 6.0 | PASS | Playwright + `GET /wbs` |
| TC-M4-002 | Check engine (`check` flags) | Normal | Như TC-M4-001 | Đọc vùng kiểm tra | 4 cờ đúng + midpoint/độ lệch | Hiển thị ✓ ±20%, ✓ PM+QA, ✓ không vòng, ✓ lá ≤ 10; Midpoint 57.6, Độ lệch 0% | PASS | Playwright |
| TC-M4-003 | Master schedule + Gantt (`/bids/74/schedule`) | Normal | Có WBS + lịch | Mở trang schedule | Gantt thanh task, mốc thanh toán, by_role | Gantt 18 thanh; 4 mốc (Kickoff…Bàn giao); bảng by_role | PASS | Playwright |
| TC-M4-004 | PUT /schedule recalc | Normal | Lịch có Backend=2 | Giảm Backend 2→1, lưu | duration tăng, end dịch sau, không gọi AI | Backend duration 6 → 12 ngày LV; `test_schedule_update.py` assert call_count không đổi | PASS | Playwright + test tự động |
| TC-M4-005 | Deadline warning | Boundary | Lịch vượt hạn nộp | Đọc cảnh báo; tăng người + sớm ngày → lưu | Warning hiển thị khi vi phạm; hết khi khắc phục | Warning "hạn nộp" hiển thị; sau boost (5 người/role, start 2026-10-01) → hết cảnh báo | PASS | Playwright |
| TC-M4-006 | PUT /wbs add (UI) | Normal | WBS completed | Thêm lá QA 5 md qua form | Tổng +5, lịch cập nhật | 57.6 → 62.6 (+5), hàng WBS-UI-01 hiển thị | PASS | Playwright |
| TC-M4-007 | PUT /wbs boundary | Boundary | WBS completed | Sửa lá man_day 10.0 / 10.1 | 10.0 chấp nhận; 10.1 → 400 | 10.0 → 200 (tổng 65.2); 10.1 → 400 `VALIDATION_ERROR` "không được vượt quá 10" | PASS | API |
| TC-M4-008 | PUT /wbs remove (sub-tree) | Normal | Hồ sơ mới có WBS | Xóa nhóm cấp 1 | Sub-tree biến mất, tổng giảm đúng, dọn depends_on | Xóa WBS-001 (9 item, lá sum 12.0) → tổng 57.6→45.6; không còn item con; không còn tham chiếu depends_on | PASS | API (bid 75) |
| TC-M4-009 | PUT /wbs cycle | Abnormal | WBS completed | A depends B, B depends A | 400 tiếng Việt, không persist | 400 `VALIDATION_ERROR` "Phụ thuộc task có vòng lặp" | PASS | API |
| TC-M4-010 | BR-12 override note | Abnormal | WBS completed | Thêm 3×5 md (lệch 26%) không note / có note | Thiếu note → 400; có note → 200 | Không note → 400 "cần ghi chú override"; có note → 200, deviation 26.0% | PASS | API |
| TC-M4-011 | Snapshot + rerun | Semi-normal | WBS completed; evaluate/solution đã chạy | Chụp snapshot (lý do) → sửa WBS → chụp lại → "Chạy lại từ WBS" | Snapshot 201; diff thêm/sửa/xóa; wbs chạy lại; evaluate/solution KHÔNG chạy lại | Snapshot UI tạo id=2 (lý do từ textarea); snapshot id=3 diff `added=1`; UI hiển thị "ĐÃ THÊM (1)"; rerun: wbs attempts 1→2, evaluate attempts 0, solution attempts 1 (không đổi); auto-snapshot id=4; WBS tái sinh 27 item | PASS | Playwright + DB |
| TC-M4-012 | Lock guard | Abnormal | `locked=true` (set qua DB) | PUT /wbs, PUT /schedule, POST snapshot | Cả 3 → 409 | Cả 3 → 409 `STATE_CONFLICT` | PASS | API (bid 75) |
| TC-M4-013 | Audit identity (X-User) | Normal | Hồ sơ unlocked | PUT /wbs header `X-User: tester-m4`, body `by: x` | Changelog actor từ header | Changelog `edit_wbs` actor=`tester-m4` (không phải `x`) | PASS | API + DB |
| TC-M4-014 | BR-01 schema | Security | — | Chạy `test_llm_schema_no_numbers.py` | Exit 0; fixture `with_man_day` bị chặn | Exit 0 (9 test) | PASS | pytest |
| TC-M4-015 | BR-10 networking | Security | Frontend build | Grep `localhost`/`127.0.0.1`/`http://` trong `frontend/src` | 0 hit; mọi request dùng `/api` | 0 hit; `API_BASE='/api'` (client.ts:29) | PASS | grep |
| TC-M4-016 | BR-04 missing_roles | Abnormal | WBS có role `infra` | PUT /schedule thiếu `infra` | 400 + `details.missing_roles` | 400 `VALIDATION_ERROR`, `missing_roles=["infra"]`, message tiếng Việt | PASS | API |

**Tổng: 16/16 PASS · 0 FAIL · 0 BLOCKED**

## Failures

Không có failure nào trong lần chạy này.

## Ghi chú / điểm cần lưu ý (không phải failure)

1. **`evaluate` (B3) không nằm trong M4**: trạng thái luôn `pending` (note "chưa triển khai ở M4"). TC-M4-011 xác nhận rerun **không chạy lại** evaluate (attempts=0) và solution (attempts=1) — đúng yêu cầu spec §2.6 "giữ evaluate + solution".
2. **Diff snapshot**: snapshot đầu tiên → `diff_summary: null`; snapshot sau không có thay đổi → diff rỗng `{added:[],removed:[],modified:[]}` (UI hiển thị "ĐÃ THÊM (0)" thay vì "Không có thay đổi" — khác biệt nhỏ về hiển thị, không phải lỗi logic).
3. **Rerun tự snapshot WBS cũ** (auto-snapshot) trước khi tái sinh — đúng spec §2.6; diff của auto-snapshot so với snapshot trước đó.
4. **Wrapper `pytest` bị nén output** ("No tests collected" sai): dùng `python3 -m pytest tests` — kết quả thật 141 collected, 0 failures.
5. **Lưu ý TC-M4-008**: tổng giảm = man-day của lá trong sub-tree (12.0), không phải tổng mọi item (cha đã bao gồm con) — hành vi đúng.
6. **Số giả lập**: `holidays.yaml`/`payment.yaml` version 1 chờ BA/PM phê duyệt (BR-06) — ảnh hưởng dữ liệu, không ảnh hưởng kết quả test.

## Suspected files (nếu có failure)

Không có.