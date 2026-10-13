# Handoff — Fix: FE↔BE (backend-dev + frontend-dev song song)

Ngày: 2026-10-11
Bước: Fix (Parallel Dispatch Coordinator) — workflow rà soát & fix lỗi FE gọi BE
Nguồn: `docs/quality/fe_be_audit.md` (bước Analyze)

## Kết quả 2 nhánh (đã reconcile, không xung đột)

### Backend (backend-dev) — DONE ✅
Files đã sửa:
- `backend/app/services/proposal_service.py` — `_normalize_sections()` / `_normalize_translations()`: `to_out()` và `translate()` normalize sections khi đọc — điền đủ 8 key theo `SECTION_NAMES` (thiếu/empty → `[Đang chờ proposal]`), loại key thừa (`conclusion`). Fix ở lớp đọc, **không migrate DB** (BR-09).
- `backend/app/main.py:40` — `allow_headers` thêm `X-Role`, `X-User`.
- `backend/tests/test_proposal_legacy_normalize.py` — regression test mới (4 test).
- `docs/quality/handoff_backend_dev.md` — handoff chi tiết.

Bằng chứng:
- Backend pytest: **245 passed** (241 baseline + 4 regression) — subagent chạy; đang chạy lại toàn bộ để xác nhận độc lập.
- Probe runtime (đã xác nhận độc lập bởi coordinator): `GET /api/bids/110/proposal` → **HTTP 200**, đủ 8 mục: `approach, assumptions_and_scope, introduction, requirements_understanding, risks, schedule, solution_overview, team` (không còn `conclusion`). Spot-check bid 80/91/104/105/112 → 200, 8 mục.
- CORS preflight (`content-type,x-role,x-user,x-actor`) → 200, allow-headers gồm `X-Actor, X-Role, X-User`.

Ghi chú F-02: `X-Role` **không được backend đọc** (`deps.py` chỉ đọc `X-Actor`/`X-User`) — header giả lập vai trò phía FE (GATE-01). Frontend đã bỏ `X-Role` khỏi client.ts; backend vẫn cho phép header này trong allow_headers (vô hại).

### Frontend (frontend-dev) — DONE ✅
Files đã sửa:
- `frontend/src/pages/ProposalPage.tsx` — 3 chỗ đọc sections đều có fallback:
  - L51: `(sections[key] ?? '').split('{{QUOTATION}}')`
  - L59: `Object.values(sections).some(value => value?.includes('{{QUOTATION}}'))`
  - L141: textarea `value={sections[key] ?? ''}`
- `frontend/src/api/client.ts` — bỏ `X-Role` khỏi `updateSetting` (:172), `approveTech` (:424), `approvePrice` (:431), `unlockBid` (:438); giữ `X-User` (backend có đọc).
- `docs/quality/handoff_frontend_dev.md` — handoff chi tiết.

Bằng chứng (xác nhận độc lập bởi coordinator):
- `npm test` → **11 passed (11)**.
- `npm run build` → **PASS** (tsc -b && vite build).
- Không còn chỗ nào đọc `sections[key]` không có fallback (chỉ 3 site, đều đã guard).
- BR-10: không có localhost/absolute URL trong frontend/src; `API_BASE = '/api'`.

## Reconcile / xung đột
Không có xung đột giữa 2 nhánh. Hai thay đổi bổ trợ nhau: backend cho phép `X-Role`/`X-User` trong CORS + frontend không còn gửi `X-Role` (header backend không bao giờ đọc). Không cần edit chéo.

## Việc còn lại cho bước Verify
1. Chạy lại toàn bộ test (backend pytest qua `python3 -c "import sys,pytest; sys.exit(pytest.main(['-q']))"` từ `backend/`; frontend `npm test` + `npm run build`).
2. Probe runtime: `GET /api/bids/110/proposal` → 200 đủ 8 mục; mở tab Proposal trên Preview với hồ sơ cũ (bid 80–110) — không crash, hiển thị placeholder `[Đang chờ proposal]` cho mục thiếu.
3. Review code 2 nhánh (backend normalize + frontend guards) → APPROVED/NEEDS-CHANGES.
4. Ghi `docs/quality/fe_be_handoff.md` tổng hợp.

Lưu ý môi trường: wrapper `rtk` nuốt output pytest (`Pytest: No tests collected`) — mọi lệnh pytest phải chạy qua `python3 -c "import sys,pytest; sys.exit(pytest.main(['-q']))"`.