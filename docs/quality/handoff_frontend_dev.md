# Handoff — Fix: Frontend (FE↔BE)

Ngày: 2026-10-11
Bước: Fix (Frontend Developer) — workflow rà soát & fix lỗi FE gọi BE
Phạm vi: `frontend/src/pages/ProposalPage.tsx`, `frontend/src/api/client.ts` (chỉ sửa theo bằng chứng trong `docs/quality/fe_be_audit.md`)

## Việc đã làm

### F-01 CRITICAL — ProposalPage crash khi `sections[key]` undefined (legacy 5 mục)
File: `frontend/src/pages/ProposalPage.tsx`
- Dòng 51 (`proposalMarkdown` useMemo): `sections[key].split('{{QUOTATION}}')` → `(sections[key] ?? '').split('{{QUOTATION}}')`. Không đổi hành vi khi dữ liệu hợp lệ.
- Dòng 59: `Object.values(sections).some((value) => value.includes(...))` → `value?.includes(...)`.
- Dòng 141 (textarea chỉnh sửa): `value={sections[key]}` → `value={sections[key] ?? ''}` (tránh warning controlled input + không bao giờ render undefined).
- Đã grep toàn bộ `frontend/src`: 3 chỗ đọc `sections[key]` / `Object.values(sections)` đều nằm trong ProposalPage.tsx và đều đã có fallback. Không còn chỗ đọc không an toàn.

### F-02 MEDIUM — Header `X-Role` FE gửi nhưng backend không đọc
File: `frontend/src/api/client.ts`
- Backend `deps.py` chỉ đọc `X-Actor`/`X-User`, KHÔNG đọc `X-Role` (đã xác minh lại).
- Theo đề xuất audit ("bỏ header không dùng ở FE"): bỏ `X-Role` khỏi 4 request: `updateSetting` (:172), `approveTech` (:424), `approvePrice` (:431), `unlockBid` (:438).
- GIỮ `X-User` (backend có đọc). Phần CORS `allow_headers` (`main.py`) thuộc scope backend-dev.

### BR-10 — Base root-relative `/api`
- Đã grep `frontend/src`: không có `localhost`/`127.0.0.1`/URL tuyệt đối. `client.ts` dùng `API_BASE = '/api'` — không cần sửa.

## Kết quả kiểm chứng (đã chạy thật)

| Hạng mục | Lệnh (từ `frontend/`) | Kết quả |
|---|---|---|
| Test | `npm test` | **PASS — 11 passed** (1 file, App.test.tsx) |
| Build | `npm run build` | **PASS** (tsc -b && vite build, 3.40s) |

Không test cũ nào fail → không phải đổi test.

## Lưu ý cho bước Verify

- Backend-dev xử lý song song: normalize sections legacy 5→8 mục ở `proposal_service.py` + regression test; thêm `X-User` (và nếu giữ thì `X-Role`) vào `allow_headers` trong `main.py`.
- Verify cần chạy lại: backend pytest (qua `python3 -c "import sys,pytest; sys.exit(pytest.main(['-q']))"` — wrapper `rtk` nuốt output), frontend `npm test` + `npm run build`, probe runtime `GET /api/bids/110/proposal` phải trả 200 đủ 8 mục, và mở tab Proposal của bid 80–110 không crash.
- Với dữ liệu legacy 5 mục, sau fix FE này tab Proposal hiển thị các mục thiếu là nội dung rỗng (không crash); sau fix backend sẽ hiện `[Đang chờ proposal]`.

## Blockers

Không có.