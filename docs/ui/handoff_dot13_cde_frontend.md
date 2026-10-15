# HANDOFF NOTE — ĐỢT 13 · Bước frontend-dev (C, D, E)

## Đã làm

### C. Quy trình & phê duyệt (`frontend/src/pages/ApprovalsPage.tsx`)
- **Không duplicate**: `getConfidence` (node AB đã thêm) và `signalStatusMeta` (AB đã tạo trong `lib/format.ts`) — dùng lại trực tiếp.
- `client.ts`: thêm `getApprovals(id)` → GET /bids/{id}/approvals; `types.ts`: thêm `ApprovalRecord`/`ApprovalsResponse` (snapshot chứa confidence + case_studies_version + confidence_thresholds_version, §5.5).
- Section "Duyệt kỹ thuật": hiện **đủ 7 tín hiệu** (confidence.signals) — biểu tượng ✓/⚠/✕/– theo tone pass/warn/fail/na (qua `signalStatusMeta`), nhãn tiếng Việt + `detail_vi`; kèm mức độ tin cậy hiện tại + phiên bản ngưỡng/case study.
- **KHÓA NÚT**: `confidence.level === 'low'` → nút "Duyệt kỹ thuật" disabled tới khi `techComment.trim().length >= 10`; hiện gợi ý "Độ tin cậy ở mức Thấp — cần nhận xét tối thiểu 10 ký tự để duyệt kỹ thuật." (Backend cũng chặn — UI làm trước).
- **MỨC ĐÃ LƯU LÚC DUYỆT**: từ `getApprovals`, tìm item `kind='tech' status='approved'` → hiện "Đã duyệt khi mức độ tin cậy: {snapshot.confidence.level_label_vi}" + "Case study v{n}" + "Ngưỡng v{n}" nếu có.

### D. Cài đặt (`frontend/src/pages/SettingsPage.tsx`)
**D1. Tab "Case study"** — thay `CaseStudiesEditor` cũ (3 trường) bằng:
- Bảng danh sách: tên, hướng (SOLUTION_LABELS), thị trường (MARKET_LABELS), số requirement, tổng thực tế (= Σ actual_man_day, `formatManDay`), cờ công khai, nút "Sửa".
- Đếm số case theo hướng giải pháp (vd "Không dùng AI: 7 · Tra cứu theo tài liệu: 6").
- Form sửa đủ trường §3.2: id, title, industry, market, customer_language, direction, requirement_count, year, public, summary, estimated/actual_man_day{poc,mvp,production}, actual_duration_weeks{poc,go_no_go,mvp,production}, team_peak{pm,ba,brse,ai_engineer,backend,frontend,qa,infra}, factors, lessons_vi, tech, bid_outcome{result,bid_month,contract_model{poc,mvp,production},win/lost_reason_vi}, wbs_file. Dữ liệu = payload từ GET /settings — không bịa. Lưu qua `updateSetting('case_studies', JSON.stringify(...))` như cơ chế cũ.
- Nút "Tải file mẫu": `downloadCaseStudiesTemplate()` (blob + `URL.createObjectURL`, pattern như ExportPage).
- Nút "Nhập từ file": chọn .xlsx/.csv/.yaml → `importCaseStudies(file,'preview')` → bước XEM TRƯỚC: "X dòng hợp lệ · Y lỗi (tổng Z dòng)", danh sách lỗi theo dòng (chuỗi "Dòng 2: cột 'title': ..."), danh sách dòng hợp lệ; nút "Lưu" → `importCaseStudies(file,'save')` → thông báo "Đã nhập N case · phiên bản vX" + refetch settings. (Bỏ nút "+ Thêm case study" cũ — schema mới bắt buộc nhiều trường, thêm tay sẽ chặn lưu; nhập file là cơ chế thêm.)
**D2. Tab "Ngưỡng độ tin cậy"** (key `'confidence'`): thêm vào mảng SETTINGS; editor textarea YAML (khởi tạo từ `JSON.stringify(payload, null, 2)` — JSON hợp lệ cũng là YAML hợp lệ), lưu qua `updateSetting('confidence', <text gốc>)`, backend validate; header hiện version.

### E. Tab "Đánh giá hệ thống" (`eval_report` — pseudo-tab, không phải settings key)
- `getEvalReportLatest()` → GET /api/eval/reports/latest; 404 → "Chưa có báo cáo đánh giá hệ thống."
- Hiện: provider/model, started_at, tổng seconds, repeat (nếu > 1); bảng tổng hợp (MAPE, total_in_expected_rate, interval_hit_rate, direction_ok_pct, avg_traceability_pct, checks_pass_pct, avg_llm_calls, avg_seconds — rate nhân 100 thành %); bảng từng case đủ 12 chỉ số §6.2 (direction_ok, total_ape, total_in_expected, interval_hit, phase_share_error, traceability_pct, must_trace_ok, checks_pass, duration_weeks_error, confidence_level → Thấp/Trung bình/Cao, llm_calls, seconds). Ghi chú "Mock chỉ kiểm tra harness, không đo chất lượng AI" khi provider=mock.
- Sửa trong review: bổ sung 3 cột còn thiếu của bảng từng case (Sai lệch tỉ trọng / Bắt buộc truy vết / Sai lệch tuần); SelectField thêm option "— Chọn —" cho select tùy chọn (bid_outcome.result); thông báo sau import save nêu rõ "N dòng lỗi bị bỏ qua" nếu có.

### F. Test frontend (thêm vào `App.test.tsx`, mock thêm getApprovals/getEffort/getEvaluations/getHistory/getBidQualification/listProposalVersions/importCaseStudies/getEvalReportLatest)
1. **Import lỗi theo dòng**: mock `importCaseStudies` trả preview errors `['Dòng 2: cột ...']` → render SettingsPage → assert "Dòng 2:" + "1 dòng hợp lệ · 1 lỗi" + tên dòng hợp lệ.
2. **Khóa nút duyệt khi mức Thấp**: mock getConfidence level='low' → nút "Duyệt kỹ thuật" disabled khi comment < 10 ký tự, enabled khi ≥ 10; assert đủ 7 tín hiệu hiển thị.
3. (Bonus) **Mức đã lưu lúc duyệt**: mock getApprovals có bản ghi tech approved → assert "Đã duyệt khi mức độ tin cậy: Trung bình" + phiên bản.

## Kiểm chứng (Done means proven)
- `cd frontend && npm run test` → **PASS (28) FAIL (0)** — chạy 2 lần liên tiếp ổn định (trước: 25 test; thêm 3).
- `cd frontend && npm run build` (tsc -b && vite build) → **OK** (exit 0, 0 lỗi TS).
- Không đụng file của node AB: BidDetailPage.tsx, BidPlanTab.tsx, WbsTreeTable.tsx không sửa. client.ts/types.ts/format.ts/App.test.tsx chỉ THÊM.
- Sửa nhỏ cho ổn định: test M4 WbsPage dùng `findByDisplayValue` thay `getByDisplayValue` (WbsTreeTable nạp draft qua useEffect — getByDisplayValue dễ race khi worker tải nặng; chạy 2 lần liên tiếp đều pass).

## Lưu ý cho bước sau (tester)
- Luồng mẫu Nhật/Tokai: mức độ tin cậy hiển thị trên Tổng quan (thẻ A), Kế hoạch (analog B1 + truy vết B2), Duyệt kỹ thuật (đủ 7 tín hiệu C). Muốn tạo tình huống mức Thấp: xóa task QA một giai đoạn → wbs_checks fail → mức Thấp → nút duyệt bị khóa tới khi nhận xét ≥ 10 ký tự.
- Import case study: Cài đặt › Case study › "Nhập từ file" → xem trước (lỗi theo dòng) → "Lưu" → version mới; confidence sẽ đổi `case_studies_version`.
- Tab "Đánh giá hệ thống" hiện báo cáo `docs/eval/reports/eval_20261013_1753_mock.json` (provider=mock, 3 case) khi backend chạy từ repo root.
- Backend groundwork (358 tests) không bị đụng tới trong bước này.