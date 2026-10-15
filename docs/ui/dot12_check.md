# ĐỢT 12 — Kiểm thực trên app thật (tester)

Ngày: 2026-10-13 · Môi trường: Preview (podman-compose, LLM_PROVIDER=mock) · Người kiểm: tester

> Toàn bộ số liệu dưới đây lấy từ API của app đang chạy thật (qua proxy Preview :3000),
> không phải số liệu giả. Không tạo ảnh/bằng chứng giả.

## 1. Kết quả chạy toàn bộ test

| Hạng mục | Lệnh | Kết quả |
|---|---|---|
| Backend | `cd backend && pytest -q` | 358 passed, 0 fail |
| Frontend | `cd frontend && npm run test` | 16 passed (1 test file) |
| Build frontend | `cd frontend && npm run build` | OK (dist/assets/index-*.js ~381 kB) |

Ghi chú: lần chạy `make test` đầu tiên, frontend fail vì `vitest: not found` (node_modules
chưa cài trên host — lỗi môi trường, không phải lỗi code). Sau `npm ci`, frontend test + build
đều pass. Chi tiết ở mục 7.

## 2. Preview

- Stack: `podman-compose.preview.vibeflow.yaml` (backend python:3.11-slim :8000 + frontend node:20-alpine :3000, vite preview proxy /api → backend).
- Backend đã restart để nạp code ĐỢT 12; thêm `LLM_PROVIDER: mock` vào environment của compose (override `.env.preview` đang bật openai_compat) — health check: `{"status":"ok","llm_provider":"mock"}`.
- Frontend mở được: title "Trợ lý dự thầu" (screenshot thật: `docs/ui/dot12_preview_home.png`).

## 3. Độ tin cậy hồ sơ — GET /api/bids/144/confidence (mẫu ja_email, đã chạy pipeline hết)

Hồ sơ: **144** — 顧客管理システム（CRM）構築支援（サンプル・架空）, trạng thái `waiting_tech_approval`,
36 requirement (parse ok), đã trả lời 5 câu hỏi làm rõ vòng 1 (tiếng Nhật giả lập).

**Mức độ tin cậy: `low` (Thấp)** — `thresholds_version: 1`, `case_studies_version: 1`

`summary_vi`: "Cảnh báo: Kiểm tra WBS: Thiếu 1 kiểm tra WBS: leaf_within_limit; Truy vết requirement:
34/36 requirement có task; So với dự án tương tự: Tổng WBS 210.0 ngoài khoảng thực tế [235.0, 266.0]
(below, lệch 0.7%)"

### Từng tín hiệu (7 tín hiệu, nguyên văn)

| # | key | label_vi | status | detail_vi | data |
|---|---|---|---|---|---|
| 1 | input_completeness | Đầu vào | **pass** | Đủ 4 mục đầu vào, không còn câu hỏi chặn | has_budget=true, has_start=true, has_milestone=true, has_requirement_file=true, blocking_unanswered=0, missing_count=0 |
| 2 | wbs_checks | Kiểm tra WBS | **fail** | Thiếu 1 kiểm tra WBS: leaf_within_limit | passed=3/4: pm_qa_ok=true, within_20pct=true, cycle_free=true, **leaf_within_limit=false** |
| 3 | schedule_checks | Kiểm tra lịch | **pass** | Lịch đạt: đúng thứ tự giai đoạn, kết thúc trong mốc khách, không cảnh báo | mvp_after_go_no_go=true, production_after_mvp=true, end_within_customer=true, late_days=-189, warning=null |
| 4 | traceability | Truy vết requirement | **warn** | 34/36 requirement có task | covered=34, total=36, ratio=0.944, uncovered=["FR-019","FR-020"] |
| 5 | coverage_uncertainty | Độ chắc của đánh giá đáp ứng | **pass** | 2/36 đánh giá chưa chắc chắn (△/×/cần làm rõ) | uncertain=2, total=36, ratio=0.056 |
| 6 | analog | So với dự án tương tự | **warn** | Tổng WBS 210.0 ngoài khoảng thực tế [235.0, 266.0] (below, lệch 0.7%) | cases: 2 case (chi tiết mục 5), actual_total_range=[235.0,266.0], estimate_total=210.0, effort_midpoint=210.0, position=below |
| 7 | history_bias | Sai lệch lịch sử | **pass** | Trung vị thực tế/ước lượng 1.07 (tương đương ước lượng, 3 case cùng hướng) | direction=none, median_actual_over_estimate=1.07, case_count=3 |

**Kết luận mức**: fail 1 tín hiệu quan trọng (wbs_checks) → **Thấp** (đúng quy tắc §5.3: fail tín hiệu quan trọng → Thấp).

## 4. Truy vết requirement

- **Đã truy vết: 34/36** (ratio 0.944). WBS có 27 task, 12 task lá mang `requirement_codes`, 34 mã distinct.
- **Chưa có task (2 requirement):**

| Mã | Nội dung (tiếng Nhật) |
|---|---|
| FR-019 | 会計システムへ顧客と請求関連情報を連携するためのインタフェースを提供できること。(Cung cấp interface liên kết thông tin khách hàng & thanh toán sang hệ thống kế toán) |
| FR-020 | 販売管理システムから商品・受注情報を取り込めること。(Nhập thông tin sản phẩm/đơn hàng từ hệ thống quản lý bán hàng) |

## 5. Case tương tự (analog) — bid 144

| id | Tiêu đề | Điểm tương đồng | requirement_count | actual_total (ngày công) | actual_duration_weeks |
|---|---|---|---|---|---|
| cs_none_crm_jp | Hệ thống CRM cho công ty thương mại Nhật (giả lập) | **0.92** | 34 | 235.0 | poc 4, go_no_go 2, mvp 14, production 7 |
| cs_none_booking_jp | Hệ thống đặt lịch bảo trì thiết bị cho khách Nhật | **0.88** | 41 | 266.0 | poc 4, go_no_go 2, mvp 16, production 8 |

- **actual_total_range: [235.0, 266.0]** · **estimate_total (tổng WBS): 210.0** · **position: `below`** (ngoài khoảng, lệch 0.7%)
- **history_bias: direction `none`**, median_actual_over_estimate **1.07**, case_count **3**

## 6. Import file mẫu case study

- **GET /api/settings/case_studies/template** → tải được `cs_template.xlsx` (6 KB, sheet "Case studies", 38 cột: id…wbs_file, hàng 2 là ví dụ cs_rag_mc_manual_aichi).
- **POST /api/settings/case_studies/import** với file YAML 2 case (1 hợp lệ + 1 cố tình sai):

| mode | total | valid_count | error_count | saved | version |
|---|---|---|---|---|---|
| preview | 2 | 1 | 3 | — | — |
| save | 2 | 1 | 3 | 1 | 2 |

Lỗi theo dòng (mode=preview, nguyên văn):
- `Dòng 2: cột 'title': String should have at least 1 character`
- `Dòng 2: cột 'direction': Input should be 'none', 'traditional_ml', 'rag', 'agent' or 'fine_tune'`
- `Dòng 2: cột 'requirement_count': Input should be greater than or equal to 1`

Case hợp lệ `cs_test_import_valid` được lưu (mode=save → version 2). Sau khi save, confidence bid 144
đổi sang `case_studies_version: 2`, history_bias case_count 3 → 4 (median 1.07 → 1.05) — chứng tỏ case mới
được gộp vào tính tương đồng. Sau khi kiểm, đã khôi phục case_studies về mặc định repo (version 1, 13 case).

## 7. WBS dự án cũ — POST /api/settings/case_studies/cs_rag_mc_manual_aichi/wbs

File: `docs/eval/du_an_cu_tokai/wbs/cs_rag_mc_manual_aichi_WBS.xlsx` (18.7 KB)

- **total_rows: 81** · **total_actual: 573.0**
- **Tổng thực tế theo phase:**

| Phase | estimated | actual | task_count | Khớp actual_man_day của case? |
|---|---|---|---|---|
| poc | 82.0 | 96.0 | 17 | ✅ khớp (case: 96) |
| mvp | 300.0 | 335.0 | 43 | ✅ khớp (case: 335) |
| production | 130.0 | 142.0 | 21 | ✅ khớp (case: 142) |

- **Điểm nóng (thực tế vượt ước lượng > 30%): 7 task** (ratio 1.5–1.57):

| task_code | name_vi | phase | estimated | actual | ratio |
|---|---|---|---|---|---|
| 1.2.01 | Khảo sát tài liệu, phân loại text/scan | poc | 4.5 | 7.0 | 1.56 |
| 1.3.01 | OCR tài liệu scan | poc | 7.0 | 11.0 | 1.57 |
| 2.3.01 | OCR toàn bộ tài liệu scan (đợt 1/2) | mvp | 6.5 | 10.0 | 1.54 |
| 2.3.02 | OCR toàn bộ tài liệu scan (đợt 2/2) | mvp | 6.5 | 10.0 | 1.54 |
| 2.3.03 | Kiểm tra chất lượng OCR | mvp | 9.0 | 14.0 | 1.56 |
| 3.1.02 | Nạp dữ liệu nhà máy thứ hai (đợt 1/2) | production | 5.0 | 7.5 | 1.5 |
| 3.1.03 | Nạp dữ liệu nhà máy thứ hai (đợt 2/2) | production | 5.0 | 7.5 | 1.5 |

- **GET /api/settings/case_studies/{id}/wbs** (tải về): trả file xlsx 18.7 KB — OK.

## 8. Tóm tắt báo cáo eval mock

File mới nhất: **`docs/eval/reports/eval_20261013_1753_mock.md`** (+ `.json`)

- Provider/model: **mock / mock** (kèm chú thích "Mock chỉ kiểm tra harness, không đo chất lượng AI")
- 3 case: gc_crm_ja, gc_inventory_vi, gc_tokai_rag · 1 lần chạy/case
- **MAPE: 21.4%** · total_in_expected: 0.333 · interval_hit: 0.667 · direction_ok: 66.7%
- traceability trung bình: 64.8% · checks_pass: 73.3% · gọi LLM trung bình: 12.0 · thời gian: 0.17s

## 9. Phát hiện lỗi (defect)

**D-1 — Mẫu tokai_minato không parse được qua API (mục D của thiết kế chưa hoàn chỉnh).**
- Hiện tượng: tạo hồ sơ từ `tokai_minato` (POST /api/bids/sample) → POST /api/bids/{id}/parse →
  attachment `MC-850H_manual_excerpt.pdf` (file_type=`sample_data`) báo lỗi
  "Không đọc được Excel — hãy kiểm tra workbook và mapping cột" → PUT /parse/confirm bị chặn
  ("Cần đọc thành công tất cả file đính kèm trước khi xác nhận") → **không chạy được pipeline cho tokai_minato qua API**.
- Nguyên nhân: `parse_service.parse()` route mọi attachment `file_type=="sample_data"` vào `read_sheets`
  (Excel), không phân biệt extension; PDF bị đưa vào parser Excel. (File PDF hợp lệ, %PDF-1.3, 1.5 KB.)
- Ảnh hưởng: không thu được số liệu confidence/truy vết cho bộ RAG tokai qua API (eval harness chạy được vì
  đi đường nội bộ, bỏ qua bước confirm chặt).
- Khắc phục (đề xuất cho backend-dev): trong `parse_service.parse()`, ưu tiên rẽ theo extension —
  file xlsx/csv → `read_sheets`; pdf/docx/txt/md → text extractor — trước khi xét `file_type`.
- **Mục này ghi là KHÔNG KIỂM ĐƯỢC qua API** (chặn bởi D-1); dùng mẫu ja_email thay thế (được phép: "tokai_minato và/hoặc ja_email").

**D-2 (môi trường, không phải code)** — `make test` lần đầu fail frontend vì host chưa có node_modules
(`vitest: not found`); sau `npm ci` thì pass. `make` không có sẵn trong pod → đã cài bằng apt.

## 10. Tổng kết pass/fail

| Mục | Kết quả |
|---|---|
| Toàn bộ test backend + frontend + build | ✅ PASS (358 + 16, build OK) |
| Preview mở được, backend mock | ✅ PASS |
| GET /api/bids/{id}/confidence (7 tín hiệu + mức) | ✅ PASS — số liệu mục 3 |
| Truy vết requirement (34/36 + danh sách chưa truy vết) | ✅ PASS — mục 4 |
| Case tương tự + history_bias | ✅ PASS — mục 5 |
| Import file mẫu (template, preview, save, lỗi theo dòng) | ✅ PASS — mục 6 |
| WBS dự án cũ (upload, tổng khớp, điểm nóng, download) | ✅ PASS — mục 7 |
| Báo cáo eval mock | ✅ PASS — mục 8 |
| Confidence/truy vết cho bộ tokai_minato qua API | ❌ BLOCKED bởi D-1 (dùng ja_email thay thế) |