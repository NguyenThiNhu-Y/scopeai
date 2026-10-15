# ĐỢT 12 — Đánh giá đối chiếu thiết kế ↔ hiện trạng (reviewer)

Ngày: 2026-10-13 · Người đánh giá: reviewer
Đối chiếu: `docs/eval/thiet_ke_danh_gia.md` ↔ code backend ĐỢT 12 + số liệu kiểm thực
`docs/ui/dot12_check.md` (tester, chạy trên Preview thật, LLM_PROVIDER=mock).

Kết luận chung: **Đạt** — backend ĐỢT 12 triển khai đúng thiết kế ở các mục bắt buộc
(3.1–3.4, 4, 5.1–5.5, 6, D). Không có lỗi chặn. 1 defect trung bình (D-1) ảnh hưởng
mục D khi chạy qua API; các mục tùy chọn (G) chưa làm, đúng phạm vi.

---

## Mục 3.1/3.2 — Thư viện case study: lưu trữ + schema → **Đạt**

| Yêu cầu thiết kế | Hiện trạng | Kết luận |
|---|---|---|
| Mặc định nạp từ `backend/app/reference/case_studies.yaml`, thay mẫu 1 dòng trong OPTIONAL_DEFAULTS | `settings_service.FILES["case_studies"]` trỏ `case_studies.yaml`; OPTIONAL_DEFAULTS không còn case_studies (settings_service.py:13-22, 23-28) | ✅ |
| Gộp `case_studies_gia_lap.yaml` (bỏ `cs_rag_maintenance_jp_vn`) + `case_studies_tokai.yaml` | case_studies.yaml có **13 case** = 7 gia_lap (8 − cs_rag_maintenance_jp_vn) + 6 tokai; `cs_rag_maintenance_jp_vn` chỉ còn trong comment (case_studies.yaml:2). Lưu ý: text task ghi "14 case" nhưng thiết kế §3.2 ghi "6 dự án Tokai" — hiện trạng 13 case đúng theo thiết kế | ✅ |
| 6 file WBS mẫu copy vào `backend/app/reference/case_studies_wbs/` | Đủ 6 file xlsx (case_studies_wbs/); 6 case tokai đều có `wbs_file` trỏ đúng tên | ✅ |
| Schema đúng bảng 3.2, validate Pydantic khi PUT + import | `CaseStudy` đủ trường bảng 3.2 kể cả `tech`, `bid_outcome`, `wbs_file` (schemas/case_study.py:78-105); `actual_man_day` không bắt buộc (case thua thầu vẫn lưu — đúng §3.2); validate khi PUT (settings_service.py:39-47) + import (normalize_case_studies) | ✅ |
| Case thiếu actual_man_day không dùng để so sánh | `find_similar_cases` lọc `not case.get("actual_man_day")` (confidence_engine.py:133) | ✅ |

## Mục 3.3 — Nhập và xuất → **Đạt**

| Yêu cầu | Hiện trạng | Kết luận |
|---|---|---|
| GET template Excel mẫu, cột theo schema, trường lồng tách cột | `GET /api/settings/case_studies/template` → 38 cột (actual_poc…contract_production…wbs_file) + dòng ví dụ (case_study_service.py:131-187); tester tải được 6 KB | ✅ |
| POST import xlsx/csv/yaml, mode preview/save | Router + service đủ 3 định dạng, `mode ∈ {preview, save}` (case_study_service.py:192-276) | ✅ |
| preview: lỗi theo từng dòng (số dòng, cột, lý do), không lưu | `normalize_case_studies` trả `Dòng <n>: cột '<field>': <lý do>`; tester ghi nguyên văn 3 lỗi dòng 2 (dot12_check.md §6) | ✅ |
| save: gộp theo id (trùng ghi đè), phiên bản mới, changelog | `import_cases` gộp `by_id` → `update_setting` tạo version + Changelog; tester: save → version 2, confidence đổi `case_studies_version` 1→2, history_bias 3→4 case (dot12_check.md §6) | ✅ |
| Che PII trong summary và lessons_vi | `mask_text` áp dụng cả 2 trường trước khi lưu/hiển thị (case_study_service.py:240-245) | ✅ |

## Mục 3.4 — File WBS dự án cũ → **Đạt**

| Yêu cầu | Hiện trạng | Kết luận |
|---|---|---|
| POST/GET `/api/settings/case_studies/{id}/wbs` | Router đủ 2 endpoint (settings.py:52-73); upload lưu `data/case_studies/<id>/` + cập nhật `wbs_file` (case_study_service.py:402-434); download ưu tiên file tải lên rồi file mặc định (resolve_wbs_file) | ✅ |
| Đọc sheet WBS theo định dạng mẫu, kiểm tổng thực tế khớp actual_man_day (lệch > 1 → cảnh báo, không chặn) | `parse_wbs_workbook` đọc cột Mã/Hạng mục/作業項目/Giai đoạn/ước lượng/thực tế/Requirement; `_compare_with_actual` cảnh báo khi |lệch| > 1 (case_study_service.py:289-399). Tester: 81 dòng, tổng 573.0, khớp actual_man_day 96/335/142 | ✅ |
| Điểm nóng: thực tế vượt ước lượng > 30% | `actual > estimated * 1.3` → hotspot kèm ratio (case_study_service.py:355-363); tester: 7 điểm nóng ratio 1.5–1.57 | ✅ |

## Mục 4 — Truy vết requirement → **Đạt**

| Yêu cầu | Hiện trạng | Kết luận |
|---|---|---|
| `WbsTaskItem.requirement_codes` (tối đa 8, chỉ task lá) | Schema có `requirement_codes: list[str] max_length=8`; validator chặn task nhóm mang mã (wbs_structure.py:44, 99-111) | ✅ |
| Cột JSON nullable ở wbs_items + migration | `models/wbs_item.py:58` `requirement_codes: Mapped[list\|None] = mapped_column(JSON, nullable=True)`; db.py có cơ chế ALTER ADD COLUMN (db.py:99) | ✅ |
| Prompt B5: danh sách requirement gọn (mã + 80 ký tự + nhóm, ≤ 150 dòng) | b5_wbs.py:79-90 cắt 80 ký tự, `requirement_lines[:150]`; prompt yêu cầu task lá ghi mã, chưa rõ thì để trống (prompts/b5_wbs.py:7-8, 21) | ✅ |
| Code bỏ mã không tồn tại (ghi vào notes) | b5_wbs.py:108-121 lọc theo `existing_codes`, note "Đã bỏ mã requirement không tồn tại" | ✅ |
| WbsTaskIn và bảng WBS sửa được requirement_codes | `WbsTaskIn.requirement_codes` (api_schemas/wbs.py:71); `_apply_update` xử lý field + chặn gán cho task nhóm (wbs_service.py:322-334) | ✅ |
| Mock gán theo category (FR→backend/frontend, NFR→infra/qa, vòng tròn); KHÔNG gán requirement "cần làm rõ" | `_assign_requirement_codes` + `_is_unclear_requirement` (mock_client.py:570-611) | ✅ |
| `test_llm_schema_no_numbers` vẫn pass | `tests/test_llm_schema_no_numbers.py:62` `test_every_llm_schema_has_no_number_fields` — nằm trong 358 passed | ✅ |
| Mẫu Nhật 34/36, 2 mục cần làm rõ trong danh sách chưa có task | Tester: 34/36, uncovered FR-019, FR-020 (dot12_check.md §4) — đúng kỳ vọng thiết kế | ✅ |

## Mục 5.1–5.4 — Độ tin cậy từng hồ sơ → **Đạt**

| Yêu cầu | Hiện trạng | Kết luận |
|---|---|---|
| `confidence_engine.py` hàm thuần, không gọi LLM, không import gateway | Docstring + code: chỉ tính từ dict đầu vào (confidence_engine.py:1-11, 526-569); không import gateway/DB | ✅ |
| GET /bids/{id}/confidence trả đúng ConfidenceOut §5.1 | Schema đủ level/level_label_vi/summary_vi/signals/analog/thresholds_version/case_studies_version (api_schemas/confidence.py:43-50); service gom dữ liệu (confidence_service.py:111-174) | ✅ |
| 7 tín hiệu §5.2 đúng ngưỡng | Đủ 7 hàm tín hiệu; ngưỡng khớp bảng §5.2 (traceability 0.95/0.80, coverage 0.15/0.30, history 0.90–1.10, analog ±10%/20%, schedule 14 ngày, input 4 mục, wbs 4 cờ) (confidence.yaml) | ✅ |
| Quy tắc ra mức §5.3 cố định, có test | `decide_level`: fail quan trọng hoặc ≥2 fail → low; ≥1 fail khác hoặc ≥2 warn → medium; còn lại high; summary ≤ 3 lý do (confidence_engine.py:495-521) | ✅ |
| Tìm case tương tự §5.4: lọc cùng hướng + có actual, công thức 0.4/0.3/0.2/0.1, ≥0.5, ≤3, dưới 2 → insufficient | `find_similar_cases` + `similarity_score` đúng công thức (confidence_engine.py:77-157); dưới 2 case → position insufficient (signal_analog:397-409) | ✅ |
| Ngưỡng trong confidence.yaml có phiên bản, sửa qua settings | `FILES["confidence"]` + PUT settings validate dict (settings_service.py:21, 48-49); version tăng khi sửa | ✅ |
| Kiểm thực thật | Bid 144: mức **low (Thấp)**, đủ 7 tín hiệu, analog 2 case (cs_none_crm_jp 0.92/235.0, cs_none_booking_jp 0.88/266.0), range [235,266], position below, history_bias none/1.07/3 (dot12_check.md §3, §5) | ✅ |

Ghi chú nhỏ: `effort_midpoint` trong analog = midpoint của effort engine (210.0), còn ví dụ
§5.1 minh họa 241.5 — thiết kế không định nghĩa rõ; cách hiện tại hợp lý và có tài liệu.

## Mục 5.5 — Gắn vào luồng duyệt → **Đạt**

| Yêu cầu | Hiện trạng | Kết luận |
|---|---|---|
| Mức Thấp bắt buộc nhận xét ≥ 10 ký tự mới duyệt được | `approval_service.tech()`: `confidence["level"] == "low"` → `len(review) < 10` → validation_error (approval_service.py:32-40) | ✅ |
| Lưu snapshot confidence + phiên bản case_studies/confidence vào bản ghi duyệt | `row.snapshot = {confidence, case_studies_version, confidence_thresholds_version}` (approval_service.py:43-48) | ✅ |

Ghi chú nhỏ: approval_service.py có sẵn phong cách nén nhiều lệnh/dòng (dòng 29, 41, 49, 72)
— không phải mới trong ĐỢT 12; phần snapshot mới viết rõ ràng.

## Mục 6 — Eval harness → **Đạt**

| Yêu cầu | Hiện trạng | Kết luận |
|---|---|---|
| `backend/eval/{cases/, metrics.py, run_eval.py, report.py}` | Đủ cấu trúc; golden_cases.yaml tách 3 file/case (gc_crm_ja, gc_inventory_vi, gc_tokai_rag) | ✅ |
| Tự trả lời câu hỏi bằng answers trong case | `_run_pipeline` dùng `case["answers"]["default"]` cho mọi câu chờ (run_eval.py:132-164); mock dùng fixture no_questions để chạy thẳng | ✅ |
| Đủ chỉ số §6.2 + tổng hợp §6.3 | metrics.py:15 chỉ số (kể cả stability_cv khi repeat ≥ 2) + aggregate (MAPE, rates, %, avg) | ✅ |
| Báo cáo md + json có provider/model; mock ghi chú | report.py:52-113; báo cáo `eval_20261013_1753_mock.{md,json}` ghi provider=mock, model=mock, chú thích "Mock chỉ kiểm tra harness, không đo chất lượng AI" | ✅ |
| `make eval`; hỗ trợ --case và --repeat | Makefile:22 `cd backend && python -m eval.run_eval`; argparse --case (append) + --repeat (run_eval.py:309-316) | ✅ |
| Chạy 1 lần với mock và commit báo cáo | Báo cáo 17:53 mock đã ghi vào `docs/eval/reports/eval_20261013_1753_mock.{md,json}`; MAPE 21.4%, total_in_expected 0.333, interval_hit 0.667, direction_ok 66.7% (dot12_check.md §8). Lưu ý: workflow cấm lệnh git nên báo cáo chưa được commit — file tồn tại trên đĩa, toàn bộ tree đang untracked trong session này | ✅ |
| Test chỉ chạy mock | test_eval_smoke.py (1 case, mock), test_eval_metrics.py (hàm thuần) — không gọi LLM thật | ✅ |

## Mục D — Nối mẫu tokai_minato → **Một phần** (implementation đạt, chạy qua API bị chặn)

| Yêu cầu | Hiện trạng | Kết luận |
|---|---|---|
| sample_service key tokai_minato, ja, JPY, giống ja_email | `_SAMPLES["tokai_minato"]` đủ: ja, JPY, 4 attachment (sample_service.py:57-73); enum `SampleIn.sample_key` đã thêm tokai_minato (schemas/api_schemas/sample.py) | ✅ |
| Chạy pipeline qua API | **BLOCKED bởi D-1**: `MC-850H_manual_excerpt.pdf` (file_type=sample_data) bị `parse_service.parse()` route vào parser Excel → lỗi → confirm chặn (dot12_check.md §9). Nguyên nhân ở parse_service (code cũ M6), mẫu mới phơi bày; eval harness chạy được vì đi đường nội bộ | ⚠️ |
| Đề xuất khắc phục | `parse_service.parse()` ưu tiên rẽ theo extension (xlsx/csv → read_sheets; pdf/docx/txt → text) trước khi xét file_type — bàn giao backend-dev | — |

## Mục G (tùy chọn "nếu kịp") — Chưa làm, đúng phạm vi

- §4b structure hint (`structure_hint_case_id`) + tín hiệu `hotspot_coverage`: chưa có trong code (grep không thấy).
- §3.5 bài học chào thầu (hiện case lost cùng hướng/thị trường): schema `bid_outcome.result` đã có để dùng sau, chưa có UI/logic hiển thị.
- Hai mục thiết kế đánh dấu tùy chọn; task ghi "làm sau cùng nếu kịp" → không phải thiếu sót.

## Mục 7 — Giao diện → **Ngoài phạm vi đợt này**

Task xác định "ĐỢT 12 = phần backend, chưa làm giao diện". Các hạng mục UI (§7) chưa làm là đúng phạm vi.

---

## Tổng hợp phát hiện

| Mức | Mô tả | Vị trí |
|---|---|---|
| **Trung bình (D-1)** | Mẫu tokai_minato không chạy pipeline qua API: PDF `sample_data` bị đưa vào parser Excel; ảnh hưởng mục D khi kiểm thực bằng API (eval harness không bị ảnh hưởng) | `parse_service.parse()` (code cũ), phơi bày bởi sample mới |
| **Thấp** | Text task ghi "case_studies_tokai.yaml (14 case)" nhưng thiết kế §3.2 ghi 6 dự án; hiện trạng 13 case (7+6) đúng thiết kế — chỉ sai số trong text task, không phải lỗi code | task / thiet_ke_danh_gia.md §3.2 |
| **Thấp** | `effort_midpoint` trong analog lấy midpoint effort engine, ví dụ §5.1 minh họa khác — thiết kế chưa định nghĩa rõ | confidence_engine.py:405-407 |
| **Thấp** | approval_service.py nén nhiều lệnh/dòng (style cũ, không phải mới) | approval_service.py:29,41,49,72 |

## Tuân thủ nguyên tắc (AGENTS.md + §2 thiết kế)

- ✅ LLM không sinh con số: confidence do code tính; WBS man-day do wbs_engine gán; không test gọi LLM thật (mock toàn bộ).
- ✅ Không hiện % giả: mức Cao/Trung bình/Thấp + lý do kiểm chứng được.
- ✅ Ít dữ liệu thì nói ít: dưới 2 case → na/insufficient.
- ✅ Dữ liệu giả lập, nhãn tiếng Việt, che PII khi import.
- ✅ 358 test backend + 16 frontend + build OK (dot12_check.md §1).

## Kết luận

Backend ĐỢT 12 **đạt yêu cầu thiết kế** ở toàn bộ mục bắt buộc. Không có lỗi chặn merge.
Cần xử lý trước khi coi mục D hoàn chỉnh qua API: **D-1** (rẽ theo extension trong
`parse_service.parse()`). Mục G tùy chọn để lại đợt sau theo đúng phạm vi.

Bàn giao bước sau: backend-dev xử lý D-1 (nếu muốn mục D chạy qua API); không có việc
khác bắt buộc.