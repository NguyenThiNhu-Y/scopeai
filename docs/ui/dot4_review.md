# Review Đợt 4 — B3-01..B3-08 và M3-01..M3-05

Ngày review: 2026-10-11  
Vai trò: QA/tester  
Phạm vi: acceptance runtime, regression pytest, đối chiếu `AGENTS.md` và `docs/ui/review_luot3.md` mục 3.2–3.3.

## Kết luận

**CHANGES REQUIRED**

Source regression suite chạy PASS trong backend Preview container, nhưng Đợt 4 chưa đủ điều kiện PASS vì các acceptance runtime chính chưa đạt hoặc chưa có evidence.

## Đã xác nhận

- Preview chạy với `LLM_PROVIDER=mock`; không gọi LLM thật.
- Full pytest trong container backend: **PASS**, không có failure.
- Mẫu Nhật tạo thành công với HTTP 201.
- Parse workbook/RFP thành công với 36 requirement và 2 attachment `ok`.
- Confirm parse thành công khi dùng enum hợp lệ `high`.
- Pipeline bắt đầu HTTP 202 và dừng đúng trạng thái `waiting_clarification` với 5 câu vòng 1.
- Nội dung RFP có budget `1,500万円` và lịch 2027, nhưng các trường có cấu trúc trong Bid vẫn null.

## Finding bắt buộc xử lý

1. `POST /api/bids/sample` không populate `budget_amount`, `budget_currency`, `customer_schedule_start` và `customer_schedule_end` từ sample RFP. Điều này vi phạm acceptance B3-03 và làm không thể so sánh báo giá với ngân sách.
2. Runtime OpenAPI chỉ đăng ký `POST /api/bids/{bid_id}/solution`; `GET /api/bids/{bid_id}/solution` trả 405 dù source workspace có hàm GET. Cần xử lý drift giữa source và Preview image/mount trước khi đánh giá B3-01/M3-04.
3. Evaluation chưa hoàn tất (`total=36`, `evaluated=0`) vì flow dừng ở clarification; chưa chứng minh đủ `○/△/×/cần làm rõ`.
4. Chưa chứng minh vòng 2 không lặp câu vòng 1.
5. Quotation trả 409 vì chưa có WBS; chưa chứng minh tính toán và so sánh với 15,000,000 JPY.
6. Bid list trả `total_price=null` và `total_price_currency=null`; B3-04 chưa đạt runtime acceptance.
7. Q&A import/export, proposal version lifecycle, price gate và export artifacts chưa được kiểm tra end-to-end.

## Ma trận B3/M3

| Mục | Evidence hiện có | Kết luận |
|---|---|---|
| B3-01 Solution fields, feasibility, risks | Source có schema/fixture theo handoff; runtime GET solution trả 405 và pipeline chưa qua evaluation | **CHANGES REQUIRED** |
| B3-02 Quotation settings/lock | Route quotation có trong OpenAPI; chưa tới trạng thái có WBS/approval để kiểm tra tính lại và lock | **Chưa đạt acceptance** |
| B3-03 Budget và lịch khách | RFP text có dữ liệu nhưng Bid metadata null | **FAIL** |
| B3-04 Bid list total/deal stage | List route có field nhưng sample trả total price/deal stage null | **FAIL** |
| B3-05 Q&A import/export | Route/source có; chưa chạy lifecycle hợp lệ và invalid ID | **Chưa đủ evidence** |
| B3-06 Proposal versions | Chưa chạy tạo version và mark sent | **Chưa đủ evidence** |
| B3-07 Schedule warning | Có test/source evidence từ handoff; chưa có runtime acceptance trong sample flow | **Chưa đủ evidence** |
| B3-08 Proposal language/export | Chưa tới proposal/export trong runtime flow | **Chưa đủ evidence** |
| M3-01 36 requirement FR/NFR khác nhau | Source test PASS; parse runtime trả count 36 nhưng không trả rows để QA tính uniqueness | **PASS source, chưa đủ runtime evidence** |
| M3-02 Evaluation theo nội dung | Source test PASS; live evaluation chưa chạy do clarification | **PASS source, chưa đủ runtime evidence** |
| M3-03 Round 2 không lặp | Chưa hoàn tất round 1/2 | **Chưa đủ evidence** |
| M3-04 CRM direction | Runtime GET solution 405 | **FAIL** |
| M3-05 Intake budget/lịch | Mock note có context nhưng Bid fields null | **FAIL** |

## Đối chiếu luật dự án

- Rule 1: Không có bằng chứng runtime cho việc budget/lịch được code dùng làm đầu vào tính toán; không được coi là đạt chỉ dựa trên văn bản RFP.
- Rule 5: Chưa tới trạng thái duyệt giá nên không thể nghiệm thu price gate qua export thật.
- Rule 8: Automated tests PASS nhưng Preview acceptance chưa PASS; theo quy định dự án không được báo hoàn tất.
- Rule 10: Các request kiểm tra dùng root-relative `/api/...` qua Preview.

## Phạm vi không sửa

QA không sửa backend hoặc frontend, không tạo screenshot/evidence giả, và không đánh dấu PASS cho các flow chưa chạy được.
