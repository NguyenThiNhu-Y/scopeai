# Review — M3 Hướng giải pháp + effort

| Thuộc tính | Giá trị |
|---|---|
| Slice | M3 |
| Reviewer | Senior Reviewer |
| Ngày | 2026-10-10 |
| Phạm vi | Review code M3, contract, acceptance evidence và test coverage |
| Tài liệu đã đọc | `AGENTS.md`, `docs/slices/M3/spec.md`, `test_report.md`, `fix_log.md`, `handoff_to_test.md`, `handoff_to_review.md` |

## Tóm tắt

Effort engine đã tách đúng khỏi LLM, đọc bảng YAML, áp dụng factor/cap và trả trace. Enum hướng giải pháp, root-relative API, schema `extra="forbid"`, retry bounded và mock gateway phù hợp với các rule tương ứng. Tuy nhiên M3 hiện chưa thể approval vì còn các lỗi contract/security và một thiếu sót functional ở stale warning.

## Findings

### HIGH — M3-REV-001: Có thể giả mạo người thực hiện mutation

- **Vị trí:** `backend/app/api/routers/solution.py:10-12`, `backend/app/schemas/api_schemas/solution.py:8-11`, `backend/app/services/solution_service.py:18-30`
- **Vấn đề:** Endpoint nhận `by` từ JSON body và ghi trực tiếp vào `SolutionChoice.chosen_by`. Router không đọc `X-Role`/`X-User`, không kiểm tra role, và không thay thế `by` bằng danh tính từ header. Client có thể gửi `by="ai_developer"` hoặc bất kỳ chuỗi nào để tạo audit record giả.
- **Tác động:** Vi phạm contract chung §1.5 và M3 spec §2.1; audit trail không đáng tin cậy và quyền hành động có thể bị giả mạo. Đây là vấn đề integrity/authorization, không chỉ là style.
- **Cách sửa cụ thể:** Thêm dependency đọc `X-Role` và `X-User` theo cơ chế giả lập của contract; chỉ cho phép các role được phép chọn/đổi hướng, dùng `X-User` làm giá trị audit authoritative. Nếu vẫn giữ `by` để tương thích MVP, phải kiểm tra nó khớp role/user hoặc bỏ qua giá trị client-supplied. Bổ sung test request thiếu/sai header, body `by` giả mạo và assert `chosen_by` lấy từ header.

### HIGH — M3-REV-002: Mutation chọn hướng không chặn hồ sơ đã khóa

- **Vị trí:** `backend/app/services/solution_service.py:18-29`
- **Vấn đề:** Service lấy `bid` nhưng không kiểm tra `bid.locked` trước khi supersede lựa chọn cũ và insert lựa chọn mới. Contract chung §1.7 quy định mọi mutation trên hồ sơ `locked=true` phải trả `409 STATE_CONFLICT`.
- **Tác động:** Sau khi hồ sơ đã được khóa, client vẫn có thể đổi hướng giải pháp và làm thay đổi effort/audit state, phá vỡ bất biến approval/lock và có thể làm dữ liệu đã duyệt không còn nhất quán.
- **Cách sửa cụ thể:** Ngay sau `get_bid_or_404`, nếu `bid.locked` thì raise `state_conflict` với message tiếng Việt và không commit. Bổ sung regression test tạo bid, đặt `locked=true`, gọi `POST /api/bids/{id}/solution`, assert HTTP 409, envelope chuẩn, lựa chọn cũ và effort không đổi.

### HIGH — M3-REV-003: `GET /evaluations` không trả stale warning sau khi đổi hướng

- **Vị trí:** `backend/app/api/routers/evaluations.py:12-26`
- **Vấn đề:** Router luôn trả `warnings=[]`, kể cả khi đã có `SolutionChoice` cũ bị supersede. Trong khi đó `choose_solution` chỉ trả warning ở response POST; warning không được persist hoặc dựng lại ở endpoint evaluations.
- **Tác động:** UI không thể hiển thị cảnh báo đánh giá theo hướng cũ sau refresh, trái với M3 spec §2.3, §5.2 bước 6 và contract §7.2. TC-M3-005/TC-M3-004 có thể pass API persistence nhưng không chứng minh đúng behavior stale-warning end-to-end.
- **Cách sửa cụ thể:** Khi bid có lịch sử choice với `superseded_at` khác `NULL` và có current choice, dựng warning `{type: "stale_solution_direction", message: "Đánh giá requirement đang theo hướng cũ"}` trong `GET /evaluations`. Bổ sung test đổi hướng hai lần rồi gọi evaluations, assert warning xuất hiện; gọi lần đầu với một choice thì không có warning.

### MEDIUM — M3-REV-004: Heuristic factor `many_requirements` áp dụng cho mọi text có từ “requirement/yêu cầu”

- **Vị trí:** `backend/app/services/factor_engine.py:16-17`
- **Vấn đề:** Chỉ cần request chứa một từ khóa là hệ số `many_requirements` được bật; không có ngưỡng hoặc tín hiệu số lượng. Một yêu cầu đơn lẻ có thể bị nhân hệ số như nhiều requirement.
- **Tác động:** Effort có thể bị tăng sai từ customer text. Điều này đi ngược nguyên tắc “ask instead of guess” và làm kết quả deterministic nhưng không có semantics đáng tin cậy.
- **Cách sửa cụ thể:** Dùng field/context đã persist cho số lượng requirement nếu có; nếu chưa có thì không bật factor khi chỉ gặp một từ khóa. Tối thiểu cần test positive với tín hiệu nhiều requirement và negative với request đơn lẻ. Nếu chưa đủ dữ liệu, trả về câu hỏi làm rõ thay vì suy diễn.

### MEDIUM — M3-REV-005: Thiếu test API cho các rule contract quan trọng

- **Vị trí:** `backend/tests/test_solution_direction.py:9-53`, `backend/tests/test_m3_backend.py:23-47`
- **Vấn đề:** Test hiện chủ yếu validate Pydantic/schema và engine thuần; chưa có regression test cho header role/user, locked bid, stale warning qua `GET /evaluations`, lịch sử supersede qua API, và không persist khi request mutation bị từ chối.
- **Tác động:** Các lỗi M3-REV-001 đến M3-REV-003 có thể tồn tại dù `make test` và exact acceptance commands đều pass.
- **Cách sửa cụ thể:** Bổ sung API tests dùng fixture `client` cho các case trên, đồng thời kiểm tra error envelope/status code đúng contract. Không coi việc Playwright thiếu Chromium là bằng chứng thay thế cho các test API này.

## Các điểm đã xác nhận đạt

- `SolutionDirection` giới hạn đúng 5 giá trị; schema cấm field thừa bằng `extra="forbid"` tại `backend/app/schemas/llm_schemas/solution_proposal.py:18-24`.
- `run_solution` mask request trước khi đưa vào prompt và gọi gateway qua `complete_with_retry` tại `backend/app/pipeline/steps/b4_solution.py:23-25`.
- `calculate_effort` chỉ đọc reference/factor engine, không gọi LLM, và trả by-phase cùng trace tại `backend/app/services/effort_engine.py:7-26`.
- Frontend dùng API base root-relative `/api` tại `frontend/src/api/client.ts:19-24`; không thấy hardcode host trong M3 client.
- UI render effort từ backend response và hiển thị raw/capped factor trace tại `frontend/src/components/EffortBreakdown.tsx:11-25` và `frontend/src/components/EffortTracePanel.tsx:10-29`.
- `make test`, backend suite, frontend build và quality gate đã được ghi nhận PASS trong `docs/slices/M3/fix_log.md`; tuy nhiên UI Playwright vẫn blocked vì thiếu Chromium theo `test_report.md`.

## Test và evidence gap

- Các exact acceptance commands đã được sửa để collect và pass, nhưng không bao phủ authorization/lock/stale-warning.
- TC-M3-001 đến TC-M3-005 chưa chạy được trên UI vì thiếu Chromium; không được diễn giải thành UI PASS.
- Chưa có evidence cho request chứa prompt injection/customer text tác động đến direction hoặc factor; schema strict và PII masking là cần thiết nhưng chưa chứng minh đầy đủ behavior ở boundary API.

## Verdict

**CHANGES REQUIRED**

Không có CRITICAL finding, nhưng có 3 HIGH findings liên quan đến audit/authorization, lock invariant và contract stale-warning. Developer cần xử lý các finding này, bổ sung regression tests, rồi chạy lại toàn bộ acceptance commands và quality gates trước khi review lại.
