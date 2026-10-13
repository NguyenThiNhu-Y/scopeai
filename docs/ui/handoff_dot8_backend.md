# Handoff — Đợt 8 backend

Ngày: 2026-10-11  
Vai trò: backend-dev  
Phạm vi: API nhân sự/lịch, vòng hỏi 2, mock Giải pháp

## Trạng thái

**DONE — đã triển khai backend contract và regression tests.**

## Đã triển khai

- `PUT /api/bids/{id}/schedule` nhận `phase_team_allocation` theo `poc/mvp/production`; headcount theo giai đoạn được dùng bởi schedule engine để tính lại duration/end date bằng code, không gọi LLM. `GET` trả lại allocation theo giai đoạn.
- Schema và ORM schedule đã lưu allocation theo giai đoạn; validation chặn phase/role lạ và headcount âm.
- `QuestionsOut` có `round_two_reason_vi`; chỉ có giá trị khi có câu hỏi vòng 2 đang chờ trả lời. B2 ghi `blocking_reason_vi` vào output khi vòng 2 thực sự phát sinh.
- Mock GapQuestions không sinh vòng 2 nếu các câu trả lời trước đều là xác nhận “như dự kiến”/tương đương; các trường hợp còn thông tin chặn vẫn tạo vòng 2 theo logic hiện hữu.
- SolutionProposal có rủi ro có cấu trúc (`type_vi`, `level` 1–5, `description_vi`, `mitigation_vi`) và `feasibility_score` 1–5 với lý do. Fixture RAG có 4 rủi ro mẫu và điểm khả thi; dữ liệu được lưu/trả qua solution API.
- Fixture SolutionProposal được bổ sung mặc định 4 rủi ro và điểm khả thi ngay cả với các biến thể mock `none`, `traditional_ml`, `agent`, `fine_tune`; fixture sinh theo ngữ cảnh cũng đi qua cùng chuẩn hóa.

## Files chính đã sửa

- `backend/app/schemas/api_schemas/schedule.py`
- `backend/app/models/schedule.py`
- `backend/app/services/schedule_engine.py`
- `backend/app/services/schedule_service.py`
- `backend/app/schemas/api_schemas/question.py`
- `backend/app/services/clarify_service.py`
- `backend/app/api/routers/questions.py`
- `backend/app/pipeline/steps/b2_gap.py`
- `backend/app/schemas/llm_schemas/solution_proposal.py`
- `backend/app/schemas/api_schemas/solution.py`
- `backend/app/models/solution_choice.py`
- `backend/app/services/solution_service.py`
- `backend/app/api/routers/solution.py`
- `backend/app/pipeline/steps/b4_solution.py`
- `backend/app/llm/mock_client.py`
- `backend/tests/test_schedule_update.py`
- `backend/tests/test_m3_backend.py`
- `backend/tests/test_clarifying_questions.py`

## Verification

- `python3 -m pytest -q tests/test_schedule_update.py tests/test_clarifying_questions.py tests/test_m3_backend.py tests/test_solution_direction.py` trong `backend/`: **38 passed**.
- `python3 -m pytest -q` trong `backend/`: **toàn bộ backend tests pass**.
- `python3 -m compileall -q backend/app backend/tests/test_schedule_update.py`: pass.
- `make test` không chạy được vì môi trường hiện tại không có lệnh `make`; lệnh pytest toàn repo qua wrapper báo “No tests collected”, nên đã chạy pytest trực tiếp từ thư mục `backend` cho các suite liên quan.
- Chưa chạy Preview/browser; tester Đợt 8 cần kiểm tra runtime và bằng chứng thật.

## Lưu ý cho frontend

- Allocation tổng vẫn dùng `team_allocation`; `phase_team_allocation` là override tùy chọn theo phase. Nếu phase/role không có override, engine fallback về allocation tổng.
- `SolutionCurrentOut.risks` có thể chứa dữ liệu risk object từ mock hoặc dữ liệu risk cũ dạng chuỗi; frontend nên render tương thích cả hai dạng trong giai đoạn chuyển tiếp.
- `feasibility_score` có thể vắng ở các bản ghi solution cũ; không hiển thị điểm giả khi field không có.
- Không có migration riêng vì dự án dùng `Base.metadata.create_all()` cho database runtime/test.
- `phase_team_allocation` là nullable để database SQLite cũ được nâng schema an toàn; API coi giá trị thiếu là mapping rỗng và fallback về allocation tổng.

## DONE

Đã tự review boundary backend, ghi handoff này và dừng tại boundary backend.
