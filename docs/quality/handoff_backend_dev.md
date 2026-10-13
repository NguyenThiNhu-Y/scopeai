# Handoff — Backend Dev: Fix FE↔BE audit (F-01, F-02)

Ngày: 2026-10-11
Bước: Fix (Backend Dev) — workflow rà soát & fix lỗi FE gọi BE
Nguồn: `docs/quality/fe_be_audit.md` + `docs/quality/handoff_fe_be_audit.md`

## Deliverables (files changed)

- `backend/app/services/proposal_service.py` — **F-01 CRITICAL**: thêm `_normalize_sections()` / `_normalize_translations()`; `to_out()` và `translate()` normalize sections khi đọc (điền đủ 8 key theo `SECTION_NAMES`, bỏ key thừa như `conclusion`, giá trị rỗng → `[Đang chờ proposal]`). Fix ở lớp đọc (BR-09), **không migrate DB**.
- `backend/app/main.py` — **F-02 MEDIUM**: thêm `X-Role`, `X-User` vào `allow_headers` của CORS (FE vẫn gửi các header này tại `client.ts:172,424,431,438`).
- `backend/tests/test_proposal_legacy_normalize.py` — regression test mới (4 test).

## Verification

- Lệnh chạy test (bắt buộc qua python -c, wrapper `rtk` nuốt output pytest):
  `cd backend && python3 -c "import sys,pytest; sys.exit(pytest.main(['-q']))"`
- Kết quả: **245 passed** (baseline 241 + 4 regression mới). Không fail, không warning mới.
- Probe runtime (uvicorn thật, `LLM_PROVIDER=mock`, DB thật `data/bidding.db`):
  - `GET /api/bids/110/proposal` → **HTTP 200**, đủ **8 section keys**: `approach, assumptions_and_scope, introduction, requirements_understanding, risks, schedule, solution_overview, team`; `document.table_of_contents` đủ 8 mục; không còn `conclusion`.
  - Spot-check thêm bid legacy: 80, 91, 104, 105 → **HTTP 200, 8 sections**; bid 112 (schema mới) → HTTP 200, 8 sections.
  - CORS preflight (Origin localhost:5173, `Access-Control-Request-Headers: content-type,x-role,x-user,x-actor`) → **200**, `access-control-allow-headers` gồm `X-Actor, X-Role, X-User`.

## Ghi chú F-02 (theo yêu cầu)

- `X-Role` **không được backend đọc** (`app/api/deps.py` `get_identity` chỉ đọc `X-Actor`/`X-User`). Header này là dự phòng/giả lập vai trò phía FE, không phải cơ chế phân quyền thật (đúng ghi chú GATE-01). Đã thêm vào `allow_headers` để preflight cross-origin không fail; nếu muốn dọn dẹp sau này thì bỏ `X-Role` khỏi `client.ts`.

## Blockers

- Không có. Frontend defense (`ProposalPage.tsx` `sections[key] ?? ''`) thuộc phạm vi frontend-dev — chưa đụng.

## Việc tiếp theo

- Frontend dev: phòng thủ `ProposalPage.tsx` (F-01) — song song đã hoàn tất phần backend.
- Verify: chạy lại toàn bộ test (backend 245 + frontend) + probe `GET /api/bids/110/proposal` phải trả 200 đủ 8 mục.