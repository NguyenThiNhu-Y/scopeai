# HANDOFF NOTE — ĐỢT 12 · Bước reviewer

## Đã làm
1. Đọc toàn bộ `docs/eval/thiet_ke_danh_gia.md`, `docs/ui/dot12_check.md` (kết quả kiểm thực thật),
   và các file code ĐỢT 12: confidence_engine.py, confidence.yaml, case_studies.yaml,
   wbs_structure.py (requirement_codes), settings_service.py (validate), settings.py
   (template/import/wbs), case_study_service.py, approval_service.py (duyệt + snapshot),
   sample_service.py (tokai_minato), eval/ (metrics, run_eval, report), b5_wbs.py, mock_client.py,
   models/wbs_item.py, db.py, Makefile.
2. Đối chiếu TỪNG mục thiết kế → kết luận Đạt/Chưa đạt/Một phần kèm file:dòng + số liệu check doc.
3. Ghi `docs/ui/dot12_review.md`.

## Kết luận
- **Đạt**: mục 3.1/3.2 (13 case = 7 gia_lap + 6 tokai, schema bảng 3.2 đủ tech/bid_outcome/wbs_file,
  validate PUT + import), 3.3 (template/import preview/save/lỗi theo dòng/gộp id/che PII/changelog),
  3.4 (WBS upload/download, khớp actual_man_day ±1, điểm nóng >30%), 4 (requirement_codes ≤8 task lá,
  prompt ≤150 dòng, bỏ mã không tồn tại, WbsTaskIn sửa được, mock gán theo category bỏ "cần làm rõ",
  test_llm_schema_no_numbers pass), 5.1–5.4 (engine thuần, ConfidenceOut đúng, 7 tín hiệu, quy tắc mức,
  case tương tự, confidence.yaml có phiên bản), 5.5 (Thấp → nhận xét ≥10 ký tự + snapshot), 6 (eval
  harness đủ, make eval, --case/--repeat, báo cáo md+json có provider/model + mock note), D (sample
  tokai_minato ja/JPY).
- **Một phần**: mục D qua API — chặn bởi **D-1**.
- **Chưa làm (tùy chọn, đúng phạm vi)**: mục G (4b structure hint, hotspot_coverage, 3.5 bài học).
- **Ngoài phạm vi**: mục 7 giao diện.

## Việc cần làm tiếp (bàn giao backend-dev / đợt sau)
- **D-1 (trung bình)**: `parse_service.parse()` route attachment `file_type=="sample_data"` vào parser
  Excel bất kể extension → PDF `MC-850H_manual_excerpt.pdf` của mẫu tokai_minato lỗi → pipeline qua API
  chặn. Đề xuất: rẽ theo extension (xlsx/csv → read_sheets; pdf/docx/txt → text) trước khi xét file_type.
  Eval harness không bị ảnh hưởng (đi đường nội bộ).
- Ghi chú nhỏ (không bắt buộc): text task ghi "14 case" nhưng thiết kế ghi 6 tokai — hiện trạng 13 case
  đúng thiết kế; `effort_midpoint` = midpoint effort engine (thiết kế chưa định nghĩa rõ);
  approval_service.py có style nén nhiều lệnh/dòng (cũ, không phải mới).

## Trạng thái
- Preview vẫn chạy (backend mock); case_studies đã khôi phục mặc định repo (version 1, 13 case).
- 358 test backend + 16 frontend + build OK.
- Báo cáo eval `docs/eval/reports/eval_20261013_1753_mock.{md,json}` tồn tại trên đĩa nhưng CHƯA commit
  (workflow cấm lệnh git; toàn bộ tree đang untracked trong session này) — nếu cần, người vận hành tự commit.
- Không sửa code trong bước reviewer (đúng vai trò chỉ review/comment).