# Handoff — Verify FE↔BE Fix (tổng hợp)

Trạng thái: **✅ PASS — review APPROVED**. Sẵn sàng cho bước tiếp theo.

## Root cause
DB SQLite (`backend/data/bidding.db`) có 14 hồ sơ legacy (bid 80–110) lưu `proposal_drafts.sections` theo schema cũ **5 mục** (`introduction, solution_overview, approach, risks, conclusion`) — thiếu `requirements_understanding, schedule, team, assumptions_and_scope`. Schema hiện tại yêu cầu đủ 8 mục → `GET /api/bids/{id}/proposal` trả HTTP 500 (ResponseValidationError); bản build cũ trả thiếu key làm FE crash `Cannot read properties of undefined (reading 'split')` tại `ProposalPage.tsx:51`.

## Fix đã làm (bước Fix)
- **Backend** (`backend/app/services/proposal_service.py`): `_normalize_sections()`/`_normalize_translations()` — normalize ở lớp đọc: điền đủ 8 key theo `SECTION_NAMES` (thiếu/empty → `[Đang chờ proposal]`), loại key thừa `conclusion`. Không ghi đè DB trừ khi user PUT (BR-09).
- **Backend** (`backend/app/main.py:40`): CORS `allow_headers` thêm `X-Role`, `X-User`.
- **Backend** (`backend/tests/test_proposal_legacy_normalize.py`): 4 regression test.
- **Frontend** (`frontend/src/pages/ProposalPage.tsx`): guard đọc sections tại `:51 ?? ''`, `:59 value?.includes`, `:141 ?? ''`.
- **Frontend** (`frontend/src/api/client.ts`): bỏ `X-Role` (backend không đọc) ở updateSetting/approveTech/approvePrice/unlockBid; giữ `X-User`.

## Bằng chứng (bước Verify, chạy độc lập)
| Kiểm chứng | Kết quả |
|---|---|
| Backend pytest (toàn bộ) | **245 passed, 0 fail** (exit 0) — 241 baseline + 4 regression |
| Frontend `npm test` | **11 passed (11)** |
| Frontend `npm run build` | **PASS** (tsc -b && vite build, 2.77s) |
| Runtime `GET /api/bids/110/proposal` | **200**, đủ 8 mục, không key thừa |
| Runtime `GET /api/bids/80/proposal` | **200**, đủ 8 mục, không key thừa |
| Review code | **APPROVED** (4/4 mục: đúng đắn, AGENTS.md, độ phủ, FE crash scan) |

Chi tiết: `docs/quality/fe_be_fix_verification.md`, `docs/quality/fe_be_fix_review.md`.

## Việc còn lại (follow-up, không chặn — từ review)
- **W1 (Major-ish)**: `backend/app/exporters/export_service.py:35` vẫn đọc `draft.sections` thô → export DOCX/PDF cho hồ sơ legacy chỉ ra 5 mục + heading thừa `conclusion` (không crash, lệch hợp đồng 8 mục). Đề xuất tái dùng `_normalize_sections()` ở export path.
- **W2 (Minor)**: `str(value)` tại `proposal_service.py:30` — nên `value if isinstance(value, str) else PLACEHOLDER` để phòng dữ liệu hỏng.
- **Kiểm tra UI trên Preview**: mở tab Proposal với hồ sơ cũ (bid 80–110) để xác nhận hiển thị placeholder 8 mục trên trình duyệt thật (runtime API đã 200, UI chưa chụp màn hình).

## File liên quan
- Audit: `docs/quality/fe_be_audit.md`
- Handoff fix: `docs/quality/handoff_fe_be_fix.md`
- Verification: `docs/quality/fe_be_fix_verification.md`
- Review: `docs/quality/fe_be_fix_review.md`