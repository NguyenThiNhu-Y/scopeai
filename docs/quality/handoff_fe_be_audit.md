# Handoff — Analyze: Audit FE ↔ BE

Ngày: 2026-10-11
Bước: Analyze (Solution Architect) — workflow rà soát & fix lỗi FE gọi BE

## Deliverable

Báo cáo đầy đủ: **`docs/quality/fe_be_audit.md`** (đối chiếu toàn bộ endpoint ↔ client, findings kèm file:line, cách tái hiện, đề xuất fix, baseline test).

## Tóm tắt cho bước Fix

1. **F-01 CRITICAL — proposal legacy data**: DB `proposal_drafts.sections` của bid 80..110 lưu schema cũ **5 mục** (thiếu `requirements_understanding`, `schedule`, `team`, `assumptions_and_scope`; thừa `conclusion`). Hệ quả: `GET /api/bids/{id}/proposal` trả **HTTP 500** (ResponseValidationError); bản build cũ làm FE crash `sections[key].split('{{QUOTATION}}')` tại `frontend/src/pages/ProposalPage.tsx:51`.
   - Fix backend: normalize sections ở `backend/app/services/proposal_service.py` (`get_or_create`/`to_out`) — điền đủ 8 key theo `SECTION_NAMES`, bỏ key thừa; áp dụng cho cả `translations` nếu cần. Không migrate DB thủ công.
   - Fix frontend: phòng thủ `ProposalPage.tsx` (`sections[key] ?? ''`, `v?.includes(...)`).
   - Regression test backend: row 5 mục cũ → GET trả 200 đủ 8 mục.
2. **F-02 MEDIUM — CORS**: `backend/app/main.py` `allow_headers` thiếu `X-Role`, `X-User` mà FE gửi (`client.ts:172,424,431,438`); `X-Role` không được `deps.py` đọc. Thêm vào allow_headers hoặc bỏ header thừa.
3. **F-03 LOW — quotations.totals** row cũ thiếu `payment_plan`/`odc_fte_months` (bid 104, 105) — FE đã có fallback, không bắt buộc.

## Bằng chứng / lưu ý môi trường

- Baseline: backend **241 passed** · frontend **11 passed** · `npm run build` **PASS**.
- Probe runtime: `GET /api/bids/110/proposal` → **HTTP 500** (đã chạy uvicorn thật, LLM_PROVIDER=mock).
- **Wrapper `rtk` nuốt output pytest** (`Pytest: No tests collected`). Mọi lệnh pytest phải chạy:
  `python3 -c "import sys,pytest; sys.exit(pytest.main(['-q']))"` từ `backend/`.
- Không sửa code ở bước này (chỉ tài liệu).

## Việc tiếp theo

Bước **Fix** (song song backend-dev + frontend-dev) theo F-01..F-03, sau đó bước **Verify** chạy lại toàn bộ test + probe `GET /api/bids/110/proposal` phải trả 200 đủ 8 mục.