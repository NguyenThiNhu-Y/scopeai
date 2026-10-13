# Workstream A — Kế hoạch & báo giá

## Đã thực hiện

- Overhaul `frontend/src/components/BidPlanTab.tsx` thành một flow kế hoạch compact:
  - editable staffing theo vai trò;
  - controls ngày bắt đầu, buffer, lịch nghỉ và khoảng go/no-go;
  - một nút `Lưu & tính lại lịch`, gửi `PUT /api/bids/{id}/schedule` để backend tính ngày/Gantt;
  - Gantt theo tuần thông qua `gantt_break_interval: 'week'`, có vùng go/no-go và milestone data do backend trả;
  - inline WBS editing qua `WbsTreeTable`, thêm task con và thêm nhóm cấp 1;
  - cập nhật WBS gửi `PUT /api/bids/{id}/wbs`, dùng `recalculated.schedule` nếu backend trả về;
  - payment milestones được gom vào `Chi tiết báo giá`, không còn section thanh toán riêng trong tab;
  - bỏ card effort độc lập và giữ effort/tổng trong context kế hoạch.
- `WbsTreeTable` có thêm row `＋ Thêm nhóm cấp 1`.

## Contract assumptions

- `ScheduleResponse.team_allocation` là phân bổ theo role dùng chung cho schedule; contract hiện tại không có phân bổ riêng theo phase, nên UI ghi rõ giới hạn này.
- `PUT /schedule` nhận `start_date`, `buffer_days`, `working_calendar`, `team_allocation`, `payment_milestones`, `go_no_go_gap_working_days`, `gantt_break_interval`, `by`.
- `PUT /wbs` trả `recalculated.schedule`; FE không tính effort, ngày hoặc headcount.
- Payment plan có thể dùng `totals.payment_plan`; fallback sang `payment_milestones` khi payment plan không có.

## Verification

- `npm run build` trong `frontend/`: PASS.
- `npm test`: 10/11 PASS. Test cũ `Đợt 6a` còn fail do matcher exact text `Gợi ý điều chỉnh` không match JSX label mới; không phải lỗi runtime/build. Cần chỉnh test hoặc tách label thành node riêng ở bước tích hợp tiếp theo.
