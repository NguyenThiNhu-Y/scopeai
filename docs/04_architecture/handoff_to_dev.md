# Handoff — Coordinator (SA + PM) → Implementation Team

| Thuộc tính | Giá trị |
|---|---|
| Từ | Parallel Dispatch Coordinator (SA + PM chạy song song, đã reconcile) |
| Cho | Backend Dev, Frontend Dev, Cloud/Infra (bước tiếp theo) |
| Ngày | 2026-10-09 |
| Nguồn | `docs/04_architecture/` (4 file), `docs/05_roadmap/roadmap.md`, `docs/03_requirements/srs.md` (v1.1), `docs/03_requirements/handoff_to_design.md` |

---

## 1. Kết quả đã giao

| File | Nội dung |
|---|---|
| `docs/04_architecture/architecture.md` | Monolith 2 tầng (React SPA + FastAPI), pipeline in-process (asyncio) + SSE, tech stack, env vars, cách chạy/test, **5 ADR**, mapping AGENTS.md rules 1–10, chốt 10 câu hỏi mở |
| `docs/04_architecture/llm_pipeline.md` | **7 bước pipeline** (intake → gap/questions → evaluate ◎/○/△/× → solution → wbs → proposal → ja_check): input, JSON schema, validation bằng code, retry ≤ 2, con số do code tính, reference tables, persist/resume, snapshot WBS |
| `docs/04_architecture/data_model.md` | **16 bảng SQLite** (bids, attachments, requirements, evaluations, questions, solution_choices, wbs_items, wbs_snapshots, schedules, quotations, approvals, pipeline_steps, proposal_drafts, export_logs, settings, reference_snapshots, changelog) + máy trạng thái |
| `docs/04_architecture/api_contract.md` | **Contract FROZEN**: 25+ endpoint root-relative `/api`, error codes tiếng Việt (400/404/409/422/500 + X-Role), SSE schema, **§12 ánh xạ milestone→endpoint (đã reconcile)** |
| `docs/05_roadmap/roadmap.md` | **8 milestone vertical** (M1 Foundation → M2 Phân tích+hỏi làm rõ → M3 Hướng giải pháp+effort → M4 WBS+schedule → M5 Proposal+giá+duyệt → M6 Đính kèm+ma trận → M7 Xuất file → M8 Hoàn thiện), acceptance criteria (shell + Preview), test strategy, DoD, ma trận FR→milestone |

## 2. Quyết định kiến trúc then chốt (bắt buộc tuân theo)

1. **Stack:** Python 3.11 + FastAPI + uvicorn (port 8000) + SQLite; React + Vite + TypeScript + Tailwind. Frontend gọi root-relative `/api` (BR-10) — cấm hardcode localhost.
2. **BR-01 (nhạy nhất):** LLM đề xuất WBS chỉ với **trọng số tương đối (1–100)**; **code gán man-day** từ midpoint bảng chuẩn. Schema LLM không chứa man-day/giá/ngày — có unit test assert (`test_llm_schema_no_numbers.py`).
3. **Bảng chuẩn YAML** ở `backend/app/reference/*.yaml` (repo) + override DB (`settings`) + **snapshot** vào `reference_snapshots` tại thời điểm tính (ADR-003) → FR-033/FR-061/BR-11.
4. **Progress realtime:** SSE (ADR-002), không WebSocket/polling. Pipeline persist từng bước (FR-023), resume từ bước lỗi.
5. **Vai trò MVP:** header `X-Role: presales|ai_developer|manager` + `X-User` (giả lập). Chặn tự duyệt giá: `approver != created_by` (FR-042.2). Khóa hồ sơ ở service layer → `409 STATE_CONFLICT`.
6. **PDF tiếng Nhật:** LibreOffice headless + font Noto CJK (cần cài vào image Preview trước M7). Kiểm tra tiếng Nhật (FR-025): rule-based + LLM phụ trợ.
7. **.xls:** đọc bằng xlrd; file lỗi → báo "lưu lại dưới dạng .xlsx".

## 3. Thứ tự triển khai (roadmap 8 milestone — vertical, chạy được end-to-end)

M1 → M2 → M3 → M4 → M5 → M7 → M8 (chuỗi cứng); **M6 song song** với M3–M5 (phụ thuộc mềm), xong trước M7. Chi tiết endpoint từng milestone: `api_contract.md` §12.

- **M1:** skeleton, `/api/health`, LLM gateway mock + mask PII, DB, pytest + `npm run build`, README, bộ test PII ≥ 50 mẫu.
- **M2:** tạo hồ sơ + danh sách/mở lại (FR-007), hỏi ≤ 7 câu/2 vòng, pipeline start + SSE + rerun, hồ sơ mẫu giả lập (text).
- **M3:** hướng giải pháp + effort code tính + hệ số có trần + dấu vết. **Cần bộ số giả lập (effort min–max, rate card, tỉ giá, trần hệ số 2.0) phê duyệt trước M3.**
- **M4:** WBS (trọng số AI → man-day code) + kiểm tra midpoint ±20% + PM/QA + snapshot; master schedule (nghỉ lễ, hạn nộp).
- **M5:** quotation + duyệt kỹ thuật + duyệt giá (chặn tự duyệt, khóa, từ chối) + kiểm tra trước duyệt (mục "không sót requirement" nối dữ liệu ở M6).
- **M6:** attachments + parse (nhiều sheet, mã nội bộ) + ma trận đáp ứng ◎/○/△/× đầy đủ.
- **M7:** kiểm tra tiếng Nhật (FR-025) + xuất Word/Excel/PDF bằng code (cổng giá `[Presales điền]`). PowerPoint **ngoài MVP** (SRS §8.2) — tùy chọn, không chặn.
- **M8:** settings (bảng chuẩn YAML validate toàn vẹn), lịch sử, UX states.

## 4. Điểm cần bước tiếp theo xử lý

1. **Bộ số giả lập** (effort min–max, rate card, tỉ giá, overhead PM 10%/BrSE 15% trên phần offshore, trần hệ số 2.0) — BA/PM phê duyệt **trước M3**; vị trí file YAML đã định trong ADR-003.
2. **LibreOffice headless + font Noto CJK** cài vào image Preview **trước M7** (xuất PDF tiếng Nhật).
3. **Bộ test PII (≥ 50 mẫu)** + **bộ mẫu tiếng Nhật (20 câu)** — xây fixture từ M1/M2.
4. **Kịch bản demo S-01:** người demo phải **đổi X-Role** khi duyệt giá (chặn tự duyệt FR-042.2); demo trọn luồng hồ sơ tiếng Nhật ≤ 10 phút.
5. **Contract FROZEN** — backend và frontend phải bám `api_contract.md`; mọi thay đổi contract phải cập nhật §12 và thông báo cả 2 phía.
6. **DoD (BR-08):** test tự động pass + chạy được trong Preview — mỗi milestone phải chứng minh cả 2.

---

**Task Coordinator (SA + PM) complete. Awaiting prompt for the next role.**