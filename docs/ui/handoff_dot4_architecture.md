# Handoff — Khảo sát kiến trúc Đợt 4

Ngày: 2026-10-11  
Vai trò: solution architect  
Trạng thái: **DONE — SCOPE READY FOR IMPLEMENTATION**

## Boundary

- Đã đọc `AGENTS.md`, `docs/ui/review_luot3.md` mục 3.2–3.3 và các handoff liên quan.
- Chỉ khảo sát kiến trúc và ghi nhận phạm vi; không sửa application code, không sửa frontend, không chạy tester/reviewer/backend.
- Không dùng git command và không gọi LLM thật.

## Bản đồ hiện trạng

### Pipeline và gateway

- Pipeline chính nằm tại `backend/app/pipeline/orchestrator.py` và `backend/app/pipeline/runner.py`.
- Các bước liên quan trực tiếp:
  - `backend/app/pipeline/steps/b1_intake.py` — intake và trích xuất bối cảnh hồ sơ.
  - `backend/app/pipeline/steps/b2_gap.py` — câu hỏi làm rõ.
  - `backend/app/pipeline/steps/b4_solution.py` — hướng giải pháp.
  - `backend/app/pipeline/steps/b6_proposal.py` — proposal.
- Gateway dùng `backend/app/llm/gateway.py`; mock dùng `backend/app/llm/mock_client.py`. Mọi thay đổi mock phải tiếp tục đi qua gateway và schema validation/retry.
- Prompt/schema liên quan nằm ở `backend/app/llm/prompts/b1_intake.py` và các schema trong `backend/app/schemas/llm_schemas/`.

### API và service

- Route chính đã có cho hồ sơ, pipeline, questions, solution, pricing, schedule, approval, proposal và exports.
- Các symbol/route được code graph xác nhận gồm:
  - `POST /api/bids/sample`, `GET /api/bids/sample/preview`.
  - `GET /api/bids/{id}/questions` và `POST /api/bids/{id}/questions/{round}/answers`.
  - `POST /api/bids/{id}/solution`, `GET /api/bids/{id}/evaluations`.
  - `GET/PUT /api/bids/{id}/schedule`, `GET /api/bids/{id}/quotation`.
  - `GET/PUT /api/bids/{id}/proposal` và các route export.
- Service tính số liệu đã tồn tại và phải được tái sử dụng:
  - `backend/app/services/pricing_service.py` / `approval_service.py` cho quotation, budget và price gate.
  - `backend/app/services/schedule_service.py` / `schedule_engine.py` cho lịch và cảnh báo.
  - `backend/app/services/sample_service.py` cho mẫu hồ sơ.
  - `backend/app/services/clarify_service.py` cho vòng hỏi.
  - `backend/app/services/proposal_service.py` và exporter cho proposal.

### Schema/model/test hiện có

- Schema solution: `backend/app/schemas/llm_schemas/solution_proposal.py` và API schema solution.
- Schema intake: `backend/app/schemas/llm_schemas/intake_extraction.py`.
- Schema proposal: `backend/app/schemas/llm_schemas/proposal.py` và `backend/app/schemas/api_schemas/proposal.py`.
- Model requirement/evaluation/question/quotation/approval/proposal đã có trong `backend/app/models/`.
- Test nền liên quan:
  - `backend/tests/test_m3_backend.py` — kiểm tra schema solution không chứa số và mock structured/retry.
  - `backend/tests/test_llm_schema_no_numbers.py` — cấm số trong output LLM/intake/gap.
  - `backend/tests/test_solution_direction.py` — hướng giải pháp và retry.
  - `backend/tests/test_clarifying_questions.py` — tối đa 2 vòng, câu hỏi và trả lời.
  - `backend/tests/test_pricing.py`, `test_approval.py`, `test_price_gate.py` — tính giá, khóa sau duyệt, placeholder trước duyệt.
  - `backend/tests/test_proposal_pipeline.py`, `test_proposal_schema.py` — proposal và cổng giá.
  - `backend/tests/test_bids.py`, `test_sample_data.py`, `test_pipeline_context.py` — API/mẫu/context.

## Phạm vi B3-01 đến B3-08

| ID | Vùng thay đổi dự kiến | Điểm cần giữ |
|---|---|---|
| B3-01 | Solution LLM schema, pipeline step, API response/evaluation | Confidence, assumptions, rejected directions, feasibility 3 điểm và risks là phân loại/giải thích; không thêm man-day/giá/ngày vào LLM schema. |
| B3-02 | Quotation schema/router/service/tests | Tùy chọn contract model/currency/contingency/onsite; recalculate bằng code; khóa mutation sau price approval. |
| B3-03 | Intake schema, b1 intake, sample RFP, quotation budget comparison | Budget/deadline có thể được trích như text/flag từ input; số dùng để tính phải do code parse/validate; không để LLM tự sinh số. |
| B3-04 | Bid list schema/router/service | Bổ sung target/deal stage/total price theo dữ liệu nguồn có thật; không bịa target. |
| B3-05 | Question/export schema/router/service/tests | Q&A export/import theo customer language, persist câu trả lời, không tạo bản dữ liệu thứ hai. |
| B3-06 | Proposal version model/schema/router/service/tests | Version lifecycle persisted, tạo/đánh dấu sent; không trộn với audit history nếu chưa có contract. |
| B3-07 | Schedule warning/service/tests | Bỏ so sánh sai giữa project end và submission deadline; so với customer milestones đã intake, hoặc trả trạng thái thiếu dữ liệu/clarify. |
| B3-08 | Proposal schema/pipeline/exporter/tests/API contract | Đủ 8 mục, tiêu đề theo `customer_language`, assumptions/scope-out 3–5 ý; số chỉ render từ code và price gate vẫn áp dụng. |

## Phạm vi M3-01 đến M3-05

| ID | Vùng thay đổi dự kiến | Điểm cần giữ |
|---|---|---|
| M3-01 | Sample fixtures dưới `backend/app` hoặc thư mục sample hiện hành, parser/tests | 36 requirement khác nội dung; mã `FR-xxx`/`NFR-xxx`; CRM thực tế: khách hàng, lịch sử, search, phân quyền, báo cáo, kế toán, Excel, performance/security/backup. Dữ liệu fictional. |
| M3-02 | Mock evaluation trong `MockLLMClient.complete`, fixture và tests | Kết quả phụ thuộc nội dung; có đủ `○`, `△`, `×`, `cần làm rõ`; note riêng từng requirement. Rating là phân loại, không phải con số do LLM. |
| M3-03 | Mock gap/questions và clarify service/tests | Vòng 2 lọc theo answer/context, không lặp question text vòng 1; vẫn giới hạn tối đa 2 vòng. |
| M3-04 | Mock solution selection và solution tests | CRM structured data → `none`/traditional ML phù hợp; lý do loại RAG/agent phải nằm ở explanation, không hardcode RAG cho mọi sample. |
| M3-05 | Sample RFP + intake mock/context/tests | Mock phải đọc nội dung hồ sơ; budget `1,500万円 税別` và lịch `2027/1–2027/9` xuất hiện trong input mẫu. Giá trị dùng tính phải được code parse/validate và có trace. |

## File chung và thứ tự triển khai

Có nguy cơ xung đột cao tại:

1. `backend/app/llm/mock_client.py` — cả B3 và M3 cần thay đổi mock.
2. Các schema LLM intake/solution/proposal.
3. Sample fixture/profile và `backend/app/services/sample_service.py`.
4. `docs/04_architecture/api_contract.md`.
5. Các test dùng chung `conftest.py` hoặc helper API.

Khuyến nghị thứ tự thực hiện dù hai backend agent được giao song song:

1. Tách thay đổi theo vùng file; M3 ưu tiên fixture/mock behavior, B3 ưu tiên API/schema/service.
2. Không để hai nhánh cùng sửa một đoạn trong `mock_client.py`; nếu bắt buộc, nhánh M3 gom behavior theo `prompt/schema/context`, nhánh B3 chỉ thêm schema/API/service.
3. Sau hai nhánh, một bước hợp nhất phải chạy compile/test và giải quyết xung đột trước tester.
4. Chỉ sau khi contract/API đã cập nhật, tester mới ghi số liệu vào `docs/ui/dot4_check.md`.
5. Reviewer kiểm tra diff cuối cùng, không review từng nhánh chưa hợp nhất.

## Rủi ro và điều kiện chặn

- **Luật 1:** mọi trường số trong intake phải là text/flag nếu thuộc output LLM; code mới được parse và dùng cho tính toán.
- **Luật 5:** quotation có thể trả số nội bộ cho presales, nhưng proposal/export customer-facing trước duyệt giá phải placeholder.
- **Không bịa target:** nếu hồ sơ mẫu không có mục tiêu riêng, API phải trả null/thiếu dữ liệu nghiệp vụ và hỏi làm rõ, không tự đặt mục tiêu.
- **Price lock:** mọi endpoint update quotation/Q&A/version/proposal phải phân biệt mutation số liệu với sửa văn bản; `locked=true` không được sửa WBS/effort/giá.
- **Contract drift:** mọi endpoint/trường mới phải được ghi đầy đủ trong `api_contract.md`, bao gồm request, response, lỗi và price gate.
- **Preview evidence:** bước tester cần gọi API thật với mock; không dùng số liệu suy diễn hoặc screenshot giả.

## Kết luận cho bước tiếp theo

Phạm vi đủ rõ để hai backend-dev triển khai B3 và M3 song song theo vùng file nêu trên. Điểm bắt buộc trước tester là hợp nhất `mock_client.py`, sample fixtures, schemas và `api_contract.md`, sau đó chạy regression test có kiểm tra luật không sinh số và price gate.

## Completeness audit against original task

| Yêu cầu đầu ra của task gốc | Trạng thái trong bước này | Deliverable hoặc bước chịu trách nhiệm |
|---|---|---|
| Đọc `AGENTS.md` và mục 3.2–3.3 của `review_luot3.md` | **Đạt** | Đã ghi trong Boundary; các luật 1, 2, 3, 4, 5, 6, 7, 8 và các mục B3/M3 đã được phản ánh. |
| B3-01 đến B3-08 | **Đã phân tích, chưa implement** | Bảng phạm vi B3-01…B3-08 ở tài liệu này; backend-dev là bước thực hiện. |
| M3-01 đến M3-05 | **Đã phân tích, chưa implement** | Bảng phạm vi M3-01…M3-05 ở tài liệu này; backend-dev là bước thực hiện. |
| Mọi con số do code tính, LLM/mock chỉ phân loại và giải thích | **Đã quy định kiến trúc** | Mục Rủi ro và điều kiện chặn; cần backend-dev thêm schema/test và tester xác minh. |
| Cập nhật `docs/04_architecture/api_contract.md` | **Chưa thực hiện trong boundary này** | Được đánh dấu là file chung và điều kiện bắt buộc trước tester; backend-dev chịu trách nhiệm cập nhật sau khi schema/API được chốt. |
| Bổ sung test backend | **Chưa thực hiện trong boundary này** | Danh sách test nền và yêu cầu regression đã được bàn giao; backend-dev bổ sung test theo từng endpoint/field. |
| Viết lại sample data 36 requirement CRM Nhật | **Chưa thực hiện trong boundary này** | M3-01 nêu rõ tiêu chí 36 mã FR/NFR, nội dung CRM và fictional data; backend-dev thực hiện. |
| Mock trả theo nội dung hồ sơ, rating đa dạng, vòng 2 không lặp, hướng CRM | **Chưa thực hiện trong boundary này** | M3-02…M3-05 nêu hành vi và test bắt buộc; backend-dev thực hiện. |
| Tester chạy pytest/API và ghi `docs/ui/dot4_check.md` | **Chưa thực hiện trong boundary này** | Tester thực hiện sau bước hợp nhất; handoff yêu cầu số liệu thật, không bằng chứng giả. |
| Reviewer ghi `docs/ui/dot4_review.md` PASS/CHANGES REQUIRED | **Chưa thực hiện trong boundary này** | Reviewer thực hiện trên diff đã hợp nhất; handoff nêu rõ các gate luật 1 và 5. |
| Không sửa giao diện | **Đạt** | Bước này chỉ tạo tài liệu trong `docs/ui/`; không thay đổi `frontend/`. |
| Giữ mock, không gọi LLM thật, không dùng git | **Đạt** | Đã ghi trong Boundary và seed/ràng buộc; bước này không gọi provider hoặc git. |

### Kết luận audit

Deliverable của vai trò solution architect **đầy đủ cho boundary khảo sát và bàn giao**, nhưng **không phải bằng chứng Đợt 4 đã hoàn thành**. Các mục “chưa thực hiện trong boundary này” là công việc bắt buộc của backend-dev/tester/reviewer trong các bước kế tiếp, không được báo cáo là PASS dựa trên tài liệu này.

**DONE — đã hoàn tất khảo sát kiến trúc và bàn giao phạm vi; dừng tại boundary solution architect.**
