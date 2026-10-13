# Handoff — QA Đợt 7

Ngày: 2026-10-11  
Vai trò: QA tester  
Trạng thái: **DONE trong boundary QA; verdict CHƯA ĐẠT / BLOCKED.**

## Deliverables

- Báo cáo kiểm thử runtime: `docs/ui/dot7_check.md`.
- Đã đọc `AGENTS.md`, `docs/ui/review_luot4.md`, `docs/ui/handoff_dot6a_qa.md`, handoff backend và frontend Đợt 7.
- Đã dùng vibegraph MCP trước khi discovery code.
- Đã chạy Preview production với `LLM_PROVIDER=mock`.
- Đã kiểm tra health/frontend thật: backend API và frontend đều HTTP `200`.
- Đã nạp hồ sơ Nhật bằng `POST /api/bids/sample` với key runtime hợp lệ `ja_email`, tạo bid evidence chính `107`.
- Đã parse attachment thật: `36` requirements; `ja_rfp.docx` và `ja_requirements.xlsx` status `ok`.
- Đã xác nhận dữ liệu `high`, chạy pipeline mock và nhận trạng thái `waiting_clarification` với 5 câu hỏi vòng 1.
- Đã đọc SSE runtime thật: endpoint trả `200`, `text/event-stream`, có event `intake completed` và `gap waiting_clarification`.

## Blockers/findings

1. `GET /api/settings` trả `200` nhưng chỉ có `keys`, không có `payload`; chưa thể xác nhận settings effort/rate card/factors và CRUD runtime.
2. RFP có mốc bắt đầu/MVP/Production nhưng bid runtime trả các field mốc khách là `null`.
3. Pipeline dừng ở clarification, nên quotation/effort/schedule/proposal downstream chưa có dữ liệu hoàn chỉnh để kiểm tra P0-5, P0-7, P0-8.
4. Playwright bị Blocked vì thiếu Chromium executable. Không tạo screenshot/evidence giả; các mục UI được ghi Blocked.

## Completeness review

- `docs/ui/dot7_check.md` có ma trận cho đủ cả 9 P0 của yêu cầu gốc.
- Mỗi mục được phân loại rõ `Fail`, `Partial`, hoặc `Blocked`; không có mục nào được báo pass chỉ từ suy luận code.
- Evidence API được tách khỏi evidence UI; không dùng HTTP `200` của endpoint làm bằng chứng browser render.
- Không phát sinh deliverable QA nào khác ngoài báo cáo kiểm thử và handoff này.

## Verification

- Không sửa source code để làm test pass.
- Không chạy git command.
- Không gọi LLM thật.
- Không thực hiện vai trò reviewer.

Đã ghi báo cáo và handoff này; dừng tại boundary QA tester.
