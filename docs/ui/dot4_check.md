# Kiểm tra Đợt 4 — API mẫu Nhật và regression

Ngày kiểm tra: 2026-10-11  
Môi trường: Preview stack, `LLM_PROVIDER=mock`, không gọi LLM thật.

## Regression pytest

| Cách chạy | Kết quả | Ghi chú |
|---|---|---|
| `LLM_PROVIDER=mock rtk pytest -q` từ `backend/` trên host | **BLOCKED/không hợp lệ** | Wrapper trả `Pytest: No tests collected`, exit 1; không dùng làm kết quả acceptance. |
| `podman-compose -f podman-compose.preview.vibeflow.yaml exec -T backend python -m pytest -q` | **PASS** | Toàn bộ test được thu thập trong container chạy qua; output đạt `100%`, không có failure. Có 1 deprecation warning của Starlette/httpx. Wrapper không in tổng số test, nên báo cáo không suy đoán số lượng. |

## API smoke live

Preview được gọi qua `http://127.0.0.1:3000` trong session. Đây là runtime evidence của Preview, không phải screenshot giả.

| Kiểm tra | Kết quả | Evidence |
|---|---|---|
| Tạo mẫu `ja_email` | **PASS** | `POST /api/bids/sample` trả HTTP 201; ngôn ngữ `ja`, hồ sơ CRM giả lập, 2 attachment. |
| Parse RFP/workbook | **PASS** | `POST /api/bids/{id}/parse` trả HTTP 200; `requirements.count: 36`, 2 attachment `ok`. |
| 36 requirement có mã FR/NFR và nội dung khác nhau | **PASS một phần** | Parse trả đúng count 36; test source `test_japanese_sample_has_36_distinct_fr_nfr_requirements` nằm trong suite PASS. Endpoint parse không trả toàn bộ nội dung/mã để QA tính uniqueness độc lập trong lần smoke này; chưa đánh dấu runtime PASS tuyệt đối. |
| Confirm dữ liệu | **PASS khi dùng enum hợp lệ** | `PUT /api/bids/{id}/parse/confirm` với `data_readiness=high` trả HTTP 200. Thử nghiệm đầu tiên gửi `ready` bị HTTP 400 vì enum chỉ nhận `low/medium/high`. |
| Bắt đầu pipeline | **PASS một phần** | `POST /api/bids/{id}/pipeline/start` trả HTTP 202 và chuyển hồ sơ sang `waiting_clarification`. |
| Câu hỏi vòng 1 | **PASS** | `GET /api/bids/{id}/questions` trả 5 câu, `round_no=1`, trạng thái `awaiting_answer`. |
| Trả lời vòng 1 / vòng 2 | **BLOCKED** | Chưa thể hoàn tất acceptance vì flow đầy đủ cần tiếp tục submit câu trả lời và chờ pipeline. Không đánh dấu không-lặp câu khi chưa có dữ liệu vòng 2. |
| Rating đủ `○/△/×/cần làm rõ` | **BLOCKED** | Evaluation trả `total: 36`, `evaluated: 0` ở trạng thái chờ clarification; chưa có bằng chứng live cho phân bố rating. |
| Hướng giải pháp CRM | **FAIL** | `GET /api/bids/{id}/solution` trả HTTP 405. OpenAPI runtime chỉ đăng ký `POST /api/bids/{bid_id}/solution`, dù source hiện tại có hàm GET. |
| Budget `1,500万円` / 15,000,000 JPY | **FAIL** | Hồ sơ tạo bằng `POST /api/bids/sample` có `budget_amount: null`, `budget_currency: null`; nội dung RFP chứa `1,500万円` nhưng metadata Bid không được populate. |
| Lịch khách 2027/1–2027/9 | **FAIL** | Response tạo mẫu không có `customer_schedule_start/end`; cả hai trường không xuất hiện trong response mẫu hoặc có giá trị null trong chi tiết. |
| Intake giữ budget/lịch | **FAIL/BLOCKED** | Request content có văn bản budget/lịch Nhật, nhưng trường có cấu trúc để so sánh và tính toán vẫn null. |
| Báo giá so với budget | **BLOCKED** | `GET /api/bids/{id}/quotation` trả HTTP 409 `Chưa có WBS — chưa thể tính báo giá`; chưa thể tạo evidence so sánh budget. |
| Danh sách hồ sơ có tổng giá | **FAIL** | `GET /api/bids` trả item mẫu với `total_price: null`, `total_price_currency: null`; deal stage cũng null. |
| Q&A export/import | **CHƯA ĐỦ EVIDENCE** | Route có trong source/contract nhưng flow live chưa hoàn thành để kiểm tra persistence và invalid question ID. |
| Proposal versions | **CHƯA ĐỦ EVIDENCE** | Chưa chạy lifecycle tạo version/đánh dấu sent trên hồ sơ đã hoàn tất pipeline. |
| Price gate/export | **CHƯA ĐỦ EVIDENCE** | Chưa tới trạng thái quotation/approval nên chưa kiểm tra các format export trước/sau duyệt. |

## Runtime route discrepancy

Trong container Preview, OpenAPI thực tế liệt kê:

- `/api/bids/{bid_id}/solution`: chỉ có `POST`;
- `/api/bids/{bid_id}/quotation`: có `GET`, `PUT`;
- `/api/bids/{bid_id}/evaluations`: có `GET`.

Source workspace hiện có `GET` trong `backend/app/api/routers/solution.py`, nhưng container vẫn phục vụ OpenAPI chỉ có `POST`. Việc rebuild Preview không làm route GET xuất hiện. Đây là blocker cần chủ sở hữu bước implementation xử lý; QA không sửa source.

## Kết luận

**CHANGES REQUIRED**

Automated regression trong đúng container backend: **PASS**. Acceptance API Đợt 4: **CHANGES REQUIRED** vì các tiêu chí runtime quan trọng chưa đạt hoặc chưa thể chứng minh, cụ thể budget/lịch metadata, GET solution, evaluation completion, round 2, quotation/budget comparison, bid-list total, Q&A lifecycle và price-gate exports.
