# Handoff Đợt 8 — Frontend hợp nhất

## Phạm vi

- Đã hợp nhất workstream A và B/C vào frontend hiện tại.
- Chưa thực hiện tester/Preview evidence hoặc reviewer; đây là boundary của bước frontend.

## Đã triển khai

- Tab `Kế hoạch & báo giá`: staffing theo role, nút `Gợi ý theo effort`, ngày bắt đầu, buffer, lịch nghỉ, go/no-go, lưu và tính lại lịch qua backend code-only, Gantt tuần, WBS thêm/sửa/xóa và chi tiết báo giá gộp payment plan.
- Tạo hồ sơ: nhập `.txt/.md/.docx/.pdf`, giới hạn 200.000 ký tự, tiền tệ mặc định theo ngôn ngữ và ghi chú ngân sách trích từ RFP.
- Tổng quan/Danh sách: KPI câu hỏi chưa trả lời, lý do blocking, thẻ thống kê danh sách và nhãn coverage tiếng Việt.
- Giải pháp: render `risks` có loại/mức/mô tả/giảm thiểu và `feasibility_score` 1–5 theo contract backend; vẫn fallback minh bạch về field cũ.
- WBS: tên dài có truncate + tooltip, thao tác sửa/xóa dùng biểu tượng có nhãn trợ năng.
- Review bổ sung: Gantt dùng trục tuần và nhãn tên task, hiển thị marker mốc MVP/Production khách; Tổng quan có hàng KPI requirement, câu hỏi, man-day, giá, ngày kết thúc và trạng thái duyệt; Danh sách có thêm thẻ Đã gửi khi backend trả thống kê server.

## Contract assumptions

- Backend schedule hiện phân bổ theo role, chưa có phân bổ riêng theo phase; UI ghi rõ giới hạn này.
- `SolutionRisk` dùng `type_vi`, `level`, `description_vi`, `mitigation_vi`; `FeasibilityScore` dùng `score`, `reason_vi`.
- DOCX/PDF được gửi qua attachment để backend trích xuất; FE chỉ chèn trực tiếp nội dung TXT/MD.
- API frontend tiếp tục dùng root-relative paths qua `api/client.ts`.

## Verification

- `frontend`: `npm test` → **11 passed**.
- `frontend`: `npm run build` → **PASS**.
- Review regression: sau khi bổ sung KPI/Gantt/statistics, `npm test` vẫn **11 passed** và build vẫn **PASS**.
- Còn warning không blocking: React Router future flags và npm user-config warnings.

## Gaps cho bước sau

- Chưa chạy Preview/browser test trên luồng mẫu Nhật; chưa tạo `docs/ui/dot8_check.md`.
- Chưa có `docs/ui/dot8_review.md`.
- Cần tester xác minh các label, file import và thao tác schedule/WBS bằng runtime thật.
- Backend hiện chưa có thống kê danh sách toàn bộ trạng thái hoặc staffing riêng theo phase; FE không tự suy diễn các số liệu này. Thẻ `Đã gửi` hiển thị `0` khi API chưa trả `stats.sent`.
