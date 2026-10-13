# Handoff — Đợt 7 frontend P0

Ngày: 2026-10-11  
Vai trò: senior frontend developer  
Phạm vi: các mục frontend 1, 2, 4, 9 và phần giao diện của 3, 6, 8.

## Trạng thái

**DONE — đã triển khai frontend trong đúng boundary.**

## Đã triển khai

- `frontend/src/pages/BidDetailPage.tsx`
  - SSE `clarify`, `done`, `error` invalidate các query liên quan theo `bidId`, gồm bid, questions, evaluations, effort, quotation, schedule, proposal, WBS, history, attachments và danh sách hồ sơ.
  - Empty state effort sau pipeline không còn hiển thị khung đỏ khi chỉ chưa có dữ liệu.
  - Thẻ Đáp ứng map nhãn backend sang `◎`, `○`, `△`, `×`, `Cần làm rõ`, không hiện `Khác` hoặc mã thô.
  - Hiển thị mốc bắt đầu dự án nếu backend trả về.
  - Đổi hiển thị tổng effort sang `man-day`.
- `frontend/src/api/types.ts`
  - Bổ sung các mốc lịch khách vào `Bid`.
  - Đồng bộ `ProposalSections` với 8 section backend: introduction, requirements understanding, solution overview, approach, schedule, team, assumptions and scope, risks.
  - Bổ sung `payload` cho `SettingSummary`.
- `frontend/src/pages/SettingsPage.tsx`
  - Ưu tiên đọc cấu trúc `payload` từ `GET /api/settings` để bảng effort, đơn giá, hệ số hiển thị đủ dữ liệu và tiếp tục lưu qua API hiện có.
  - Ánh xạ tên hệ số sang nhãn nghiệp vụ tiếng Việt, không render mã như `customer_jp`.
  - Giữ fallback YAML cho response cũ.
- `frontend/src/pages/ProposalPage.tsx`
  - Đồng bộ đủ 8 mục proposal.
  - Tiêu đề tiếng Nhật dùng `はじめに`, `ご要件の理解`, `提案概要`, `進め方`, `スケジュール`, `体制`, `前提条件・対象外`, `リスク`.
  - Bỏ phần tiêu đề phụ giả định/ngoài phạm vi lặp bên ngoài 8 mục.
  - Bỏ nhãn lồng `Proposal & hồ sơ` ở đầu tab.
- `frontend/src/components/BidPlanTab.tsx`
  - Đổi nhãn metric từ ngày công sang `man-day`.
  - Hiển thị cảnh báo nghiệp vụ khi chênh ngân sách vượt `±30%`: kiểm tra lại phạm vi/effort.
- `frontend/src/components/GanttChart.tsx`, `frontend/src/pages/ApprovalsPage.tsx`
  - Đổi các nhãn hiển thị còn lại sang `man-day`.
- `frontend/src/pages/SchedulePage.tsx`, `frontend/src/pages/WbsPage.tsx`
  - Bỏ hiển thị cảnh báo/lưu ý so sánh lịch với hạn nộp hồ sơ.
  - Giữ hiển thị mốc MVP/Production theo kế hoạch khách.
- `frontend/src/components/ScheduleForm.tsx`
  - Nhãn trường lịch là `Ngày bắt đầu dự án`.
- `frontend/src/App.test.tsx`
  - Cập nhật smoke test để mở tab Yêu cầu & câu hỏi trước khi kiểm tra câu hỏi, phù hợp empty/tab state hiện tại.
  - Bổ sung regression cho cảnh báo budget vượt `±30%`, settings `payload`/nhãn hệ số và trường `Ngày bắt đầu dự án`.

## Verification

- `npm ci`: pass.
- `npm run test -- --run`: **11 tests passed**.
- `npm run type-check`: pass.
- `npm run build`: pass, Vite production bundle tạo thành công.
- Các lệnh test/build đã chạy trong giới hạn tối đa hai lần mỗi lệnh.
- Không gọi LLM thật; không thay đổi `LLM_PROVIDER=mock`.
- Không dùng git command.
- Không chạy Preview/browser trong bước này; không tạo screenshot hoặc evidence giả.

## Lưu ý cho tester/reviewer

- Cần kiểm tra trên Preview bằng hồ sơ mẫu Nhật: SSE sau pipeline phải làm mới solution, effort, quotation, schedule, proposal và approvals mà không F5.
- Cần xác nhận `GET /api/settings` thực tế trả `payload` đầy đủ và thao tác sửa/lưu cả ba bảng.
- Cần xác nhận proposal API thực tế trả đủ 8 section và nội dung chứa dữ liệu dossier; frontend không tự sinh số.
- Cần kiểm tra cảnh báo budget với dữ liệu lệch dưới và trên `±30%`.
- Hạn nộp hồ sơ vẫn tồn tại ở model/form/list vì đây là dữ liệu intake, nhưng không còn được dùng để so sánh hoặc cảnh báo lịch dự án ở Schedule/WBS/Detail.
- Preview/browser evidence chưa được thực hiện nên không được coi là bằng chứng hoàn tất runtime.

## DONE

- Đã hoàn tất implementation và frontend verification trong boundary.
- Đã ghi handoff note này.
- Dừng tại boundary frontend, chờ tester và reviewer của workflow.
