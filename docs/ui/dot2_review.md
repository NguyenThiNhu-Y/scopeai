# Đợt 2 — Review tổng Màn 3–6

## Phạm vi và nguyên tắc

Review này đối chiếu Đợt 2 với:

- `docs/ui/review_ui_tung_man.md`, mục Màn 3 Tổng quan đến Màn 6 Kế hoạch & báo giá.
- `AGENTS.md`, đặc biệt quy tắc không bịa số liệu, contract-first, LLM mock và yêu cầu Preview.
- `docs/ui/compare_03_tong_quan.md` đến `docs/ui/compare_06_ke_hoach.md`.
- `docs/ui/api_gaps.md` và các handoff frontend, tester, backend của Màn 3–6.
- Code hiện tại và quan hệ gọi qua Vibegraph MCP trước khi đọc source liên quan.

Reviewer không sửa `backend/` hoặc `frontend/`, không tạo screenshot giả và không dùng git command.

## Kết luận

# CHANGES REQUIRED

Đợt 2 chưa đủ điều kiện `PASS` hoặc approval. Các báo cáo đã làm tốt việc phân biệt API/source evidence với browser evidence và không bịa dữ liệu, nhưng còn blocker nghiệm thu bắt buộc và một số lỗi contract/integration có thể làm UI hiển thị sai.

## Findings

### F-01 — CAO: Không có bằng chứng browser/Preview cho nghiệm thu Màn 3–6

Evidence:

- `compare_03_tong_quan.md`: Chromium không khởi động được; không có DOM/screenshot.
- `compare_04_yeu_cau.md`: 9 ca `BLOCKED`, 1 ca `NOT RUN`.
- `compare_05_giai_phap.md`: acceptance runtime/visual `CHANGES REQUIRED`.
- `compare_06_ke_hoach.md`: visual verification blocked.

Ảnh hưởng: chưa thể xác nhận layout 1440×900, chữ tràn, thao tác tab/nút, loading/error state, Gantt, WBS tree và console/network. Theo `AGENTS.md`, build/test hoặc static source không thay thế được Preview evidence.

Yêu cầu đóng: chạy lại hồ sơ mẫu Nhật với `LLM_PROVIDER=mock` trong môi trường có Chromium, lưu screenshot thật nếu chạy được, assert DOM/click/network và cập nhật cả bốn compare report. Nếu môi trường vẫn không có browser, phải giữ trạng thái blocked và không tuyên bố PASS.

### F-02 — CAO: Luồng sample/pipeline không nhất quán giữa các compare report

Evidence:

- Màn 5 ghi sample pipeline start trả `409`, bid vẫn `draft`, nên `/effort` và `/quotation` không thể kiểm tra end-to-end.
- Màn 6 lại ghi hồ sơ ID `92` đã ở `waiting_tech_approval` và các endpoint quotation/schedule/WBS/effort trả `200`.
- Màn 4 ghi request có `sample_key` trả `400` và `/api/bids/83/pipeline` trả `404`.

Ảnh hưởng: không có một fixture/bid lifecycle tái lập duy nhất để chứng minh cùng một workflow Đợt 2. Người đọc không thể biết kết quả nào là cùng hồ sơ, kết quả nào là dữ liệu seed cũ, và acceptance flow có thực sự chạy từ đầu hay không.

Yêu cầu đóng: chọn một fixture hồ sơ Nhật duy nhất, ghi rõ cách tạo và trạng thái trước/sau pipeline; xác minh route pipeline chính thức và sample preview contract; chạy lại từ tạo hồ sơ đến trạng thái chờ duyệt kỹ thuật.

### F-03 — CAO: Màn 6 chưa đáp ứng hành vi WBS theo yêu cầu

Evidence từ `BidPlanTab` và `WbsTreeTable` qua Vibegraph:

- `BidPlanTab` truyền `editor={null}` và toàn bộ `onAdd/onEdit/onDelete/onSave` chỉ gọi `onEditWbs`, nên bảng trên Màn 6 là read-only preview.
- `WbsTreeTable` có khả năng render editor nhưng không được kích hoạt ở Màn 6.
- Không thấy collapse/filter phase hoặc thao tác inline edit/save chung trong Màn 6.
- `compare_06_ke_hoach.md` đánh dấu M6-09, M6-10 chưa hoàn tất.

Ảnh hưởng: không đạt yêu cầu cây WBS thu gọn, chọn phase bằng tab, sửa trực tiếp tên/man-day, thêm/xóa khi hover và lưu chung.

Yêu cầu đóng: frontend triển khai đúng hành vi trong Màn 6 hoặc cập nhật acceptance nếu sản phẩm chủ đích dẫn sang trang WBS riêng. Không được ghi PASS khi màn hiện tại chỉ là preview.

### F-04 — CAO: Thiếu ma trận phase × work-type theo contract

Evidence:

- Backend `compute_schedule` trả `work_breakdown` theo `phase × role`, cộng `total`.
- Test `test_schedule_exposes_phase_role_work_breakdown` chỉ chứng minh phase/role totals.
- `api_gaps.md` xác nhận WBS chưa có work-type độc lập.
- `compare_06_ke_hoach.md` đánh dấu M6-07 blocked.

Ảnh hưởng: phase × role không tương đương phase × work-type mà prompt yêu cầu; UI không thể hiển thị đúng ma trận nghiệp vụ.

Yêu cầu đóng: bổ sung field work-type trong WBS/contract và test, hoặc ghi rõ quyết định sản phẩm thay thế role bằng work-type. Frontend không được đổi tên nhãn để che khác biệt dữ liệu.

### F-05 — CAO: M6 chưa nối PUT quotation settings sau khi backend đã cung cấp endpoint

Evidence:

- `handoff_backend_dot2.md` ghi đã thêm `PUT /api/bids/{bid_id}/quotation` với validation model, currency, contingency và onsite.
- `BidPlanTab` qua Vibegraph chỉ gọi `getQuotation`, `getEffort`, `getSchedule`, `getWbs`; không gọi mutation PUT.
- UI còn hiển thị “Chỉ đọc vì backend chưa có API chỉnh sửa”, trái với contract hiện tại.

Ảnh hưởng: các control chọn mô hình/tiền tệ/onsite vẫn không dùng được dù backend gap tương ứng đã được xử lý.

Yêu cầu đóng: frontend nối PUT với loading/error/success state, invalidate quotation-dependent queries và test mutation. Cập nhật handoff/compare để bỏ mô tả API đã thiếu nếu đã tích hợp.

### F-06 — CAO: M6 chưa hiển thị chênh lệch ngân sách theo phần trăm và có nguy cơ sai onsite percentage

Evidence:

- Backend `quotation_to_out` trả cả `budget.difference` (số tiền) và `budget.difference_percent`; `QuotationResponse` hiện mới khai báo `difference`, còn chưa khai báo `difference_percent`.
- `BidPlanTab` chỉ render `quotation.data.budget?.difference`, nên bảng không hiển thị yêu cầu “chênh lệch %” dù backend đã tính field percentage.
- Backend `calculate_quotation` lưu onsite theo fraction `0..1` và test/compare ghi `onsite_percent=0.1`; `BidPlanTab` render trực tiếp `${quotation.data.totals.onsite_percent}%`, có nguy cơ hiển thị `0.1%` thay vì `10%`.

Ảnh hưởng: bảng so ngân sách thiếu chỉ số phần trăm bắt buộc; nếu fraction onsite được hiển thị như percentage thì số liệu báo giá nội bộ sai đơn vị.

Yêu cầu đóng: bổ sung `difference_percent` vào frontend contract và render riêng với ký hiệu `%`; xác nhận đơn vị onsite trong contract và thêm test fixture cho conversion. Không đổi hoặc suy diễn số liệu ở frontend.

### F-07 — CAO: Full backend test result không reproducible, có mâu thuẫn bằng chứng

Evidence:

- Job mới nhất báo lỗi `Pytest: No tests collected` khi chạy complete backend suite.
- `handoff_backend_dot2.md` chỉ xác nhận `tests/test_pricing.py`: 8 tests pass.
- `compare_05_giai_phap.md` lại ghi full backend suite pass với 201 tests.

Ảnh hưởng: không thể dùng “201 tests pass” làm quality gate của Đợt 2. Đây là regression/evidence risk, dù nhóm pricing đã có test mục tiêu.

Yêu cầu đóng: chạy một lệnh full suite trong đúng working directory/config, lưu output thật hoặc log đầy đủ, giải thích nguyên nhân collection failure nếu còn; cập nhật compare/handoff thống nhất. Không ghi full-suite PASS chỉ dựa trên report cũ.

### F-08 — TB: Màn 3–5 còn thiếu dữ liệu contract nâng cao

`api_gaps.md` và các compare report nhất quán về các field chưa có:

- confidence và rejected directions;
- assumptions;
- feasibility có 3 điểm và recommendation;
- risk object gồm severity/type/description/mitigation;
- question `topic` và `blocking`;
- Q&A import/export.

Đây là gap hợp lệ được ghi minh bạch, không phải lỗi do frontend tự bịa. Tuy nhiên các acceptance item tương ứng vẫn chưa đạt và phải giữ trạng thái blocked/partial cho đến khi contract và fixture có dữ liệu thật.

### F-09 — TB: Màn 6 vẫn render effort breakdown đầy đủ dù yêu cầu chỉ giữ tóm tắt

`BidPlanTab` vẫn render `EffortBreakdown` đầy đủ ngay dưới thẻ báo giá. `compare_06_ke_hoach.md` đánh dấu M6-11 chưa hoàn tất.

Yêu cầu đóng: bỏ bản đầy đủ khỏi Màn 6 hoặc chuyển thành một dòng tóm tắt có liên kết tới Màn 5; không đánh dấu hoàn tất khi còn duplicate content.

### F-10 — CAO: Thiếu deliverable kiểm tra tổng của workflow

Evidence:

- `docs/ui/review_ui_tung_man.md` mục Bước 4 yêu cầu tester chạy toàn bộ luồng hồ sơ mẫu Nhật từ Tạo hồ sơ đến duyệt giá, chụp ở `1440x900` và `1280x800`, và ghi `docs/ui/final_check.md`.
- Workspace không có `docs/ui/final_check.md` và không có `docs/ui_v3/final/` evidence.
- Các compare report từng màn đều ghi browser blocked, nhưng chưa có một biên bản tổng hợp cuối workflow để xác nhận console, network, nút không hoạt động và chữ tràn trên toàn luồng.

Ảnh hưởng: deliverable reviewer có thể kết luận `CHANGES REQUIRED`, nhưng chưa thể coi Đợt 2 đã hoàn tất đúng workflow vì thiếu artifact kiểm tra tổng bắt buộc.

Yêu cầu đóng: tester tạo `docs/ui/final_check.md` bằng kết quả chạy thật. Nếu browser tiếp tục unavailable, file phải ghi rõ từng kích thước và từng kiểm tra bị blocked, không tạo screenshot thay thế; sau đó reviewer cập nhật lại verdict.

## Những phần đã đạt hoặc có bằng chứng tốt

- Frontend build: các handoff M3–M6 ghi PASS.
- Frontend test: 1 file, 6 tests theo các handoff frontend.
- M3 đã tích hợp schedule vào card effort/kế hoạch và render yêu cầu gốc thu gọn Markdown tối giản.
- M4 giữ danh sách Q&A đã trả lời, trạng thái disabled minh bạch cho Q&A import/export và không bịa `topic`/`blocking`.
- M5 có empty state rõ hơn, progressbar semantics và nhãn risk accessible khi backend có dữ liệu.
- M6 định dạng amount theo currency backend, có các metric/bảng dùng dữ liệu response hiện có và không tự suy diễn budget/range.
- Backend có test mục tiêu pricing được handoff xác nhận `8 tests passed`, cùng test `work_breakdown` tính từ task thật.
- Không có bằng chứng screenshot giả hoặc gọi LLM thật.

## Acceptance matrix

| Phạm vi | Kết luận |
|---|---|
| Màn 3 Tổng quan | `CHANGES REQUIRED`: API gaps còn lại và chưa có browser evidence |
| Màn 4 Yêu cầu & câu hỏi | `CHANGES REQUIRED`: browser blocked, thiếu topic/blocking và Q&A import/export |
| Màn 5 Giải pháp | `CHANGES REQUIRED`: pipeline/sample runtime không tái lập, API gaps và browser blocked |
| Màn 6 Kế hoạch & báo giá | `CHANGES REQUIRED`: WBS interaction, work-type matrix, PUT integration, contract field/unit mismatch |
| Automated quality gate | `CHANGES REQUIRED`: full backend result mâu thuẫn; chỉ pricing subset được xác nhận |
| Kiểm tra tổng workflow | `CHANGES REQUIRED`: thiếu `docs/ui/final_check.md` và final evidence |

## Required follow-up

1. Chuẩn hóa fixture/sample Nhật và chạy lại pipeline end-to-end trong Preview.
2. Cung cấp browser-capable run để tạo DOM/screenshot/console/network evidence cho Màn 3–6.
3. Nối frontend với PUT quotation và sửa field/unit mismatch của budget/onsite.
4. Quyết định và triển khai WBS phase × work-type contract, hoặc phê duyệt thay đổi acceptance rõ ràng.
5. Hoàn tất Màn 6 WBS interaction và bỏ effort duplicate.
6. Re-run full backend suite từ đúng project root, ghi output thật và đồng bộ mọi report.
7. Tạo `docs/ui/final_check.md` theo Bước 4 và ghi rõ kết quả ở cả `1440x900` và `1280x800`.
8. Chỉ chuyển sang `PASS` sau khi các CAO và blocker nghiệm thu trên được đóng bằng evidence.

## Reviewer handoff note

- Deliverable: `docs/ui/dot2_review.md`.
- Role completed: reviewer tổng Đợt 2, chỉ review code/document, không sửa application source.
- Verdict: `CHANGES REQUIRED`.
- Không dùng git command.
- Không chuyển sang frontend-dev, tester hoặc backend-dev; các mục trên là follow-up cho workflow tiếp theo.
