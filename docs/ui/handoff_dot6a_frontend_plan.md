# Handoff — Đợt 6a frontend tab Kế hoạch & báo giá

Ngày: 2026-10-11  
Vai trò: senior frontend developer  
Phạm vi: chỉ tab Kế hoạch & báo giá, các mục báo giá và lịch của Đợt 6a.

## Trạng thái

**DONE — đã tích hợp giao diện, API types/client compatibility và frontend test cho phạm vi được giao.**

## Đã triển khai

- `frontend/src/components/BidPlanTab.tsx`
  - Thêm form chỉnh báo giá trước khi duyệt:
    - Giá cố định, T&M, ODC.
    - VND, JPY, USD.
    - Dự phòng `0–100%`.
    - Onsite nhập theo phần trăm hiển thị, gửi API theo tỉ lệ `0–1`.
    - Điều chỉnh giá `-50..+200%`.
    - Số tháng cho T&M/ODC và FTE cho ODC.
  - Gửi `PUT /api/bids/{id}/quotation` qua client root-relative hiện có.
  - Hiển thị trạng thái khóa khi hồ sơ đã khóa hoặc đã duyệt giá.
  - Hiển thị ngân sách, chênh lệch tuyệt đối, phần trăm chênh lệch và gợi ý điều chỉnh từ backend.
  - Hiển thị payment plan theo tháng và tổng ODC FTE-tháng.
  - Thêm form khoảng nghỉ go/no-go, mặc định 10 ngày làm việc.
  - Hiển thị ngày MVP/Production sớm nhất và ngày theo kế hoạch khách từ response.
  - Gửi `PUT /api/bids/{id}/schedule` để backend tính lại, không tự tính số liệu ở frontend.
- `frontend/src/components/GanttChart.tsx`
  - Nhận `go_no_go_start` và `go_no_go_end` từ backend.
  - Tô khoảng nghỉ go/no-go trên Gantt và thêm chú giải.
  - Không hiển thị mã task thô; dùng nhãn phase, vai trò và ngày công.
- `frontend/src/api/types.ts`
  - Bổ sung type cho model `tm`/`odc`, payment plan, ODC FTE-tháng, budget percentage/suggestion và các field schedule Đợt 6a.
- `frontend/src/lib/format.ts`
  - Đổi nhãn model sang tiếng Việt, không render raw code model.
- `frontend/src/App.test.tsx`
  - Thêm test hiển thị cấu hình ODC, ngân sách, FTE-tháng, ngày kế hoạch khách và khoảng go/no-go.
  - Cập nhật assertion Gantt theo nhãn phase nghiệp vụ.
- Trạng thái lỗi của thao tác tính lại báo giá/lịch hiển thị bằng tiếng Việt và có hướng thử lại.

## Verification

- `npm ci`: thành công theo `frontend/package-lock.json`.
- `npm run type-check`: pass.
- `npm run test -- --run`: **8 tests passed** sau khi review lại.
- `npm run build`: pass, Vite production bundle tạo thành công.
- Không gọi LLM thật và không thay đổi `LLM_PROVIDER=mock`.
- Không chạy Preview trong bước frontend và không tạo screenshot/evidence giả.

## Lưu ý cho bước tester/reviewer

- Cần kiểm tra trên Preview với mẫu Nhật các số liệu thực tế: tổng giá từng model, chênh ngân sách, ngày MVP/Production và vùng Gantt go/no-go.
- Backend response phải có `totals.payment_plan`, `totals.odc_fte_months`, `budget.difference_percent`, `budget.adjustment_suggestion_percent` và các field schedule Đợt 6a để UI hiển thị đầy đủ.
- Cảnh báo test hiện có: React Router future flag; không làm fail test/build.
- Q&A sheet, email khách, Preview walkthrough và reviewer nằm ngoài boundary của bước này.

## DONE

- Đã sửa code frontend và test trong đúng phạm vi tab Kế hoạch & báo giá.
- Đã ghi handoff note này.
- Dừng tại boundary frontend.
