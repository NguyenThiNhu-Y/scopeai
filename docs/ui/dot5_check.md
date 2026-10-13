# Kiểm tra Đợt 5 — frontend

Ngày: 2026-10-11  
LLM provider: `mock`  
Phạm vi: frontend source, build và automated tests

## Automated verification

- `npm run build`: **PASS** — TypeScript compile và Vite production build thành công.
- `npm test -- --run`: **PASS — 7 tests passed** sau khi cập nhật assertion trạng thái dịch vụ và thêm regression test định dạng ngày.
- `npm run build`: **PASS** — xác nhận lại sau các chỉnh sửa cuối.
- Follow-up frontend: `npm run build` **PASS**, `npm test -- --run` **PASS — 7 tests passed**.
- Không có screenshot hoặc bằng chứng Preview giả.

## Source acceptance checklist

| Mục | Trạng thái source | Ghi chú |
|---|---|---|
| L3-01 | PASS | Ngày công hiển thị tối đa 1 chữ số thập phân. |
| L3-02 | PASS | Onsite ratio `0..1` được đổi sang phần trăm trước khi hiển thị. |
| L3-03 | PASS | Nhãn coverage map sang tiếng Việt, gồm `cần làm rõ`. |
| L3-04 | CHANGES REQUIRED | Một số nhãn đã Việt hóa, nhưng ma trận vẫn render trực tiếp `solution_direction`/`category` ở `RequirementMatrix.tsx:171`; cần map nhãn trước khi coi là PASS. |
| L3-05 | PASS source | `formatDate` xử lý cả ngày và timestamp ISO thành `dd/MM/yyyy HH:mm`; có regression test, chưa có Preview evidence. |
| L3-06 | PASS | Pipeline dùng flex-wrap. |
| L3-07 | PASS | Retry là nút phụ trong khu vực lỗi pipeline. |
| L3-08 | PASS | Feasibility/risk hiển thị dữ liệu định tính hoặc empty state nghiệp vụ. |
| L3-09 | PASS | Tổng effort overview được ghi chú và phần chi tiết nằm ở tab kế hoạch. |
| L3-10 | PASS | Gantt dùng task dates và vùng cuộn ngang theo layout hiện có. |
| L3-11 | PASS | WBS dùng component cây hiện có và điều hướng sang trình sửa. |
| L3-12 | PASS | Danh sách có tổng giá, tiền tệ, deadline và deal stage. |
| L3-13 | PASS | Settings đọc `GET /settings`, có loading/error/empty. |
| L3-14 | PASS | Không còn tên sản phẩm cũ ở màn tạo hồ sơ. |
| L3-15 | PASS | Nút tạo hồ sơ luôn có màu nhấn và trạng thái chọn. |
| L3-16 | PASS | Tên bộ mẫu phản ánh CRM. |
| L3-17 | PASS | Các literal kỹ thuật đã rà soát được thay bằng trạng thái nghiệp vụ; comments/test fixtures không phải UI. |
| L3-18 | PARTIAL | Các query phụ dùng `retry: false`; chưa có Preview console evidence xác nhận không còn 409 khi mở hồ sơ. |

## Dot 4 data surfaced

- Reliability, assumptions, excluded directions, qualitative feasibility và risks đã có type/rendering.
- Budget comparison và total quotation đã có rendering.
- Q&A export và trả lời trên màn hình đã có; chưa có control frontend để nhập lại file Q&A.
- Proposal headings theo ngôn ngữ khách hàng.
- Proposal versions đã có contract tại mục 10.0a, nhưng frontend chưa tích hợp query/control để
  liệt kê, tạo hoặc đánh dấu phiên bản; UI giữ empty state nghiệp vụ.

## Runtime limitation

Chưa chạy được walkthrough Preview đầy đủ trong bước này. Vì vậy các mục có nhãn `PARTIAL` và các
acceptance approval/export/version chưa được coi là PASS runtime.

**Kết luận: DONE cho các finding frontend tái hiện được ở source; acceptance runtime vẫn CHANGES REQUIRED vì chưa có walkthrough Preview đầy đủ.**
