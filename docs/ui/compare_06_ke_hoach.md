# So sánh Màn 6 — Kế hoạch & báo giá

Ngày audit: 2026-10-11  
Phạm vi: QA trên Preview sau workflow Màn 6  
Hồ sơ: mẫu tiếng Nhật, `LLM_PROVIDER=mock`, viewport yêu cầu `1440x900`

## Kết luận

**CHANGES REQUIRED / chưa đủ bằng chứng visual.** Preview backend/frontend chạy được. Các API Màn 6 trả dữ liệu thật cho hồ sơ Nhật đã ở trạng thái `waiting_tech_approval`, gồm JPY, mốc thanh toán, schedule và WBS. Chromium không có executable trong môi trường nên không thể chụp screenshot hoặc assert DOM ở `1440x900`; không tạo screenshot giả. Pipeline/sample cũng không được coi là PASS khi API trả lỗi hoặc hồ sơ chưa đủ dữ liệu.

## Ma trận yêu cầu

| ID | Yêu cầu gốc | Evidence hiện tại | Mức | Đã sửa | Trạng thái |
|---|---|---|---|---|---|
| M6-01 | Chọn mô hình Trọn gói/T&M/ODC và tiền tệ VND/JPY/USD | `QuotationResponse` chỉ có `contract_model`, `currency`; không có endpoint cập nhật hai giá trị | CAO | Không | BLOCKED — API gap |
| M6-02 | Bốn ô số: tổng kèm khoảng, dự phòng, ngày công, onsite | `BidPlanTab.tsx` đã có bốn ô; tổng/dự phòng/ngày công lấy từ response; quotation ID `92` trả `onsite_percent=0.1` nhưng không có endpoint chỉnh sửa | CAO | Có | PARTIAL — thiếu range và onsite editable do contract |
| M6-03 | Bảng so ngân sách gồm phạm vi, ngân sách, giá, chênh lệch % | Đã thêm bảng ngân sách; quotation ID `92` trả `budget=null`, nên không có phạm vi/ngân sách/chênh lệch để hiển thị; không suy diễn từ tổng giá | CAO | Có | PARTIAL — thiếu budget contract/data |
| M6-04 | Bảng theo giai đoạn gồm ngày công, chi phí, khoảng | Đã render chi phí theo giai đoạn từ `totals.by_phase`; endpoint effort có khoảng tổng hợp theo phase nhưng quotation/schedule chưa trả object phase gồm ngày công, chi phí và khoảng | CAO | Có | PARTIAL — API gap |
| M6-05 | Mốc thanh toán | API `/api/bids/92/quotation` và `/schedule` trả 4 mốc, tổng tỷ lệ 100%; `PaymentMilestonesView` hiển thị tên, %, ngày đến hạn backend tính | TB | Có | API PASS; visual BLOCKED — thiếu Chromium |
| M6-06 | Chi tiết theo vai trò thu gọn | API quotation trả `totals.by_role` cho 7 vai trò; `details` và bảng vai trò đã có, amount dùng đúng `quotation.currency` | TB | Có | API/source PASS; visual BLOCKED — thiếu Chromium |
| M6-07 | Ma trận giai đoạn × loại công việc, có tổng | Không có field/API loại công việc trong response hiện tại | CAO | Không | BLOCKED — API gap |
| M6-08 | Form tham số lịch gọn, Gantt hiển thị ngay | API `/api/bids/92/schedule` trả `start_date`, `team_allocation`, `tasks` có phase/start/end; `ScheduleForm` và `GanttChart` tồn tại | TB | Không | API PASS; visual BLOCKED — thiếu Chromium |
| M6-09 | WBS cây thu gọn, chọn giai đoạn bằng tab | WBS tree hiện có, nhưng chưa có collapse/filter phase trong tab Màn 6 | TB | Không | Chưa hoàn tất |
| M6-10 | Sửa tên/man-day trực tiếp, thêm/xóa khi hover, lưu chung | Chỉnh sửa hiện mở `WbsPage`; bảng Màn 6 là preview read-only với nút chuyển trang | CAO | Không | Chưa hoàn tất trong scope source hiện tại |
| M6-11 | Bỏ thẻ effort trùng, giữ một dòng tóm tắt | Màn 6 vẫn render `EffortBreakdown` đầy đủ | TB | Không | Chưa hoàn tất |
| M6-12 | Loading/rỗng/lỗi và không bịa dữ liệu | Có trạng thái loading/error/empty; field thiếu hiển thị hướng dẫn hoặc `Backend chưa cung cấp` | TB | Có | Đã xử lý ở frontend; chưa xác minh browser |

## Kết quả Preview/API

- Preview stack: backend và frontend đều `Up`; frontend phục vụ qua cổng preview nội bộ `3000` và proxy `/api` hoạt động.
- `GET /api/health`: HTTP `200`.
- `GET /api/bids?page=1&page_size=10`: HTTP `200`; danh sách có hồ sơ mẫu Nhật hư cấu và các hồ sơ đã chạy pipeline.
- `GET /api/bids/sample/preview`: HTTP `200`.
- Hồ sơ Nhật đã chạy tới duyệt kỹ thuật, ID `92`: `quotation`, `schedule`, `wbs`, `effort` đều HTTP `200`.
- Quotation ID `92`: `currency=JPY`, `contract_model=fixed_price`, tổng `grand_total=8,085,806`, `onsite_percent=0.1`, 4 mốc thanh toán, 7 vai trò; `budget=null`.
- Schedule ID `92`: có ngày bắt đầu `2026-10-26`, phân bổ đội ngũ và task WBS theo phase.
- WBS ID `92`: có cây task PoC/MVP/Production.
- Effort ID `92`: có các hệ số và min/max theo phase.
- Hồ sơ draft mới ID `94`: các API `quotation/schedule/wbs/effort` trả HTTP `409` vì pipeline chưa chạy; không dùng hồ sơ này để đánh giá màn đã có dữ liệu.
- Browser: Playwright không khởi động được vì thiếu Chromium executable; không có screenshot hoặc DOM evidence.

## Kiểm tra kỹ thuật

- Đã sửa lỗi định dạng tiền: mọi amount trong `BidPlanTab.tsx` dùng `quotation.currency`, thay vì mặc định VND.
- Đã bổ sung bốn metric, bảng ngân sách và bảng theo giai đoạn từ dữ liệu API có thật.
- Không tự tính giá, effort, lịch, khoảng hoặc chênh lệch phần trăm khi backend chưa trả field tương ứng.
- `WbsTreeTable` tại Màn 6 vẫn là bản xem trước; thao tác thật nằm ở `WbsPage` và không được giả lập là inline edit.

## Blocker

- Chưa có bằng chứng screenshot/DOM ở `1440x900` nếu Chromium không khả dụng.
- Contract chưa hỗ trợ cập nhật mô hình/tiền tệ hoặc onsite; quotation chưa có budget, ma trận loại công việc, và object phase đầy đủ gồm ngày công/chi phí/khoảng.
- Cần backend bổ sung contract trước khi đánh dấu các mục API-dependent là PASS.
