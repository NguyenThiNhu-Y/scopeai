# Review — M2 Phân tích yêu cầu + hỏi làm rõ

| Thuộc tính | Giá trị |
|---|---|
| Vai trò | Reviewer (code + document review) |
| Ngày | 2026-10-09 |
| Phạm vi | Toàn bộ code M2 (backend + frontend) + spec/test_report/fix_log |
| Nguồn | `AGENTS.md`, `docs/slices/M2/spec.md`, `docs/slices/M2/test_report.md`, `docs/slices/M2/fix_log.md`, `docs/04_architecture/api_contract.md` (§3, §5, §6) |
| Ghi chú | Repo chỉ track `.gitignore` (không có commit milestone trước) → review trực tiếp trên code hiện tại, không có diff |

---

## 1. Kết luận

**Verdict: CHANGES REQUIRED** — có **1 finding HIGH** (lỗi trạng thái máy — làm hỏng dữ liệu hồ sơ, đã tái hiện được). Không có CRITICAL. Các quy tắc AGENTS.md 1–10 và contract M2 nhìn chung được tuân thủ tốt (29/29 test PASS, quality gate PASSED).

---

## 2. Findings theo mức độ

### 🔴 HIGH

#### H-1. `submit_answers` không kiểm tra trạng thái hồ sơ → làm hỏng bid vĩnh viễn
- **File:** `backend/app/services/clarify_service.py:104-158` (đặc biệt dòng 130-135 bỏ qua kiểm tra, 155-158 commit `bid.status="analyzing"`).
- **Vấn đề:** `submit_answers` không xác minh `bid.status == "waiting_clarification"` và không yêu cầu có câu hỏi đang chờ (`awaiting` rỗng). Với `{"answers": []}` trên bid **draft** (hoặc `waiting_tech_approval`), `missing` = ∅ → vượt kiểm tra → `bid.status = "analyzing"` được **commit** → sau đó router gọi `resume(...)` mới fail (422 "Bước 'gap' chưa từng được đăng ký").
- **Hậu quả (đã tái hiện live):** bid 67 `draft` → `analyzing` vĩnh viễn, **không pipeline chạy, không bước failed để rerun** — hồ sơ kẹt cứng, UI hiển thị "Đang phân tích…" và disable nút Phân tích mãi mãi. Vi phạm máy trạng thái (data_model §18).
- **Cách sửa (đề xuất cho Developer):**
  1. Đầu `submit_answers`: nếu `bid.status != "waiting_clarification"` → `validation_error("Hồ sơ không ở trạng thái chờ làm rõ")`.
  2. Nếu `awaiting` rỗng → `validation_error("Không có câu hỏi chờ trả lời")`.
  3. Chỉ commit `bid.status="analyzing"` **sau khi** toàn bộ validate (thiếu câu, thuộc vòng) đã qua — hoặc chuyển commit sang cuối hàm.
  4. Thêm test: `POST /questions/1/answers` với `{"answers":[]}` trên bid draft → 400, trạng thái giữ nguyên `draft`.

### 🟠 MEDIUM

#### M-1. Ngoại lệ không phải `LLMSchemaError` → bước kẹt `running`, bid kẹt `analyzing` vĩnh viễn
- **File:** `backend/app/pipeline/orchestrator.py:70-87` (`except Exception` nuốt mọi lỗi) + `backend/app/pipeline/steps/b1_intake.py:53-57` / `b2_gap.py:116-120` (chỉ bắt `LLMSchemaError`).
- **Vấn đề:** `complete_with_retry` chỉ bắt `ValidationError`/`JSONDecodeError` (`gateway.py:67`); `LLMProviderError` (mạng/timeout/provider trả sai) **không được retry, không được đánh dấu failed** → bay lên `run()` → log rồi im lặng. Bước ở `running`, bid ở `analyzing`; `rerun` tìm bước `failed` → không thấy → 422, không recovery được.
- **Cách sửa:** trong `run()`, bắt ngoại lệ chung, xác định bước đang chạy (hoặc bước kế tiếp) và `mark_failed` + `publish_error` trước khi log; hoặc mở rộng `except` ở từng bước. Thêm test mock client raise `LLMProviderError` → bước `failed` + bid quay về trạng thái có thể rerun.

#### M-2. `_finalize` dùng `assert bid is not None`
- **File:** `backend/app/pipeline/orchestrator.py:93-94`.
- **Vấn đề:** `assert` bị vô hiệu khi chạy `python -O`; nếu bid bị xóa giữa chừng → `AttributeError` mơ hồ thay vì lỗi rõ. Đổi thành `if bid is None: raise ...` (hoặc dùng `get_bid_or_404`).

#### M-3. Trả lời khi pipeline vẫn đang chạy: answers đã lưu nhưng trả 409
- **File:** `backend/app/api/routers/questions.py:51-68` + `clarify_service.py:104-158`.
- **Vấn đề:** `submit_answers` commit answers + `bid=analyzing` **trước** khi `resume` kiểm tra `is_running` → nếu pipeline vẫn chạy (race hiếm), client nhận 409 nhưng answers đã lưu; lần thử lại sẽ dính `missing_ids`/`Câu hỏi không thuộc vòng này` mơ hồ. Cùng gốc với H-1: cần kiểm tra trạng thái/đăng ký task trước khi mutate.

#### M-4. SSE: không giới hạn số subscriber/bid
- **File:** `backend/app/pipeline/sse.py:36,77-99`.
- **Vấn đề:** client API có thể mở vô hạn kết nối SSE tới 1 bid → tích queue trong bộ nhớ (mỗi queue 256 msg). Trình duyệt giới hạn ~6/domain nhưng client không-phải-trình-duyệt thì không. Đề xuất: cap subscriber/bid (vd 10) hoặc cap tổng.

### 🟡 LOW

#### L-1. `request_content` toàn khoảng trắng lọt qua min_length
- **File:** `backend/app/schemas/api_schemas/bid.py` (min_length=30) + `bid_service.create_bid` (`request_content` không `.strip()` như `project_name`).
- **Vấn đề:** `" " * 30` đạt `min_length` → LLM nhận nội dung rỗng. FE đã `.trim()` trước khi gửi nhưng API trực tiếp thì không. Sửa: strip + kiểm tra độ dài sau strip (hoặc validator `min_length` trên giá trị stripped).

#### L-2. LIKE wildcard trong tìm kiếm `q`
- **File:** `backend/app/services/bid_service.py:63-67`.
- **Vấn đề:** `%`/`_` trong `q` không được escape → tìm `%` trả toàn bộ. Không nghiêm trọng (chỉ ảnh hưởng kết quả tìm kiếm), nhưng nên escape hoặc dùng `contains(..., autoescape=True)`.

#### L-3. Trùng helper `get_db_session` trong router pipeline
- **File:** `backend/app/api/routers/pipeline.py:20-21` — trùng `app/api/deps.py::get_db`. Dùng chung dependency.

#### L-4. UX: nút "Phân tích" không disabled trong lúc câu hỏi đang tải
- **File:** `frontend/src/pages/BidDetailPage.tsx:99` (`hasUnanswered` đọc `questionsQuery.data` khi query còn disabled/loading → `false`).
- **Vấn đề:** trên bid `waiting_clarification`, trong khoảng khắc câu hỏi chưa load xong, nút "Phân tích" không bị disable → bấm được → backend trả 409 CLARIFY_PENDING (không hỏng dữ liệu, chỉ UX). Có thể chấp nhận; nếu muốn chặt: disable khi `isWaitingClarification && questionsQuery.isLoading`.

---

## 3. Tuân thủ AGENTS.md 1–10 (đã kiểm tra)

| Rule | Kết quả | Bằng chứng |
|---|---|---|
| 1. No invented numbers | ✅ | Schema LLM `extra="forbid"`, không trường man-day/giá/ngày; `test_llm_schema_no_numbers.py`; prompt dặn BR-01 |
| 2. Structured output + retry ≤ 2 | ✅ | `complete_with_retry` (gateway.py:47-79); `test_retry_bad_schema_then_fail` (3 lần gọi) |
| 3. One LLM gateway, test không gọi LLM thật | ✅ | `LLMClient` Protocol; conftest ép `LLM_PROVIDER=mock`; mock ghi `call_count`; test `test_no_http_request_in_tests` |
| 4. Ask instead of guess | ✅ | `waiting_clarification` dừng pipeline; vòng ≤ 2; vòng 2 không gọi LLM (`test_round_two_no_llm_call`); `missing_ids` |
| 6. Privacy | ✅ | Mask tại gateway + `b1_intake`; `test_pii_mask.py` ≥ 50 mẫu; `OpenAICompatClient` không log key; mẫu giả lập hư cấu |
| 7. Languages | ✅ | Câu hỏi theo `customer_language`, `reason_vi` tiếng Việt; UI/lỗi tiếng Việt |
| 8. Done means proven | ✅ | `make test` exit 0; 29/29 acceptance PASS; Preview chạy được |
| 9. Keep it simple | ✅ | SSE in-process asyncio queue, không broker/WebSocket |
| 10. Frontend networking | ✅ | `API_BASE='/api'` root-relative; quality gate grep BR-10 PASSED |

## 4. Contract conformance

- 9 endpoint M2 đúng path/method theo spec §2.1; envelope lỗi `{error:{code,message,details}}` đúng §1.3.
- `details.min_length=30` cho `request_content` ngắn — đúng spec §2.1.
- `409 STATE_CONFLICT` / `409 CLARIFY_PENDING` / `422 PIPELINE_ERROR` — đúng; race 409 đã phủ bởi unit test (SlowMockClient).
- `pipeline_progress` shape khớp làm rõ §2.1.
- **Ngoại lệ:** `POST /answers` với body rỗng/không hợp lệ phá máy trạng thái (H-1) — contract §6.2 không nói rõ nhưng vi phạm data_model §18.

## 5. Chất lượng chung

- Code sạch, có docstring tiếng Việt, tách lớp rõ (router → service → pipeline → llm), test phủ tốt (56 backend + 4 frontend).
- Dead code: `get_db_session` trùng (L-3); `SampleOut`/`PipelineStartOut`… được dùng đủ. Không phát hiện code chết đáng kể.
- Bảo mật input: XSS/SQLi đã test (React escape + SQLAlchemy parameter binding); prompt injection từ nội dung khách chỉ ảnh hưởng output LLM (đã validate schema + retry) — chấp nhận được ở M2.

---

## Verdict

**CHANGES REQUIRED** — cần sửa **H-1** (guard trạng thái trong `submit_answers` + test hồi quy) trước khi merge. M-1 nên sửa cùng lượt vì cùng gốc "lỗi không phải schema làm kẹt pipeline". Các mục còn lại (M-2..M-4, L-1..L-4) có thể gom vào một lượt fix nhỏ hoặc để milestone sau.

Đề nghị: nhờ Developer trong chat áp dụng các fix (H-1, M-1) và chạy lại `make test` + kịch bản Preview, hoặc chạy lại workflow cho cùng milestone M2.