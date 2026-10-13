# Handoff — Solution Architect: OpenRouter RFP E2E validation

Ngày: 2026-10-13  
Bước: Analyze and Freeze  
Nguồn chính: `sample_data/rfp_tokai_minato/email_yeu_cau_khach.txt`, `docs/04_architecture/llm_pipeline.md`, `docs/04_architecture/api_contract.md`, `docs/04_architecture/architecture.md`

## 1. Phạm vi đã đóng băng

Email mô tả một PoC trợ lý tri thức bảo trì thiết bị cho ba nhà máy, hai ngôn ngữ Nhật/Việt, dữ liệu tài liệu + lịch sử sự cố, SSO Entra ID, dữ liệu phải ở tenant Azure và không dùng để train model. Trong phạm vi test local/Preview, dữ liệu phải là giả lập; không sử dụng tên, số điện thoại, email hay tài liệu thật.

Bốn định dạng fixture bắt buộc theo yêu cầu người dùng, cùng CSV theo danh mục file đính kèm của email, cần được tạo dưới `sample_data/rfp_tokai_minato/fixtures/`:

| Fixture | Nội dung bắt buộc | Kiểu kiểm tra |
|---|---|---|
| `RFP_tokai_minato_poc.docx` | Mục tiêu, phạm vi PoC, người dùng, điều kiện dữ liệu, mốc hỏi đáp/nộp đề xuất/PoC; nội dung Nhật giả lập | DOCX parser + intake context |
| `request_tokai_minato.txt` | Bản text giả lập của yêu cầu khách, gồm mục tiêu, phạm vi, điều kiện, lịch và danh sách file; không phải symlink/copy thay thế cho email nguồn | TXT parser + intake context + PII masking |
| `requirements_tokai_minato.xlsx` | Ít nhất một sheet requirement, header Nhật/Anh rõ ràng, có chức năng và phi chức năng, mã dòng có thể là công thức hoặc trống | Excel sheet detection, column mapping, mã REQ duy nhất |
| `fault_history_tokai_minato.csv` | Lịch sử lỗi giả lập Nhật/Việt, cột thời gian/thiết bị/mô tả/xử lý/kết quả; không chứa PII thật | CSV parser + data profile + PII masking |
| `MC-850H_manual_excerpt.pdf` | Manual bảo trì giả lập có tiêu đề, cảnh báo an toàn, mã lỗi và quy trình kiểm tra | PDF text parser |

Email TXT gốc `sample_data/rfp_tokai_minato/email_yeu_cau_khach.txt` là context bắt buộc và phải được giữ nguyên. `request_tokai_minato.txt` là deliverable test riêng để kiểm tra đường upload/parse TXT; nội dung có thể được biên soạn từ cùng yêu cầu nhưng không được coi là fixture đã tồn tại nếu chưa tạo file vật lý.

Workflow đã được người dùng review và duyệt trước khi thực thi: `analyze-and-freeze` → `implement-fixtures-and-fixes` → `verify-parallel` (BE/FE) → `final-regression-and-real-llm`. Handoff này là deliverable của bước đầu tiên, không thay thế kết quả test hoặc fixture của các bước sau.

## 2. Testcase và acceptance criteria

### A. Input và parser

| ID | Kiểm tra | Pass khi |
|---|---|---|
| A-01 | Tạo bid từ nội dung email tiếng Nhật | HTTP 201, lưu đúng ngôn ngữ `ja`, nội dung không rỗng |
| A-02 | Upload DOCX/TXT/XLSX/CSV/PDF | Mỗi file được lưu trong attachment, loại file đoán/cho phép sửa đúng |
| A-03 | Parse toàn bộ fixture | Từng attachment `parse_status=ok`; TXT/PDF/DOCX có text; XLSX/CSV đọc được rows/sheets |
| A-04 | Requirement mapping | Có requirement sau parse XLSX, mã nội bộ duy nhất và ổn định; không ghi đè dữ liệu file khác |
| A-05 | Data profile | CSV có row count, columns, empty percentage và readiness suggestion; PII bị đánh dấu nếu fixture cố ý có trường liên hệ giả lập |
| A-06 | Parse confirmation gate | Chưa confirm thì start pipeline bị chặn; confirm hợp lệ thì bid vẫn ở draft và có thể start |
| A-07 | File safety | File type không hỗ trợ, path traversal và file vượt giới hạn bị từ chối theo error contract |

### B. LLM gateway/OpenRouter

| ID | Kiểm tra | Pass khi |
|---|---|---|
| B-01 | Chuyển provider thật | `LLM_PROVIDER=openai_compat` chọn `OpenAICompatClient`; không đọc/in giá trị API key trong log hoặc báo cáo |
| B-02 | OpenAI-compatible request | Gọi `{LLM_BASE_URL}/chat/completions`, Bearer auth, model cấu hình, system prompt có JSON Schema |
| B-03 | JSON mode compatibility | Nếu cấu hình JSON mode bật thì gửi `response_format=json_object`; nếu provider/model không hỗ trợ, lỗi phải rõ hoặc config được điều chỉnh có chủ ý, không bỏ validation |
| B-04 | Structured output | Response được parse và validate bằng Pydantic schema trước khi persist |
| B-05 | Retry bounded | Provider/schema error retry tối đa `LLM_MAX_RETRIES` (mặc định 2), sau đó step failed rõ ràng |
| B-06 | Privacy | Email/số điện thoại trong email/fixture không xuất hiện nguyên dạng trong prompt gửi provider |
| B-07 | No invented numbers | Schema/prompt/output LLM không tạo man-day, giá hoặc ngày lịch; các số chính thức do engine/bảng YAML tính |
| B-08 | Real smoke | Pipeline chạy đến trạng thái hợp lệ tiếp theo (`waiting_clarification` hoặc `waiting_tech_approval`) với step failure = 0, hoặc provider blocker được ghi chính xác |

### C. Pipeline và BE

| ID | Kiểm tra | Pass khi |
|---|---|---|
| C-01 | Intake → gap | Intake persist output; gap trả tối đa 7 câu, đúng ngôn ngữ khách và dừng nếu thiếu thông tin ảnh hưởng solution/effort/price |
| C-02 | Clarification resume | Trả lời đủ câu hỏi làm pipeline resume từ gap, không chạy lại intake |
| C-03 | Evaluation | Mỗi requirement có đúng một rating thuộc tập cố định; batch không làm mất/trùng mã |
| C-04 | Solution | Direction thuộc tập cố định; feasibility/risk định tính, không có số do LLM |
| C-05 | WBS | WBS tối đa 3 cấp, dependency không vòng, PM/QA theo phase; man-day do code tính từ weight/reference tables |
| C-06 | Proposal | Proposal đúng customer language; schema đủ section; không chứa số tiền/man-day/ngày do LLM |
| C-07 | Price gate | Chưa human price approval thì proposal/export chỉ hiển thị placeholder, không hiển thị giá thật |
| C-08 | Export | DOCX/XLSX/PDF mở được, header/content đúng, không overwrite remark/notes và giữ placeholder khi chưa duyệt |
| C-09 | Regression | Toàn bộ backend tests và quality gate hiện có pass |

### D. FE/Preview

| ID | Kiểm tra | Pass khi |
|---|---|---|
| D-01 | Create/upload UI | Form submit, chọn đủ bốn file, hiển thị attachment/status/error đúng |
| D-02 | Parse review | FE hiển thị parse result, readiness và confirm; lỗi BE hiển thị message tiếng Việt theo envelope |
| D-03 | Pipeline progress | SSE/polling cập nhật step trong giới hạn contract, reconnect không nhân đôi trạng thái |
| D-04 | Clarify/evaluation/proposal | Các màn hiển thị đúng trạng thái chờ làm rõ/duyệt; không crash với dữ liệu thiếu hoặc proposal legacy |
| D-05 | FE build/tests | Vitest pass và production build pass |
| D-06 | Runtime Preview | Browser test chạy trên Preview được; không dùng raw dev server/localhost và bằng chứng phải là runtime thật |

## 3. Vùng mã cần bước Implement/Verify kiểm tra

### Backend

- `backend/app/llm/gateway.py`: factory, protocol, bounded retry.
- `backend/app/llm/openai_compat_client.py`: endpoint, JSON mode, HTTP/error parsing, masking boundary.
- `backend/app/core/config.py`: provider/base URL/model/retry settings; không log secret.
- `backend/app/pipeline/orchestrator.py`, `backend/app/pipeline/runner.py`, `backend/app/pipeline/steps/`: persist/resume và state transition.
- `backend/app/api/routers/attachments.py`, `backend/app/services/attachment_service.py`, `backend/app/services/parse_service.py`, `backend/app/parsers/`: bốn fixture formats và partial-parse behavior.
- `backend/app/privacy/` và `backend/app/schemas/llm_schemas/`: PII/schema/no-number invariants.
- `backend/app/services/proposal_service.py`, `backend/app/services/quotation_engine.py`, `backend/app/api/routers/exports.py`: proposal legacy normalization, price gate, exports.
- `backend/tests/test_real_llm_contract.py`, `test_file_reader.py`, `test_bids.py`, `test_llm_schema_no_numbers.py`, `test_price_gate.py`, `test_export_*`, `test_m6_pipeline_integration.py` và regression tests mới.
- `backend/app/parsers/text.py`, `backend/tests/test_file_reader.py`: xác nhận TXT fixture đi qua cùng contract upload/parse và không bị bỏ qua khi parse hỗn hợp.

### Frontend

- `frontend/src/api/client.ts`, `frontend/src/api/events.ts`: root-relative API, error envelope, SSE/reconnect.
- `frontend/src/components/AttachmentUploader.tsx`, `FileParseReview.tsx`.
- `frontend/src/pages/BidNewPage.tsx`, `BidDetail*`, `ClarifySection.tsx`, `ProposalPage.tsx`, `ApprovalsPage.tsx`.
- `frontend/src/api/types.ts`: response/status/type compatibility.
- `frontend/src/App.test.tsx` và các test/build scripts trong `frontend/package.json`.

## 4. Rủi ro và quyết định kiểm thử

1. **Provider/model không hỗ trợ `response_format`**: không coi việc tắt validation là workaround. Có thể thử `LLM_RESPONSE_FORMAT_JSON=false` nếu OpenRouter model chỉ trả JSON trong content; vẫn phải parse + validate + retry.
2. **Chi phí và rate limit**: chạy real smoke với fixture nhỏ, không gửi toàn bộ dữ liệu lớn; các test CI vẫn dùng mock.
3. **LLM output không ổn định**: kết quả semantic của real LLM không nên assert bằng exact wording. Assert schema, state, invariants, no-number, requirement coverage và price gate.
4. **Clarification là trạng thái hợp lệ**: pipeline không nhất thiết đi thẳng tới approval; `waiting_clarification` là PASS nếu câu hỏi hợp lệ và không tính effort/price trước khi đủ dữ liệu.
5. **PII**: email trong file gốc là dữ liệu giả lập nhưng vẫn phải mask. Không đưa API key, `.env` hoặc raw provider headers vào artifact/handoff.
6. **Fixture không được tạo số nghiệp vụ giả từ LLM**: số trong fixture chỉ là dữ liệu đầu vào giả lập; effort/schedule/price trong output phải truy nguyên về code/reference YAML.
7. **Preview evidence**: nếu Preview/browser không khả dụng, ghi blocker chính xác; không tạo screenshot giả.

## 5. Điều kiện bàn giao

Bước Implement được coi là đủ đầu vào khi:

- fixture directory và tối thiểu năm file vật lý đã được tạo: DOCX, TXT, XLSX, CSV và PDF; trong đó DOCX/TXT/XLSX/PDF đáp ứng yêu cầu định dạng trực tiếp của người dùng, CSV đáp ứng attachment trong email;
- file nguồn `email_yeu_cau_khach.txt` vẫn nguyên vẹn và được phân biệt với `request_tokai_minato.txt`;
- mỗi bug sửa có regression test;
- không thay đổi contract kiến trúc nếu chưa có lý do và test;
- test thật của provider được tách khỏi CI/mock suite;
- report cuối có bảng A-01…D-06, lệnh kiểm chứng, kết quả, blocker và file thay đổi.

## 6. Trạng thái handoff

Phân tích và testcase matrix đã hoàn tất. Các bước implement và verification sau đó đã tạo đủ fixture vật lý tại `sample_data/rfp_tokai_minato/fixtures/`, gồm DOCX, TXT, XLSX, CSV và PDF; đã thêm regression coverage cho TXT, CSV tên tiếng Nhật và PII column `連絡先`; đồng thời đã chạy backend/frontend verification.

OpenRouter real smoke vẫn chưa đạt: backend smoke dừng trước provider request khi process không nhận `LLM_PROVIDER=openai_compat`, còn Preview dùng `openai_compat` nhưng thiếu `LLM_API_KEY` và dừng ở `intake: failed` sau bounded retries. Không có credential nào được đọc hoặc in. Vì vậy B-08/D-06 chỉ được ghi là blocker, không được đánh dấu PASS. Handoff verification chi tiết nằm tại `docs/quality/handoff_main_verification.md`.
