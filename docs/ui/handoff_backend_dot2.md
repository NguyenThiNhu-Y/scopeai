# Handoff — Backend xử lý API gaps Đợt 2

Ngày: 2026-10-11  
Vai trò: backend-dev  
Trạng thái: **PARTIAL / FRONTEND INTEGRATION REQUIRED**

## Đã sửa

- `backend/app/api/routers/quotation.py`
  - Thêm `PUT /api/bids/{bid_id}/quotation`.
  - Validate contract model (`fixed_price`, `tm`, `odc`), currency (`VND`, `JPY`, `USD`), contingency và onsite percentage.
  - Tính lại báo giá bằng quotation engine, không gọi LLM.
- `backend/app/schemas/api_schemas/quotation.py`
  - Thêm schema `QuotationSettingsIn`.
- `backend/app/models/quotation.py`
  - Lưu `onsite_percent` trong quotation snapshot.
- `backend/app/services/quotation_engine.py`
  - Trả `totals.phase_man_days`.
  - Trả `budget.scope` và `budget.difference_percent` khi hồ sơ có ngân sách.
  - Giữ `budget=null` khi hồ sơ không có ngân sách; không tính chênh lệch giả.
- `backend/app/schemas/api_schemas/schedule.py`
  - Thêm `work_breakdown`.
- `backend/app/services/schedule_engine.py` và `schedule_service.py`
  - Trả ma trận phase × role và total, tính từ task WBS thật.
- `backend/tests/test_pricing.py`
  - Bổ sung test phase man-day, budget percentage, cập nhật quotation settings, validation và work breakdown.
- `docs/ui/api_gaps.md`
  - Cập nhật trạng thái các gap đã xử lý và ghi rõ gap còn phụ thuộc frontend/contract.

## Chưa xử lý

- Điểm khả thi, confidence, hướng bị loại, assumptions và risk object cần mở rộng schema/pipeline B4; hiện chưa có nguồn persisted data đủ để trả an toàn.
- Question `topic`/`blocking` và Q&A import/export chưa có contract/backend flow.
- Work-type matrix hiện được cung cấp theo role vì WBS chưa có work-type độc lập.
- Frontend cần nối PUT quotation settings và đọc các field mới.

## Verification

- `python3 -m pytest -q tests/test_pricing.py`: PASS, 8 tests.
- Regression test mới cho `work_breakdown` kiểm tra đủ phase và tổng phase được tính từ role rows.
- Lần chạy qua output wrapper báo sai `No tests collected`; đã chạy lại raw theo quy tắc dự án.
- Test validation dùng HTTP 400 theo error contract của ứng dụng, không dùng 422 mặc định của FastAPI.
- Chưa chạy Preview trong vai trò backend-dev; browser evidence thuộc tester.

## Workflow boundary

Chỉ xử lý backend API/contract gaps của Màn 3–6. Không sửa frontend, không thực hiện tester hoặc reviewer tổng. Dừng tại handoff này.
