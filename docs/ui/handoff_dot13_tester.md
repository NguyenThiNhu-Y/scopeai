# HANDOFF NOTE — ĐỢT 13 · Bước tester

## Đã làm
1. **Chạy toàn bộ test**: backend `pytest -q` **358 passed, 0 fail** (exit 0); frontend `npm run test` **28 passed** (2 files); `npm run build` **OK** (0 lỗi TS).
2. **Preview**: rebuild stack với code Đợt 13, `LLM_PROVIDER=mock`, health OK. **Sửa preview**: mount `./docs:/app/docs:ro` cho backend để `GET /api/eval/reports/latest` tìm được báo cáo (defect D-13-1).
3. **Kiểm UI + API trên bid 144 (ja_email)** — số liệu thật, đầy đủ trong `docs/ui/dot13_check.md`:
   - Thẻ độ tin cậy Tổng quan (Thấp + 3 lý do + Xem chi tiết → tab Kế hoạch).
   - Khối "So với dự án tương tự" khớp API (2 case, thanh so sánh ƯL vs TT, Sai lệch lịch sử).
   - Truy vết 34/36 + cột Requirement (chip, hover nội dung) + bấm FR-019 → tab Đáp ứng.
   - Import case study: tải template, preview lỗi theo dòng (7 lỗi dòng 2), save → version 2 → **đã khôi phục** repo (v1, 13 case).
   - Khóa duyệt mức Thấp: xóa task QA WBS-002-01-04 → wbs_checks fail pm_qa_ok → nút khóa tới khi ≥ 10 ký tự → duyệt → snapshot "Đã duyệt khi mức độ tin cậy: Thấp · Case study v1 · Ngưỡng v1" (GET /approvals id=5) → **đã khôi phục task QA**.
   - Tab Ngưỡng độ tin cậy: sửa + lưu → version 2 → **đã khôi phục** repo.
   - Tab Đánh giá hệ thống: bảng tổng hợp 8 chỉ số + từng case 12 cột, provider mock, 1.81s; **kiểm thêm trường hợp 404** (di chuyển file json tạm) → UI hiện "Chưa có báo cáo đánh giá hệ thống." → đã khôi phục.
   - Screenshot thật: `docs/ui/dot13_{overview,plan_analog,approvals,after_approve,import_preview,eval_tab,eval_404,wbs_hover}.png`.
4. **Ghi `docs/ui/dot13_check.md`** — số liệu thật, nhãn tiếng Việt, không ảnh giả.

## Defect phát hiện (chưa sửa code — báo backend-dev)
- **D-13-1 (Thấp)**: `settings.py:25` resolve `Path("docs/eval/reports")` theo CWD → 404 khi backend chạy từ `backend/` dù có báo cáo. Đề xuất: resolve từ `__file__` (như `eval/report.py:14`). Preview đã workaround bằng mount docs.
- **D-13-2 (Thấp)**: `WbsTaskIn.man_day le=10` không tái tạo được man_day pipeline > 10 (task QA gốc 18.0) khi sửa qua API → tổng WBS lệch nhỏ khi khôi phục. Ràng buộc có trước, không phải regression Đợt 13.
- **D-1 (kế thừa Đợt 12, chưa sửa)**: tokai_minato không chạy pipeline qua API (PDF sample_data bị route vào parser Excel). Mục này BLOCKED, dùng ja_email thay thế.

## Trạng thái dữ liệu sau kiểm thực (đã khôi phục)
- `case_studies`: repo default (version 1, 13 case) — đã xóa row DB tạo khi test import.
- `confidence`: repo default (version 1) — đã xóa row DB tạo khi test lưu.
- Bid 144: trạng thái **waiting_price_approval** (đã duyệt kỹ thuật trong test), WBS có đủ 4 task QA (man_day 10 thay vì 18 gốc → tổng 202 vs 210), confidence low (leaf_within_limit như gốc), traceability 34/36. Bản ghi approvals id=5 (tech approved, snapshot Thấp) còn lại — là bằng chứng kiểm thực.
- Bid 145 (tokai_minato): draft, chưa confirm được (D-1) — để lại không ảnh hưởng.

## Bàn giao cho bước sau (reviewer)
- Đọc `docs/ui/dot13_check.md` → ghi `docs/ui/dot13_review.md` đối chiếu thiết kế §7 + task A–F.
- Lưu ý: D-13-1 (eval path), D-13-2 (man_day cap), D-1 kế thừa (tokai). Bid 144 đã duyệt kỹ thuật (waiting_price_approval) — nếu reviewer cần xem trạng thái chờ duyệt kỹ thuật thì tạo hồ sơ ja_email mới.
- Preview đang chạy (backend mock, docs đã mount).