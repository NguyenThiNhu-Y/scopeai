# Test Cases — M4 WBS 3 cấp + master schedule (Acceptance)

| Thuộc tính | Giá trị |
|---|---|
| Milestone | M4 — WBS 3 cấp + master schedule (sửa được, code tính lại) |
| Chuẩn template | IPA (mặc định — theo template M2/M3 trong repo) |
| Định dạng | Markdown |
| Nguồn | `docs/slices/M4/spec.md` §5.2/§5.3, `docs/slices/M4/handoff_to_test.md`, `AGENTS.md` (BR-01..04, BR-07, BR-10, BR-12) |
| Môi trường | Preview podman-compose (origin :5173, proxy `/api` → backend :8000), `LLM_PROVIDER=mock` |
| Ngày | 2026-10-10 |

## Legend trường

| Field | Ý nghĩa |
|---|---|
| TC-ID | `TC-M4-NN` — định danh duy nhất |
| 機能名 / Function | Chức năng kiểm thử |
| 画面 / Screen | Màn hình / endpoint |
| 観点 / Viewpoint | 正常系 / 準正常系 / 異常系 / 境界値 / Security |
| テスト項目 / Test Item | Mô tả ngắn |
| 事前条件 / Precondition | Trạng thái trước khi thực hiện |
| テスト手順 / Procedure | Các bước thao tác cụ thể |
| 期待結果 / Expected Result | Kết quả mong đợi (kiểm chứng được) |
| 備考 / Notes | Ghi chú thêm |

---

## A. Hiển thị WBS 3 cấp (spec §5.2-1, FR-032/FR-041)

### TC-M4-001: WBS 3 cấp hiển thị đủ nhóm/task/sub-task theo phase

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-001 |
| **機能名** | Xem WBS (GET /wbs) |
| **画面** | `/bids/{id}/wbs` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Bảng WBS 3 cấp render từ backend |
| **事前条件** | Preview chạy (mock LLM); hồ sơ đã chạy pipeline tới bước `wbs=completed` |
| **テスト手順** | 1. Mở `/bids/{id}/wbs` 2. Quan sát bảng |
| **期待結果** | 1. Có đúng 3 cấp (level 1/2/3) hiển thị với indent 2. Mỗi phase `poc`/`mvp`/`production` có task 3. Task lá có cột role + man-day ≤ 10 4. Tổng man-day hiển thị do backend trả |
| **備考** | spec §2.1, §5.2-1 |

### TC-M4-002: Cờ kiểm tra WBS hiển thị (PM/QA, ±20%, vòng, lá ≤ 10)

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-002 |
| **機能名** | Check engine (GET /wbs → check) |
| **画面** | `/bids/{id}/wbs` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | CheckWarnings hiển thị 4 cờ |
| **事前条件** | Như TC-M4-001 |
| **テスト手順** | 1. Mở trang WBS 2. Đọc vùng cảnh báo/kiểm tra |
| **期待結果** | 1. `pm_qa_ok`, `within_20pct`, `cycle_free`, `leaf_within_limit` đều hiển thị đúng trạng thái 2. `warning` = null hoặc hiển thị message tiếng Việt 3. Deviation % hiển thị |
| **備考** | spec §2.1, BR-07 (message tiếng Việt) |

---

## B. Master schedule + Gantt (spec §5.2-2/3/6, FR-034)

### TC-M4-003: Form lịch → Gantt + mốc thanh toán

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-003 |
| **機能名** | Master schedule (GET/PUT /schedule) |
| **画面** | `/bids/{id}/schedule` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Điền tham số → Gantt + milestones |
| **事前条件** | Hồ sơ có WBS completed; chưa có lịch (hoặc đã có) |
| **テスト手順** | 1. Mở `/bids/{id}/schedule` 2. Điền ngày bắt đầu, số người mỗi role (đủ mọi role trong WBS), buffer, lịch nghỉ 3. Bấm "Tính lịch" |
| **期待結果** | 1. Gantt hiển thị thanh từng task theo `start_date`/`end_date` do backend trả 2. Có danh sách mốc thanh toán (tên/%/ngày đến hạn) 3. Có ngày kết thúc tổng |
| **備考** | spec §2.4/§2.5, §5.2-2 |

### TC-M4-004: Giảm headcount 2→1 → lịch dài hơn, không gọi AI

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-004 |
| **機能名** | PUT /schedule recalculation |
| **画面** | `/bids/{id}/schedule` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Đổi số người → duration/end đổi |
| **事前条件** | Đã có lịch với role `backend` headcount=2 |
| **テスト手順** | 1. Giảm `backend` 2 → 1 2. Lưu 3. Đọc lại lịch |
| **期待結果** | 1. `by_role.backend.duration_days` tăng (≈ x2) 2. `end_date` dịch về sau 3. Mock LLM call_count không tăng (không gọi AI) |
| **備考** | spec §5.2-3, BR-03 |

### TC-M4-005: Lịch vượt hạn nộp → cảnh báo; tăng người → hết cảnh báo

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-005 |
| **機能名** | Deadline warning |
| **画面** | `/bids/{id}/schedule` |
| **観点** | 境界値 (Boundary) |
| **テスト項目** | deadline_violation true/false theo tham số |
| **事前条件** | Hồ sơ có hạn nộp; WBS completed |
| **テスト手順** | 1. Đặt ít người + buffer lớn sao cho end_date > deadline → lưu 2. Quan sát cảnh báo 3. Tăng số người → lưu 4. Quan sát lại |
| **期待結果** | 1. Lần 1: `deadline_violation=true`, warning tiếng Việt hiển thị 2. Lần 2: end_date ≤ deadline, hết cảnh báo |
| **備考** | spec §5.2-6, §2.4 |

---

## C. Sửa WBS (spec §5.2-4/5, FR-041, UC-06)

### TC-M4-006: Thêm task lá 5 man-day → tổng +5, lịch cập nhật

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-006 |
| **機能名** | PUT /wbs add |
| **画面** | `/bids/{id}/wbs` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Thêm lá → tổng +5, recalculated.schedule |
| **事前条件** | WBS completed; tổng hiện tại T |
| **テスト手順** | 1. Bấm "Thêm task" 2. Điền mã mới, phase, role `qa`, man-day 5.0 3. Lưu |
| **期待結果** | 1. Tổng mới = T + 5 2. `recalculated.schedule` có end_date mới 3. Không gọi AI (call_count không đổi) |
| **備考** | spec §2.2, §5.2-4, BR-03 |

### TC-M4-007: Sửa man-day lá > 10 → chặn 400 tiếng Việt

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-007 |
| **機能名** | PUT /wbs validation |
| **画面** | `/bids/{id}/wbs` |
| **観点** | 境界値 (Boundary) |
| **テスト項目** | man_day = 10.0 chấp nhận; 10.1 bị chặn |
| **事前条件** | WBS completed |
| **テスト手順** | 1. Sửa lá: man_day = 10.0 → lưu (chấp nhận) 2. Sửa lá: man_day = 10.1 → lưu |
| **期待結果** | 1. 10.0 được chấp nhận (≤ 10) 2. 10.1 → 400 `VALIDATION_ERROR`, message tiếng Việt, không persist |
| **備考** | spec §2.1/§2.2, BR-07 |

### TC-M4-008: Xóa nhóm → sub-tree biến mất, tổng giảm đúng

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-008 |
| **機能名** | PUT /wbs remove |
| **画面** | `/bids/{id}/wbs` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Xóa nhóm cấp 1 → toàn bộ con biến mất |
| **事前条件** | WBS completed; chọn nhóm cấp 1 có sub-tree |
| **テスト手順** | 1. Xóa nhóm cấp 1 2. Lưu 3. Đọc lại WBS |
| **期待結果** | 1. Nhóm + toàn bộ sub-tree không còn trong items 2. Tổng giảm đúng tổng man-day của sub-tree 3. `depends_on` trỏ tới item đã xóa được dọn |
| **備考** | spec §2.2, §5.2-4 |

### TC-M4-009: Phụ thuộc vòng → 400 tiếng Việt

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-009 |
| **機能名** | PUT /wbs cycle detection |
| **画面** | `/bids/{id}/wbs` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | A depends B, B depends A → chặn |
| **事前条件** | WBS completed; 2 task lá A, B |
| **テスト手順** | 1. Sửa A: depends_on = [B] 2. Sửa B: depends_on = [A] 3. Lưu |
| **期待結果** | 1. 400 `VALIDATION_ERROR`, message tiếng Việt 2. Không persist trạng thái vòng |
| **備考** | spec §5.2-5, BR-07 |

### TC-M4-010: Override ngoài ±20% thiếu note → 400 (BR-12)

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-010 |
| **機能名** | BR-12 override note |
| **画面** | PUT /wbs |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Sửa tổng lệch > 20% không kèm note |
| **事前条件** | WBS completed; thêm lượng man-day khiến deviation > 20% |
| **テスト手順** | 1. Thêm task lá lớn (vd. 15 md) sao cho lệch > 20% 2. Không điền note 3. Lưu |
| **期待結果** | 1. 400 `VALIDATION_ERROR` yêu cầu note 2. Có note → chấp nhận |
| **備考** | spec §2.2, AGENTS.md BR-12 |

---

## D. Snapshot + rerun (spec §5.2-7, FR-041.2)

### TC-M4-011: Snapshot → rerun từ WBS → giữ evaluate/solution, diff hiển thị

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-011 |
| **機能名** | Snapshot + rerun (POST /wbs/snapshot, POST /rerun) |
| **画面** | `/bids/{id}/wbs` |
| **観点** | 準正常系 (Semi-normal) |
| **テスト項目** | Chụp snapshot, chạy lại từ WBS, xem diff |
| **事前条件** | WBS completed; evaluate/solution completed |
| **テスト手順** | 1. Bấm "Chụp snapshot" (kèm lý do) 2. Bấm "Chạy lại từ WBS" 3. Chờ pipeline chạy lại bước wbs 4. Kiểm tra trạng thái các bước + diff |
| **期待結果** | 1. Snapshot 201, `diff_summary` hợp lệ 2. `evaluate` + `solution` vẫn completed (KHÔNG chạy lại) 3. `wbs` chạy lại → completed 4. Diff thêm/sửa/xóa hiển thị |
| **備考** | spec §2.3/§2.6, §5.2-7 |

---

## E. Lock + audit (spec §5.2-8, M3-REV-001/002)

### TC-M4-012: Hồ sơ locked=true → 409 STATE_CONFLICT

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-012 |
| **機能名** | Lock guard |
| **画面** | PUT /wbs, PUT /schedule, POST /wbs/snapshot |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Mutation trên bid locked bị chặn |
| **事前条件** | Set `locked=true` cho hồ sơ qua DB |
| **テスト手順** | 1. PUT /wbs 2. PUT /schedule 3. POST /wbs/snapshot |
| **期待結果** | Cả 3 đều 409 `STATE_CONFLICT`, message tiếng Việt |
| **備考** | spec §2.2/§2.5, M3-REV-002 |

### TC-M4-013: Changelog ghi đúng người sửa từ header X-User

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-013 |
| **機能名** | Audit identity (X-Role/X-User) |
| **画面** | PUT /wbs, PUT /schedule |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Danh tính authoritative từ header |
| **事前条件** | Hồ sơ unlocked, WBS completed |
| **テスト手順** | 1. PUT /wbs với header `X-User: tester-m4` (body `by` khác) 2. Đọc changelog |
| **期待結果** | 1. Changelog ghi actor = `tester-m4` (từ header, không phải body `by`) 2. Action `edit_wbs` |
| **備考** | spec §2.6, M3-REV-001 |

---

## F. Rule AGENTS.md (spec §5.3)

### TC-M4-014: BR-01 — LLM không xuất số/ngày (schema chặn)

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-014 |
| **機能名** | BR-01 no invented numbers |
| **画面** | Schema `WbsStructure` / test |
| **観点** | Security / 異常系 |
| **テスト項目** | Fixture `with_man_day` bị chặn |
| **事前条件** | Backend test suite |
| **テスト手順** | 1. Chạy `test_llm_schema_no_numbers.py` |
| **期待結果** | 1. Exit 0 2. Fixture chứa `man_day` bị schema `extra="forbid"` chặn |
| **備考** | spec §3.2, AGENTS.md BR-01 |

### TC-M4-015: BR-10 — bundle không hardcode localhost

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-015 |
| **機能名** | BR-10 frontend networking |
| **画面** | Bundle JS |
| **観点** | Security |
| **テスト項目** | Không có host cứng trong frontend/src |
| **事前条件** | Frontend đã build |
| **テスト手順** | 1. Grep `localhost`/`127.0.0.1`/`http://` trong `frontend/src` 2. Kiểm tra bundle |
| **期待結果** | 1. Không có URL tuyệt đối; mọi request dùng `/api` |
| **備考** | AGENTS.md BR-10 |

### TC-M4-016: BR-04 — thiếu team_allocation cho role trong WBS → 400 missing_roles

| Field | Content |
|---|---|
| **TC-ID** | TC-M4-016 |
| **機能名** | BR-04 ask instead of guess |
| **画面** | PUT /schedule |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Không đoán số người; báo role thiếu |
| **事前条件** | WBS có role `infra`; team_allocation không có `infra` |
| **テスト手順** | 1. PUT /schedule thiếu `infra` |
| **期待結果** | 1. 400 `VALIDATION_ERROR` 2. `details.missing_roles = ["infra"]` 3. Message tiếng Việt |
| **備考** | spec §2.5, AGENTS.md BR-04 |