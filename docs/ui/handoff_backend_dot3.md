# Handoff — Backend xử lý API gaps Đợt 3

Ngày: 2026-10-11  
Vai trò: backend-dev  
Trạng thái: **PARTIAL / FRONTEND INTEGRATION REQUIRED**

## Boundary

- Chỉ xử lý backend/API/schema/test cho các gap Đợt 3 được giao.
- Không sửa frontend, không chạy tester hoặc reviewer tổng, không tạo screenshot.
- Giữ LLM mock; không gọi LLM thật và không tạo số từ LLM.

## Đã xử lý

- `GET /api/bids/{bid_id}/exports/requirements.xlsx`
  - Thêm query nullable `note_language=vi|en|ja`.
  - Renderer dùng ngôn ngữ được chọn cho tiền tố ghi chú; không truyền query thì fallback về `bid.customer_language`.
  - Bổ sung test export theo ngôn ngữ.
- `GET /api/history`
  - Thêm query nullable `bid_id` để lọc trực tiếp audit log theo hồ sơ.
  - Bổ sung test đảm bảo không trả history của hồ sơ khác.
- `BidListItem` và `GET /api/bids`
  - Bổ sung nullable `deal_stage`, `created_at`, `total_price`, `total_price_currency`.
  - `POST /api/bids` nhận và lưu `deal_stage`.
  - `GET /api/bids` nhận filter `deal_stage`.
  - `total_price` lấy từ quotation mới nhất và `totals.grand_total`, là số đã tính bởi quotation engine.
  - Bổ sung test filter và các field list.
- `docs/ui/api_gaps.md`
  - Đánh dấu các gap export, history và deal-stage đã xử lý.
  - Ghi rõ Màn 2 chỉ xử lý được một phần: `target` chưa có field/model nguồn.
  - Ghi rõ proposal versions là contract blocker vì chưa có schema/lifecycle persisted.

## Không xử lý và lý do

- Mục tiêu hồ sơ (`target`): chưa có field/model/backend source đủ rõ; không bịa dữ liệu.
- Proposal versions gửi khách: chưa có model hoặc lifecycle contract; cần quyết định schema trước khi thêm endpoint.
- Proposal translation: chưa có contract nội dung theo ngôn ngữ; không tạo bản dịch giả.
- Q&A import/export và Question `topic`/`blocking`: chưa có contract lưu trữ và quyền xử lý file đủ rõ.

## Verification

- Original focused regression tests: **19 passed, 0 failed**:
  - `tests/test_bids.py`
  - `tests/test_audit_log.py`
  - `tests/test_requirements_parser_export.py`
- Các regression tests sau completeness review: **14 passed, 0 failed**:
  - `tests/test_approval.py`
  - `tests/test_proposal_pipeline.py`
  - `tests/test_pricing.py`
- Full backend suite ban đầu có **3 failures** ngoài các gap Đợt 3, do lỗi wiring sẵn có trong approval → quotation (`actor` bị truyền vào `onsite_percent`); lỗi đã được sửa bằng truyền rõ `by=actor`.
- `python3 -m compileall -q backend/app backend/tests`: PASS.
- Các lần gọi qua output wrapper có thể báo `Pytest: No tests collected`; không dùng thông báo wrapper làm số liệu test. Full-suite acceptance cần lấy từ lần chạy raw hoàn tất, không được suy diễn từ focused tests.
- Chưa chạy Preview trong vai trò backend-dev; browser evidence thuộc tester.

## Frontend integration required

- Màn 7 cần truyền `note_language` khi gọi export requirement.
- Màn 9 có thể truyền `bid_id` khi gọi history.
- Màn 2 cần nối `deal_stage`, `created_at`, `total_price`, `total_price_currency` và query filter `deal_stage`.
- Frontend types/client hiện chưa được thay đổi trong boundary backend này.

## Handoff status

**Backend Dot 3 complete with documented contract blockers.** Các gap có contract rõ đã được triển khai và có test; các gap không đủ nguồn/schema được giữ unavailable và ghi rõ lý do. Dừng tại boundary backend-dev.
