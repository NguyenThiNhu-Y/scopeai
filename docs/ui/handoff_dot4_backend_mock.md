# Handoff — Đợt 4 backend, mock và dữ liệu mẫu

Ngày: 2026-10-11  
Vai trò: parallel dispatch coordinator  
Trạng thái: **CHANGES REQUIRED — đã hợp nhất và sửa các finding, còn blocker acceptance live**

## Phạm vi đã nhận từ hai backend-dev

- B3-01..B3-08 đã được triển khai trong backend, gồm solution fields, quotation settings/lock,
  customer schedule, bid list fields, Q&A import/export, proposal versions, schedule warning và
  proposal contract.
- M3-01..M3-05 đã được triển khai, gồm workbook CRM Nhật 36 requirement, mock đánh giá theo nội
  dung, câu hỏi vòng 2 khác vòng 1, hướng CRM không dùng RAG mặc định và intake đọc RFP context.
- `docs/04_architecture/api_contract.md` đã có các mục contract cho solution, Q&A và proposal
  versions.
- Không sửa frontend và không gọi LLM thật.

## Việc hợp nhất đã thực hiện

- Bổ sung fixture solution `none` với `reliability_vi`, `assumptions_vi`,
  `excluded_directions` và mô tả feasibility định tính.
- Mở rộng mock evaluation để có nhánh xác định cho cả `×` và `cần làm rõ`, ngoài `◎`, `○`, `△`;
  ghi chú vẫn phụ thuộc vào nội dung requirement.
- Đổi schema feasibility từ điểm số `1..5` sang mô tả định tính; mock không còn sinh số feasibility.
- Cho phép rating `cần làm rõ` trong API response và thống kê evaluation.
- Thêm `GET /api/bids/{id}/solution` để đọc hướng giải pháp hiện tại.
- Intake dùng code để ánh xạ budget `15,000,000 JPY` và các tháng lịch explicit từ RFP vào `Bid`;
  LLM chỉ giữ ghi chú giải thích.
- Làm Q&A import trả `400 VALIDATION_ERROR` khi workbook chứa question ID không tồn tại hoặc
  không thuộc bid hiện tại, thay vì dereference `None`.
- Đồng bộ fixture mẫu Nhật với RFP: lưu ngân sách `15,000,000 JPY` (ghi trong RFP là
  `1,500万円`, chưa thuế) và lịch khách `2027-01-01` đến `2027-09-30` vào `Bid`; intake mock
  giữ nguyên thông tin này ở dạng ghi chú văn bản.
- Không thay đổi frontend, không thay đổi công thức tính effort/lịch/giá.

## Đối chiếu luật bắt buộc

- Rule 1: output LLM/mock không thêm man-day, giá hoặc ngày để dùng tính toán; feasibility là
  mô tả định tính, còn budget/schedule được code parse và số tính toán thuộc code/reference tables.
- Rule 2: các output mock vẫn đi qua schema hiện có với `extra="forbid"` và gateway retry.
- Rule 3: không tạo đường gọi LLM ngoài gateway/mock.
- Rule 4: câu hỏi vòng sau được lọc trùng và không tự đoán dữ liệu thiếu.
- Rule 5: quotation/proposal vẫn giữ price gate; proposal trước duyệt dùng placeholder.
- Rule 10: các route mới dùng root-relative `/api/...`.

## Kiểm tra đã chạy

- `python3 -m compileall -q backend/app backend/tests`: **PASS**.
- `python3 -m pytest tests/test_m3_backend.py tests/test_solution_direction.py -q` từ `backend/`:
  **9 passed**.
- Kiểm tra bằng mã nguồn đã xác nhận workbook có 36 mã và 36 nội dung khác nhau; RFP DOCX có
  ngân sách `1,500万円` và các mốc MVP/thực vận hành năm 2027.
- Hai backend-dev báo focused pytest bị blocker vì runtime thiếu package `pytest`:
  `pytest: command not found` và `python3 -m pytest: No module named pytest`.
- Chưa có `docs/ui/dot4_check.md` và `docs/ui/dot4_review.md`; đây là deliverable của tester và
  reviewer ở bước kế tiếp, không được coi là PASS dựa trên handoff này.
- Chưa có bằng chứng Preview/API thật trong bước này.

## Việc bắt buộc cho bước kế tiếp

1. Tester cần cài/khởi tạo dependency test theo môi trường dự án, chạy toàn bộ pytest và ghi số
   liệu thật vào `docs/ui/dot4_check.md`.
2. Tester phải gọi API với sample Nhật và mock để xác nhận 36 nội dung/mã duy nhất, đủ
   `○/△/×/cần làm rõ`, vòng 2 không lặp, hướng CRM, intake budget `1,500万円` và lịch
   `2027/1–2027/9`, quotation so ngân sách và bid list có tổng giá.
3. Tester cần kiểm tra riêng Q&A import với question ID sai và proposal version/quotation lock.
4. Reviewer phải đọc `AGENTS.md`, `review_luot3.md` mục 3.2–3.3 và diff cuối, sau đó ghi
   `docs/ui/dot4_review.md` với `PASS` hoặc `CHANGES REQUIRED`.
5. Nếu test phát hiện schema/API drift, sửa contract và code tối thiểu trước khi đánh giá Đợt 4.

## Đối chiếu sau tester/reviewer

- Tester đã ghi `docs/ui/dot4_check.md` với API evidence thật và kết luận `CHANGES REQUIRED`.
  Các lỗi budget mapping, solution GET và rating schema đã được xử lý ở source; cần chạy lại live
  smoke để xác nhận.
- Reviewer đã ghi `docs/ui/dot4_review.md` và phát hiện đúng hai drift chính; feasibility numeric
  và rating response đã được sửa. Các blocker quotation/evaluation completion, round-2 live flow,
  price-gate runtime evidence và bid-list total vẫn chưa có acceptance PASS.
- Rà soát bổ sung đã sửa và xác nhận 3 regression: warning lịch, đường dẫn workbook fixture và
  tính đa dạng note evaluation; cả 3 case đều pass sau sửa.
- Không sửa `frontend/` và không gọi LLM thật.

**HANDOFF — coordinator complete. Đợt 4 vẫn chưa PASS do các mục Preview/price-gate/quotation
chưa được chạy lại sau source fixes; không có bằng chứng giả.**
