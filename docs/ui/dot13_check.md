# ĐỢT 13 — Kiểm thực trên app thật (tester)

Ngày: 2026-10-14 · Môi trường: Preview (podman-compose, LLM_PROVIDER=mock) · Người kiểm: tester

> Toàn bộ số liệu dưới đây lấy từ API + giao diện của app đang chạy thật (qua proxy Preview :3000),
> không phải số liệu giả. Screenshot thật: `docs/ui/dot13_*.png`. Không tạo ảnh/bằng chứng giả.

## 1. Kết quả chạy toàn bộ test

| Hạng mục | Lệnh | Kết quả |
|---|---|---|
| Backend | `cd backend && pytest -q` | **358 passed, 0 fail** (exit 0) |
| Frontend | `cd frontend && npm run test` | **28 passed** (2 test files) |
| Build frontend | `cd frontend && npm run build` | OK (0 lỗi TS) |

## 2. Preview

- Stack: `podman-compose.preview.vibeflow.yaml` — backend python:3.11-slim :8000 (không publish cổng) + frontend node:20-alpine :3000 (vite preview, proxy `/api` → backend). Rebuild toàn bộ với code Đợt 13 (fingerprint thay đổi).
- `LLM_PROVIDER: mock` (override trong compose environment). Health: `{"status":"ok","app":"presales-bidding-assistant","llm_provider":"mock","database":"ok"}`.
- Frontend mở được: title "Trợ lý dự thầu".
- **Sửa preview**: mount thêm `./docs:/app/docs:ro` cho backend (xem defect D-13-1) để `GET /api/eval/reports/latest` tìm thấy báo cáo.

## 3. Mức độ tin cậy hiển thị — bid 144 (mẫu ja_email)

Hồ sơ **144** — 顧客管理システム（CRM）構築支援（サンプル・架空）, 36 requirement, đã chạy pipeline hết.
Trạng thái đầu: `waiting_tech_approval` (sau khi kiểm khóa duyệt → `waiting_price_approval`, mục 6).

**GET /api/bids/144/confidence**: `level: low (Thấp)`, `thresholds_version: 1`, `case_studies_version: 1`, đủ 7 tín hiệu (giống Đợt 12: wbs_checks fail leaf_within_limit, traceability warn 34/36, analog warn below).

### Thẻ Tổng quan (screenshot `dot13_overview.png`) — ✅ khớp API
- Huy hiệu **Thấp**; đúng 3 lý do (fail trước warn): ✕ "Kiểm tra WBS: Thiếu 1 kiểm tra WBS: leaf_within_limit", ⚠ "Truy vết requirement: 34/36 requirement có task", ⚠ "So với dự án tương tự: Tổng WBS 210.0 ngoài khoảng thực tế [235.0, 266.0]".
- Link "Xem chi tiết ›" → chuyển sang tab **Kế hoạch & báo giá** (kiểm thực: click → khối analog hiện ra).

### Khối "So với dự án tương tự" (screenshot `dot13_plan_analog.png`) — ✅ khớp API analog.cases

| Cột hiển thị | Case 1 (cs_none_crm_jp) | Case 2 (cs_none_booking_jp) |
|---|---|---|
| Tên | Hệ thống CRM cho công ty thương mại Nhật (giả lập) | Hệ thống đặt lịch bảo trì thiết bị cho khách Nhật (giả lập) |
| Hướng | Không dùng AI (= none) | Không dùng AI |
| Thị trường | Nhật Bản (= jp) | Nhật Bản |
| Req | 34 | 41 |
| PoC / MVP / Production | 31 / 142 / 62 | 35 / 160 / 71 |
| Tổng | 235 | 266 |
| Tuần | PoC 4, go_no_go 2, MVP 14, Production 7 | PoC 4, go_no_go 2, MVP 16, Production 8 |

- Thanh so sánh từng giai đoạn (ước lượng vs khoảng thực tế): **PoC ƯL 33 · TT 31–35 · MVP ƯL 120 · TT 142–160 · Production ƯL 57 · TT 62–71** — thể hiện vị trí `below` (ước lượng dưới khoảng thực tế).
- Dòng "Sai lệch lịch sử: thực tế tương đương ước lượng (3 dự án cùng hướng)" — khớp `history_bias {direction: none, median: 1.07, case_count: 3}` (nhãn tiếng Việt, không hiện số thô).
- Trạng thái "Chưa đủ dữ liệu tham chiếu" (position=insufficient) không xảy ra với bid 144 (2 case) — được phủ bởi unit test frontend (AnalogCompare).

## 4. Truy vết requirement (tab Kế hoạch) — ✅

- Dòng **"Truy vết: 34/36 requirement có task"** + "Requirement chưa có task:" kèm **FR-019, FR-020** (nội dung tiếng Nhật đầy đủ) — khớp API `traceability {covered: 34, total: 36, uncovered: [FR-019, FR-020]}`.
- Cột **Requirement** trong bảng WBS: 27 chip mã (FR-/NFR-); **hover hiện nội dung requirement** (title attr, ví dụ chip NFR-001 → "通常利用時の顧客検索が実用的な応答時間で完了すること。").
- **Bấm requirement chưa có task (FR-019)** → chuyển `?tab=coverage` (tab Đáp ứng yêu cầu) — đúng thiết kế.

## 5. Import file mẫu case study (Cài đặt › Case study) — ✅

- **Tải file mẫu**: tải được `cs_template.xlsx` (6.187 bytes).
- **Nhập từ file (preview, file 2 dòng: 1 hợp lệ + 1 cố tình sai)** → "Xem trước: **1 dòng hợp lệ · 7 lỗi** (tổng 2 dòng)" + danh sách lỗi theo dòng nguyên văn:
  - `Dòng 2: cột 'title': String should have at least 1 character`
  - `Dòng 2: cột 'industry': Field required` · `'market': Field required` · `'customer_language': Field required`
  - `Dòng 2: cột 'direction': Input should be 'none', 'traditional_ml', 'rag', 'agent' or 'fine_tune'`
  - `Dòng 2: cột 'requirement_count': Input should be greater than or equal to 1` · `'summary': Field required`
  - + danh sách dòng hợp lệ ("Case hợp lệ Đợt 13 (giả lập)"), nút Lưu/Hủy.
- **Lưu (file 1 case hợp lệ)** → "Đã nhập 1 case · phiên bản 2." → API xác nhận `case_studies` source=db, version 2, **14 case** (13 + 1 test); bid 144 confidence đổi `case_studies_version` 1 → **2**. (history_bias vẫn 3 case vì case test hướng rag ≠ none của bid — đúng.)
- **Đã khôi phục** case_studies về repo default (version 1, 13 case) sau kiểm thực.
- Bảng danh sách case: TÊN/HƯỚNG/THỊ TRƯỜNG/REQ/TỔNG THỰC TẾ/CÔNG KHAI/SỬA — đủ 13 case; case thua thầu (không có actual_man_day) hiện tổng **"—"** (đúng).
- Đếm theo hướng: "Không dùng AI: 3 · Học máy truyền thống: 1 · Tra cứu theo tài liệu: 7 · Trợ lý nhiều bước: 2 · Tinh chỉnh mô hình: 0" (tổng 13).

## 6. Khóa duyệt khi mức Thấp — ✅ (tạo tình huống bằng cách xóa task QA)

**Tạo tình huống**: PUT /bids/144/wbs remove task QA `WBS-002-01-04` (Kiểm thử MVP) →
- `wbs_checks` fail **2 cờ: pm_qa_ok, leaf_within_limit** (trước: 1 cờ) — `pm_qa_ok: false`.
- `traceability` 34/36 → **32/36** (task mang NFR-002, NFR-008); `analog` Tổng WBS 210 → 192 (lệch 9.2%).
- Mức vẫn **Thấp** (đúng quy tắc §5.3).

**Kiểm UI (screenshot `dot13_approvals.png`)**: hiện đủ **7 tín hiệu** với biểu tượng ✓/✕/⚠ + nhãn tiếng Việt + detail_vi; "Độ tin cậy ước lượng: Thấp · Ngưỡng v1 · Case study v1"; gợi ý "Độ tin cậy ở mức Thấp — cần nhận xét tối thiểu 10 ký tự để duyệt kỹ thuật.".

**Khóa nút**: nút "Duyệt kỹ thuật" **disabled** khi mức Thấp; nhập comment "ngắn" (< 10 ký tự) → vẫn disabled; nhập "Đã rà soát WBS, chấp nhận rủi ro độ tin cậy" (≥ 10) → **enabled**.

**Duyệt + mức đã lưu (screenshot `dot13_after_approve.png`)**: bấm Duyệt kỹ thuật → hồ sơ chuyển `waiting_price_approval`; UI hiện "**Đã duyệt khi mức độ tin cậy: Thấp · Case study v1 · Ngưỡng v1**" + "Đã duyệt bởi ai_developer · 14/10/2026 12:06". GET /bids/144/approvals:
`{id: 5, kind: tech, status: approved, approver: ai_developer, reason: "Đã rà soát WBS, chấp nhận rủi ro độ tin cậy", snapshot: {confidence.level_label_vi: "Thấp", case_studies_version: 1, confidence_thresholds_version: 1}}` — khớp UI.

**Khôi phục**: thêm lại task QA (man_day 10 = max API) → `pm_qa_ok` pass, traceability về 34/36, mức Thấp (leaf_within_limit như gốc). Lưu ý nhỏ: tổng WBS 202 (gốc 210) vì API sửa chặn man_day > 10 (xem D-13-2).

## 7. Cài đặt › Ngưỡng độ tin cậy — ✅

- Tab mở, textarea YAML (JSON hợp lệ = YAML hợp lệ) chứa đủ cấu trúc `confidence.yaml`: `thresholds` (traceability, coverage_uncertainty, schedule, input_completeness, wbs_checks.required_flags), `level_rules` (important_signals, min_fail_for_low, min_warn_for_medium, max_summary_reasons), `similarity` (min_score, max_cases, weights).
- Lưu thay đổi → "Đã lưu Ngưỡng độ tin cậy · phiên bản 2." + header "ĐÃ CHỈNH SỬA · V2" (API: source=db, version 2). **Đã khôi phục** về repo (version 1).

## 8. Cài đặt › Đánh giá hệ thống — ✅ (screenshot `dot13_eval_tab.png`)

- GET /api/eval/reports/latest → báo cáo `eval_20261013_1753_mock.json` (provider **mock**, model mock, started_at 2026-10-13 17:53:16, tổng thời gian **1.81s**).
- Ghi chú "Mock chỉ kiểm tra harness, không đo chất lượng AI.".
- Bảng tổng hợp (8 chỉ số): MAPE **21.4** · Tỉ lệ tổng nằm trong khoảng đáp án **33%** · Tỉ lệ khoảng chạm đáp án **67%** · Hướng giải pháp đúng **66.7** · Truy vết trung bình **64.8** · Kiểm tra đạt **73.3** · Số lần gọi LLM trung bình **12** · Thời gian trung bình **0.17s**.
- Bảng từng case **đủ 12 cột** (§6.2): CASE/HƯỚNG ĐÚNG/APE TỔNG/TRONG KHOẢNG/KHOẢNG CHẠM/SAI LỆCH TỈ TRỌNG/TRUY VẾT/BẮT BUỘC TRUY VẾT/KIỂM TRA ĐẠT/SAI LỆCH TUẦN/ĐỘ TIN CẬY/LLM CALLS/GIÂY:
  - gc_crm_ja: ✓ · 14.3% · ✕ · ✓ · 0.033 · 94.4% · ✓ · 80% · 19.3 tuần · Thấp · 6 · 0.18
  - gc_inventory_vi: ✓ · 2.8% · ✓ · ✓ · 0.026 · 0% · ✓ · 80% · 12.6 tuần · Thấp · 12 · 0.07
  - gc_tokai_rag: ✕ · 47.2% · ✕ · ✕ · 0 · 100% · ✓ · 60% · 2.4 tuần · Thấp · 18 · 0.27
- **Trường hợp 404** (tạm di chuyển file json ra khỏi `docs/eval/reports/` → GET /api/eval/reports/latest trả 404): UI hiện đúng **"Chưa có báo cáo đánh giá hệ thống."** (screenshot `dot13_eval_404.png`). Đã khôi phục file, tab trở lại hiển thị báo cáo bình thường.

## 9. Mẫu tokai_minato — ❌ BLOCKED (D-1 kế thừa Đợt 12)

- Tạo hồ sơ 145 (設備保全ナレッジAIアシスタント構築（PoC）（サンプル・架空）) → POST /parse → attachment `MC-850H_manual_excerpt.pdf` báo "Không đọc được Excel — hãy kiểm tra workbook và mapping cột" → PUT /parse/confirm bị chặn "Cần đọc thành công tất cả file đính kèm trước khi xác nhận".
- **D-1 chưa được sửa** (PDF file_type=sample_data vẫn bị route vào parser Excel). Dùng mẫu ja_email (bid 144) thay thế — được phép theo task.

## 10. Phát hiện lỗi (defect)

| Mã | Mức | Mô tả | Vị trí |
|---|---|---|---|
| **D-13-1** | Thấp | `GET /api/eval/reports/latest` resolve `Path("docs/eval/reports")` theo **CWD** → 404 khi backend chạy từ `backend/` (hoặc container `/app`) dù báo cáo tồn tại. Preview đã workaround bằng mount `./docs:/app/docs:ro`. Đề xuất: resolve từ `__file__` (như `report.py` đang làm). | `settings.py:25` |
| **D-13-2** | Thấp | `WbsTaskIn.man_day le=10` không thể tái tạo man_day pipeline > 10 (task QA gốc 18.0) khi sửa/khôi phục qua API → tổng WBS lệch nhỏ (202 vs 210). Ràng buộc có trước Đợt 13, không phải regression. | `api_schemas/wbs.py` |
| **D-1** | Trung bình (kế thừa) | tokai_minato không chạy pipeline qua API (PDF bị đưa vào parser Excel) — chưa sửa từ Đợt 12. | `parse_service.parse()` |

## 11. Tổng kết pass/fail

| Mục | Kết quả |
|---|---|
| Toàn bộ test backend + frontend + build | ✅ PASS (358 + 28, build OK) |
| Preview mở được, backend mock | ✅ PASS |
| Thẻ độ tin cậy Tổng quan (huy hiệu + ≤ 3 lý do + Xem chi tiết) | ✅ PASS — mục 3 |
| Khối "So với dự án tương tự" khớp API (case, hướng, thị trường, req, effort, tổng, tuần, thanh so sánh, sai lệch lịch sử) | ✅ PASS — mục 3 |
| Truy vết 34/36 + cột Requirement (chip, hover) + bấm sang tab Đáp ứng | ✅ PASS — mục 4 |
| Import file mẫu (tải template, preview lỗi theo dòng, save → version) | ✅ PASS — mục 5 |
| Khóa duyệt mức Thấp (xóa task QA → fail → khóa → ≥ 10 ký tự → duyệt) + 7 tín hiệu + mức đã lưu | ✅ PASS — mục 6 |
| Tab Ngưỡng độ tin cậy (sửa + lưu version) | ✅ PASS — mục 7 |
| Tab Đánh giá hệ thống (tổng hợp + từng case, provider, thời gian) | ✅ PASS — mục 8 |
| Mẫu tokai_minato qua API | ❌ BLOCKED bởi D-1 (dùng ja_email thay thế) |