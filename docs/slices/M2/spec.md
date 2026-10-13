# Slice Spec — M2 Phân tích yêu cầu + hỏi làm rõ

| Thuộc tính | Giá trị |
|---|---|
| Tên tài liệu | Đặc tả milestone M2 — Phân tích yêu cầu + hỏi làm rõ (slice spec) |
| Phiên bản | 1.0 |
| Ngày | 2026-10-09 |
| Trạng thái | Sẵn sàng cho bước Build |
| Vai trò | Solution Architect |
| Nguồn | `AGENTS.md`, `docs/05_roadmap/roadmap.md` (§4 M2), `docs/04_architecture/` (architecture.md, api_contract.md, data_model.md, llm_pipeline.md), `docs/04_architecture/handoff_to_dev.md`, `docs/03_requirements/srs.md` (FR-001, FR-006*, FR-007, FR-010, FR-011, FR-023, NFR-001/002/004/009), `docs/slices/M1/spec.md` + `docs/slices/M1/handoff_to_build.md` |
| Ghi chú | Yêu cầu milestone M2 (prompt workflow) bổ sung 3 điểm so với roadmap: (1) `request_content` tối thiểu **30 ký tự**; (2) AI bước 1 trích xuất **7 nhóm thông tin** (mục tiêu, người dùng, dữ liệu, ràng buộc, ngân sách, thời hạn, ngôn ngữ khách); (3) **2 mẫu yêu cầu giả lập** để bấm thử. Đã ghi nhận vào `api_contract.md` (§3.1, §3.7, §12) và `llm_pipeline.md` (§2, §3) — xem §2.2. |

---

## 1. Phạm vi (Scope)

### 1.1 Milestone này giao những gì

M2 là **vertical slice nghiệp vụ đầu tiên** (roadmap §4): presales tạo hồ sơ → dán email/RFP → AI phân tích → **dừng hỏi ≤ 7 câu** khi thiếu thông tin → trả lời trên web → pipeline **resume từ điểm dừng** → tiến độ từng bước **realtime (SSE)**; có **danh sách hồ sơ + mở lại hồ sơ** ở mọi trạng thái. Cụ thể:

1. **Tạo hồ sơ (FR-001):** form đầy đủ (tên dự án, khách hàng, hạn nộp, ngôn ngữ khách vi/en/ja, nội dung yêu cầu bắt buộc **≥ 30 ký tự** — yêu cầu milestone), ngân sách tùy chọn; hồ sơ mới ở trạng thái `draft`; lỗi validate trả `400 VALIDATION_ERROR` tiếng Việt.
2. **Danh sách + mở lại hồ sơ (FR-007):** `GET /api/bids` lọc theo `status`, tìm theo `q` (tên dự án/khách hàng), phân trang; `GET /api/bids/{id}` trả chi tiết kèm `pipeline_progress` để UI khôi phục màn hình; mở lại hồ sơ "Chờ làm rõ" hiển thị câu hỏi chưa trả lời (FR-007.2).
3. **Pipeline M2 (FR-023):** orchestrator đăng ký đủ **7 bước** (contract §5.1) nhưng **chỉ triển khai 2 bước**:
   - **B1 Intake** — AI bước 1: trích xuất cấu trúc 7 nhóm thông tin (mục tiêu, người dùng, dữ liệu, ràng buộc, ngân sách, thời hạn, ngôn ngữ khách) theo schema `IntakeExtraction` (đã cập nhật `llm_pipeline.md` §2), retry ≤ 2, persist ngay.
   - **B2 Gap** — AI bước 2: liệt kê thông tin thiếu + **tối đa 7 câu hỏi** làm rõ (nội dung bằng **ngôn ngữ khách**, lý do bằng **tiếng Việt**, mức ảnh hưởng solution/effort/price); **câu hỏi chặn = mọi câu hỏi được sinh ra** → pipeline dừng ở `waiting_clarification` chờ presales trả lời (FR-010.3); tối đa **2 vòng** (FR-010.4), sau vòng 2 code **không gọi LLM nữa** mà bắt buộc trả lời theo giả định.
   - 5 bước còn lại (`evaluate`, `solution`, `wbs`, `proposal`, `ja_check`) tạo dòng `pending` kèm ghi chú "chưa triển khai ở M2" — kích hoạt ở M3/M4/M6/M7.
4. **Hỏi làm rõ (FR-010, FR-011):** `GET /api/bids/{id}/questions` (kèm `rounds_used`, `max_rounds=2`); `POST /api/bids/{id}/questions/{round}/answers` — trả lời thiếu → `400 VALIDATION_ERROR` kèm `details.missing_ids`; trả lời giả định → `is_assumption=true` + nhãn "giả định — cần khách xác nhận"; trả lời đủ → pipeline **tự chạy tiếp từ bước `gap`** (không làm lại `intake`).
5. **Tiến độ realtime (FR-023, NFR-001):** SSE `GET /api/bids/{id}/pipeline/events` — sự kiện `step`/`clarify`/`error`/`done`/`heartbeat` theo contract §5.2; trạng thái bước hiển thị ≤ 5 giây sau khi đổi; persist từng bước; **resume từ bước lỗi** qua `POST /api/bids/{id}/rerun` với `from_step=null` (chạy từ bước `failed` đầu tiên, giữ bước đã xong).
6. **Hồ sơ mẫu giả lập (FR-006 phần 1):** **2 mẫu text** (email tiếng Nhật + email tiếng Việt — dữ liệu 100% hư cấu, ghi chú "giả lập") nạp bằng một nút qua `POST /api/bids/sample`.
7. **Bộ mẫu tiếng Nhật (FR-025):** fixture **20 câu tiếng Nhật** xây sớm ở M2 (dùng cho `tests/test_ja_check.py` ở M7).
8. **Mở rộng bộ test PII (NFR-002):** thêm mẫu email/SĐT lẫn trong **thân email** (tiếng Việt + tiếng Nhật) — vì M2 gửi `request_content` dán từ email cho LLM.

### 1.2 Milestone này KHÔNG gồm những gì (rành mạch)

- ❌ **Không có đính kèm/đọc file** (`POST /api/bids/{id}/attachments`, `parse`, `parse/confirm`) — thuộc M6 (FR-002..005). M2 chỉ phân tích **text dán**; `no_requirement_file` giữ `false` mặc định, chưa có màn hình xác nhận parse (lỗi `400` "chưa xác nhận parse" của §5.1 **chưa áp dụng** ở M2).
- ❌ **Không triển khai các bước pipeline** `evaluate` (M6), `solution` (M3), `wbs` (M4), `proposal` (M7), `ja_check` (M7) — chỉ đăng ký `pending`. Không có đánh giá ◎/○/△/×, không hướng giải pháp, không WBS/effort/lịch/giá.
- ❌ **Không có con số nào do LLM hoặc do code** ở M2: chưa có effort/quotation/schedule (M3/M4/M5); trạng thái "Chờ làm rõ" chặn mọi phép tính (FR-010.3) — đơn giản vì chưa có module nào.
- ❌ **Không có `rerun` từ bước tùy ý** (`from_step=wbs` thuộc M4 — FR-041.2); M2 chỉ hỗ trợ `from_step=null` (resume lỗi, FR-023).
- ❌ **Không có duyệt kỹ thuật/giá, khóa hồ sơ, cổng giá** — M4/M5.
- ❌ **Không có auth thật** — header `X-Role`/`X-User` đọc và lưu `created_by` (ghi audit), chưa có phân quyền/chặn tự duyệt (M5).
- ❌ **Không có Alembic** — migration tiếp tục `Base.metadata.create_all()` (BR-09); bảng mới (`questions`, `pipeline_steps`) tạo được bằng `create_all` (M1 risk đã ghi nhận — không đổi cột bảng cũ).
- ❌ **Không có CI server** — giữ `scripts/quality_gate.sh` (bước Cloud/Infra dựng CI sau).
- ❌ **Không có trang Cài đặt / bảng chuẩn YAML** — M3/M8.

---

## 2. Frozen API contract subset (M2)

> Contract gốc: `docs/04_architecture/api_contract.md` (**FROZEN**). M2 dùng **9 endpoint** (ánh xạ §12). Backend và frontend phải bám đúng contract; mọi thay đổi sau phải qua ADR mới và cập nhật §12.

### 2.1 Endpoints (copy từ api_contract.md)

#### `POST /api/bids` — Tạo hồ sơ (FR-001, §3.1)

**Request:**
```json
{
  "project_name": "Hệ thống CRM khách hàng ABC",
  "customer_name": "Công ty XYZ (giả lập)",
  "submission_deadline": "2026-12-15",
  "customer_language": "ja",
  "request_content": "<dán email / nội dung yêu cầu — bắt buộc, ≥ 30 ký tự>",
  "budget_amount": 50000000,
  "budget_currency": "JPY"
}
```
- `request_content` bắt buộc + **tối thiểu 30 ký tự** → thiếu/ngắn trả `400 VALIDATION_ERROR` kèm `details.min_length=30` (FR-001.1 + yêu cầu milestone M2).
- `customer_language` ∈ {vi, en, ja} (FR-001.2).

**Response 201:**
```json
{
  "id": 1, "project_name": "...", "customer_name": "...", "submission_deadline": "2026-12-15",
  "customer_language": "ja", "status": "draft", "locked": false,
  "budget_amount": 50000000, "budget_currency": "JPY", "created_by": "Nhu",
  "created_at": "2026-10-09T10:00:00Z"
}
```

#### `GET /api/bids` — Danh sách hồ sơ (FR-007, §3.2)

**Query params:** `status` (lọc, tùy chọn), `q` (tìm theo tên dự án/khách hàng), `page` (mặc định 1), `page_size` (mặc định 20).

**Response 200:**
```json
{
  "items": [
    { "id": 1, "project_name": "...", "customer_name": "...", "status": "draft",
      "submission_deadline": "2026-12-15", "customer_language": "ja", "locked": false,
      "updated_at": "2026-10-09T10:00:00Z" }
  ],
  "total": 1
}
```

#### `GET /api/bids/{id}` — Chi tiết hồ sơ (FR-007, §3.3)

**Response 200:** như 3.1 + `no_requirement_file`, `data_readiness`, `display_currency`, `pipeline_progress` (tóm tắt trạng thái các bước — để UI khôi phục màn hình).

> **Làm rõ shape `pipeline_progress` (không phá vỡ contract — chi tiết hóa trường chưa định nghĩa):**
> ```json
> "pipeline_progress": {
>   "steps": [ { "step_key": "intake", "status": "completed" },
>              { "step_key": "gap", "status": "waiting_clarification" },
>              { "step_key": "evaluate", "status": "pending" } ],
>   "waiting_clarification": true,
>   "rounds_used": 1,
>   "max_rounds": 2
> }
> ```

#### `POST /api/bids/sample` — Nạp hồ sơ mẫu giả lập (FR-006, §3.7 — **path đã sửa, xem §2.2**)

**Request:** `{}` (mặc định `ja_email`) hoặc `{"sample_key": "ja_email" | "vi_email"}`. **Response 201:** như 3.1 — hồ sơ mẫu mới ở trạng thái `draft`. Dữ liệu 100% hư cấu, ghi chú "giả lập" (BR-06).

#### `POST /api/bids/{id}/pipeline/start` — Chạy pipeline (FR-023, §5.1)

**Request:** `{}`.

**Response 202:**
```json
{
  "bid_id": 1, "status": "analyzing",
  "steps": [
    { "step_key": "intake", "status": "running" },
    { "step_key": "gap", "status": "pending" },
    { "step_key": "evaluate", "status": "pending" },
    { "step_key": "solution", "status": "pending" },
    { "step_key": "wbs", "status": "pending" },
    { "step_key": "proposal", "status": "pending" },
    { "step_key": "ja_check", "status": "pending" }
  ]
}
```
**Errors:** `409 STATE_CONFLICT` (pipeline đang chạy), `409 CLARIFY_PENDING` (đang `waiting_clarification` với câu hỏi chưa trả lời). *(Lỗi `400 VALIDATION_ERROR` "chưa xác nhận parse" chỉ áp dụng khi có attachments — M6.)*

#### `GET /api/bids/{id}/pipeline/events` — SSE tiến độ (FR-023, §5.2)

**Headers:** `Accept: text/event-stream`. Stream sự kiện (mỗi lần trạng thái bước đổi — yêu cầu ≤ 5s, NFR-001):
```
event: step
data: {"bid_id":1,"step":"intake","status":"running","attempt":1}

event: step
data: {"bid_id":1,"step":"intake","status":"completed","attempt":1}

event: step
data: {"bid_id":1,"step":"gap","status":"running","attempt":1}

event: clarify
data: {"bid_id":1,"round":1,"questions":[{"id":5,"question":"ご要望のデータ件数は？","reason_vi":"Ảnh hưởng trực tiếp tới effort xử lý dữ liệu","impact":"effort","related_req_codes":[]}]}

event: error
data: {"bid_id":1,"step":"gap","status":"failed","message":"Output LLM không đúng schema sau 3 lần thử"}

event: done
data: {"bid_id":1,"status":"waiting_tech_approval"}
```
- Client `EventSource` tự reconnect; server gửi `event: heartbeat` mỗi 15s.
- **M2 semantic:** sự kiện `done` phát khi `intake` + `gap` hoàn tất (không còn câu hỏi hoặc hết vòng 2) — 5 bước còn lại vẫn `pending` (chưa triển khai ở M2). Trạng thái hồ sơ chuyển `waiting_tech_approval` theo máy trạng thái (data_model §18); M3+ sẽ kích hoạt các bước còn lại (xem §7).

#### `POST /api/bids/{id}/rerun` — Chạy lại từ bước X (FR-023, §5.3)

**Request (M2):**
```json
{ "from_step": null, "reason": "Resume sau lỗi", "by": "presales" }
```
- M2 chỉ hỗ trợ `from_step=null` → chạy từ bước `failed` đầu tiên, **giữ** các bước `completed`. `from_step=wbs` thuộc M4.
- **Response 202:** như 5.1. **Errors:** `409 STATE_CONFLICT` (đang chạy), `422 PIPELINE_ERROR` (không có bước failed).

#### `GET /api/bids/{id}/questions` — Danh sách câu hỏi (FR-007.2, FR-010, §6.1)

**Query:** `round` (tùy chọn). **Response 200:**
```json
{
  "items": [ { "id": 5, "round_no": 1, "question": "ご要望のデータ件数は？", "reason_vi": "Ảnh hưởng trực tiếp tới effort xử lý dữ liệu",
               "impact": "effort", "related_req_codes": [], "answer": null, "is_assumption": false,
               "status": "awaiting_answer" } ],
  "rounds_used": 1, "max_rounds": 2
}
```

#### `POST /api/bids/{id}/questions/{round}/answers` — Trả lời câu hỏi (FR-011, §6.2)

**Request:**
```json
{ "answers": [
    { "question_id": 5, "answer": "約100万件", "is_assumption": false },
    { "question_id": 6, "answer": "Giả định: dùng RAG với chunk 512", "is_assumption": true }
  ]
}
```
- Trả lời giả định → `is_assumption: true` → nhãn "giả định — cần khách xác nhận" (FR-011.2).
- Trả lời thiếu câu → `400 VALIDATION_ERROR` kèm `details.missing_ids` (FR-011.3).
- **Response 200:** `{ "status": "analyzing", "pipeline_resumed_from": "gap" }` — pipeline tự chạy tiếp (FR-011.3).

### 2.2 Thay đổi contract trong M2 (đã ghi vào api_contract.md)

| Thay đổi | Lý do | Ghi chú |
|---|---|---|
| **§3.1:** `request_content` tối thiểu **30 ký tự** | Yêu cầu milestone M2: "dán email/RFP (tối thiểu 30 ký tự)" | Không phá vỡ endpoint; `details.min_length=30`; cập nhật bảng error code §2 |
| **§3.7:** đổi path `POST /api/bids/{id}/sample` → **`POST /api/bids/sample`** | Path gốc ngụ ý nạp mẫu vào hồ sơ đã tồn tại — trái FR-006 ("bấm một nút → hồ sơ mẫu được **tạo**") và kịch bản roadmap M2 | `sample_key` ∈ {`ja_email`, `vi_email`}, mặc định `ja_email`; M6 bổ sung attachments mẫu; cập nhật §12 |
| **§12:** dòng M2 cập nhật endpoint sample | Theo thay đổi §3.7 | — |
| **Làm rõ `pipeline_progress`** (GET `/api/bids/{id}`) | Trường chưa định nghĩa shape — UI cần để khôi phục màn hình | Chi tiết hóa trong §2.1, không phá vỡ contract |

### 2.3 Contract chia sẻ backend ↔ frontend (M2)

| Tên | Backend (Pydantic) | Frontend (TypeScript) | Ghi chú |
|---|---|---|---|
| `BidCreate` | `app/schemas/api_schemas/bid.py` — project_name, customer_name, submission_deadline, customer_language, request_content (min_length=30), budget_amount?, budget_currency? | `src/api/types.ts` — `interface BidCreate` | FE gửi; lỗi validate hiển thị tiếng Việt |
| `BidOut` / `BidListItem` | `bid.py` — như §3.1/§3.2 | `interface Bid`, `interface BidListItem` | — |
| `BidDetailOut` | `bid.py` — BidOut + no_requirement_file, data_readiness, display_currency, pipeline_progress | `interface BidDetail extends Bid { pipeline_progress: PipelineProgress }` | `PipelineProgress { steps: StepState[]; waiting_clarification: boolean; rounds_used: number; max_rounds: number }` |
| `QuestionOut` / `QuestionsOut` | `question.py` — §6.1 | `interface Question`, `interface QuestionsResponse` | — |
| `AnswerItemIn` / `AnswersIn` | `question.py` — §6.2 | `interface AnswerItem { question_id: number; answer: string; is_assumption: boolean }` | — |
| `PipelineStartOut` / `RerunIn` | `pipeline.py` — §5.1/§5.3 | `interface PipelineStartResponse`, `interface RerunRequest` | — |
| SSE events | `pipeline/sse.py` — event `step`/`clarify`/`error`/`done`/`heartbeat` theo §5.2 | `src/api/events.ts` — EventSource wrapper; `usePipelineEvents` hook | FE parse `data:` JSON, cập nhật step states |
| `SampleKey` | `sample.py` — Literal["ja_email","vi_email"] | `type SampleKey = 'ja_email' \| 'vi_email'` | — |

---

## 3. LLM steps touched (M2)

### 3.1 Bước 1 — Intake / trích xuất thông tin yêu cầu (B1)

**Triển khai ở M2:** có (chạy trên text dán đã che PII). Schema đã cập nhật `llm_pipeline.md` §2.

**Input context:** `request_content` (đã qua `privacy/mask.py` — BR-06), `customer_language` người dùng chọn, giới hạn ký tự (`RFP_SUMMARY_MAX_CHARS`, mặc định 8.000).

**Output JSON schema (`IntakeExtraction` — `app/schemas/llm_schemas/intake_extraction.py`):**
```json
{
  "objectives_vi": "string — mục tiêu dự án, tiếng Việt, ≤ 300 từ",
  "users_vi": "string — người dùng / đối tượng sử dụng, tiếng Việt, ≤ 200 từ",
  "data_vi": "string — mô tả dữ liệu liên quan, tiếng Việt, ≤ 200 từ",
  "constraints_vi": ["string — tối đa 5 ràng buộc"],
  "budget_mentioned": "boolean",
  "budget_note_vi": "string — ≤ 100 từ (bắt buộc khi budget_mentioned=true)",
  "deadline_mentioned": "boolean",
  "deadline_note_vi": "string — ≤ 100 từ (bắt buộc khi deadline_mentioned=true)",
  "customer_language_detected": "enum: vi | en | ja | unknown",
  "summary_vi": "string — ≤ 500 từ",
  "keywords": ["string, ≤ 10"],
  "notes": ["string, ≤ 5"]
}
```

**Validation (code):**
| Rule | Hành vi |
|---|---|
| Độ dài từng trường (`objectives_vi` ≤ 300 từ, `users_vi`/`data_vi` ≤ 200 từ, `summary_vi` ≤ 500 từ, `budget_note_vi`/`deadline_note_vi` ≤ 100 từ, `constraints_vi` ≤ 5, `keywords` ≤ 10, `notes` ≤ 5) | sai → retry ≤ 2 → fail rõ (BR-02) |
| `customer_language_detected` ∈ enum | sai → retry ≤ 2 |
| `budget_note_vi`/`deadline_note_vi` bắt buộc khi cờ tương ứng = `true` | sai → retry ≤ 2 |
| **BR-01:** schema không chứa trường man-day/giá/ngày — ngân sách/thời hạn chỉ là **ghi chú văn bản** | unit test assert (`test_llm_schema_no_numbers.py`) |

**Persist:** `pipeline_steps.output_json` (bước `intake`) — hiển thị trên màn hình phân tích.

### 3.2 Bước 2 — Gap detection → câu hỏi làm rõ (B2)

**Triển khai ở M2:** có. Schema theo `llm_pipeline.md` §3.

**Input context:** output B1 (`IntakeExtraction`), `request_content` đã mask, số vòng đã dùng (0 hoặc 1), câu trả lời vòng trước (nếu vòng 2).

**Output JSON schema (`GapQuestions` — `app/schemas/llm_schemas/gap_questions.py`):**
```json
{
  "needs_clarification": "boolean",
  "questions": [
    {
      "question": "string — nội dung câu hỏi bằng NGÔN NGỮ KHÁCH (vi/en/ja)",
      "reason_vi": "string — lý do hỏi bằng tiếng Việt",
      "impact": "enum: solution | effort | price",
      "related_req_codes": []
    }
  ]
}
```

**Validation (code):**
| Rule | Hành vi |
|---|---|
| `needs_clarification=false` → `questions` phải rỗng | schema fail → retry ≤ 2 |
| `questions.length ≤ 7` (`MAX_QUESTIONS_PER_ROUND`) | vượt → giữ 7 câu đầu + cảnh báo |
| Mỗi câu có đủ `question`, `reason_vi`, `impact` ∈ enum | schema fail → retry ≤ 2 |
| `related_req_codes` — **M2 luôn rỗng** (chưa có bảng `requirements`, thuộc M6); prompt dặn LLM không sinh mã; bỏ qua kiểm tra tồn tại khi danh sách requirement rỗng | — |
| Vòng hỏi đã = 2 → **không gọi LLM nữa**, chuyển thẳng yêu cầu presales tự trả lời theo giả định (FR-010.4) | code chặn — test riêng |

**"Câu hỏi chặn" (diễn giải yêu cầu milestone):** trong contract **mọi câu hỏi được sinh ra đều chặn** — `needs_clarification=true` → pipeline dừng ở `waiting_clarification`, không chạy tiếp cho tới khi presales trả lời hoặc đánh dấu giả định (FR-010.3). Không có khái niệm "câu hỏi không-chặn" trong contract; **không thêm** trường `is_blocking` vào schema (tránh phá vỡ contract).

**Con số do code:** không có con số nào ở M2. Trạng thái "Chờ làm rõ" chặn mọi phép tính effort/giá (FR-010.3) — ở M2 chưa có module tính số nên điều này hiển nhiên đúng; test vẫn assert không có dữ liệu effort/giá được sinh ra.

**Persist/resume:** câu hỏi lưu bảng `questions` (round_no, status `awaiting_answer`); pipeline dừng ở bước `gap` (`waiting_clarification`); trả lời → chạy tiếp từ `gap`, **không** làm lại `intake`.

### 3.3 Mock responses cần cho test

`MockLLMClient` bổ sung fixture theo tên schema (cơ chế registry M1 §3.4):

| Fixture | Schema | Mục đích test |
|---|---|---|
| `IntakeExtraction` good (ja) | IntakeExtraction | happy path — email Nhật → trích xuất đầy đủ 7 nhóm thông tin |
| `IntakeExtraction` good (vi) | IntakeExtraction | mẫu tiếng Việt |
| `IntakeExtraction` bad_schema | IntakeExtraction | thiếu trường bắt buộc → retry ≤ 2 → fail rõ (BR-02) |
| `IntakeExtraction` with_number | IntakeExtraction | chứa trường `man_day`/giá/ngày → bị chặn (BR-01) |
| `GapQuestions` good (ja, 5 câu) | GapQuestions | `needs_clarification=true`, 5 câu tiếng Nhật + `reason_vi` tiếng Việt → luồng Chờ làm rõ |
| `GapQuestions` no_questions | GapQuestions | `needs_clarification=false`, `questions=[]` → pipeline chạy tiếp → `done` |
| `GapQuestions` too_many (9 câu) | GapQuestions | vượt 7 → giữ 7 câu đầu + cảnh báo |
| `GapQuestions` bad_schema | GapQuestions | sai schema → retry ≤ 2 → fail |
| Chế độ "vòng 2" | — | `rounds_used=2` → code **không gọi** `complete()` (assert `call_count` không tăng) — FR-010.4 |

---

## 4. Tasks (file-level)

### 4.1 Backend (Python 3.11 + FastAPI + SQLAlchemy 2.0 + Pydantic v2)

Theo `architecture.md` §7 — chỉ tạo phần M2 (kế thừa M1):

| File | Nội dung |
|---|---|
| `backend/app/models/question.py` | `Question` ORM theo `data_model.md` §6 (id, bid_id FK CASCADE, round_no CHECK(1,2), question, reason_vi, impact CHECK(solution/effort/price), related_req_codes JSON, answer, is_assumption DEFAULT 0, answered_by, answered_at, status DEFAULT 'awaiting_answer' CHECK(awaiting_answer/answered/skipped)) |
| `backend/app/models/pipeline_step.py` | `PipelineStep` ORM theo `data_model.md` §13 (id, bid_id FK CASCADE, step_key CHECK(7 bước), status CHECK(pending/running/completed/failed/waiting_clarification/skipped), attempts DEFAULT 0, output_json JSON, error_message, started_at, finished_at; UNIQUE(bid_id, step_key)) |
| `backend/app/models/__init__.py` | import `Question`, `PipelineStep` (để `create_all` thấy) |
| `backend/app/schemas/api_schemas/bid.py` | `BidCreate` (request_content `min_length=30`), `BidOut`, `BidListItem`, `BidDetailOut` (+ `PipelineProgressSummary`) |
| `backend/app/schemas/api_schemas/question.py` | `QuestionOut`, `AnswerItemIn`, `AnswersIn`, `QuestionsOut` (§2.3) |
| `backend/app/schemas/api_schemas/pipeline.py` | `StepStateOut`, `PipelineStartOut`, `RerunIn` (§2.3) |
| `backend/app/schemas/api_schemas/sample.py` | `SampleIn` (sample_key Literal["ja_email","vi_email"] | None), `SampleOut` |
| `backend/app/schemas/llm_schemas/intake_extraction.py` | `IntakeExtraction` (§3.1) |
| `backend/app/schemas/llm_schemas/gap_questions.py` | `GapQuestions`, `GapQuestionItem` (§3.2) |
| `backend/app/schemas/llm_schemas/__init__.py` | export `IntakeExtraction`, `GapQuestions` |
| `backend/app/services/bid_service.py` | `create_bid` (validate ≥ 30 ký tự, trạng thái `draft`, ghi changelog `create_bid`), `list_bids` (filter status, search q ILIKE, page/page_size), `get_bid` (+ `pipeline_progress` từ `pipeline_steps`), `get_bid_or_404` |
| `backend/app/services/clarify_service.py` | `save_questions_from_gap` (lưu câu hỏi vòng mới, chuyển bid `waiting_clarification`), `list_questions` (+ rounds_used/max_rounds), `submit_answers` (validate đủ câu → `missing_ids`; lưu answer/is_assumption/answered_by; chuyển bid `analyzing`; ghi changelog `answer_question`), `count_unanswered` |
| `backend/app/services/sample_service.py` | `load_sample(sample_key)` — đọc `sample_data/ja_email.md` / `sample_data/vi_email.md`, tạo bid mới (project_name/customer_name/… hư cấu, ghi chú "giả lập") |
| `backend/app/pipeline/__init__.py` | export orchestrator, sse |
| `backend/app/pipeline/orchestrator.py` | `PipelineOrchestrator.start(bid_id)` — tạo task asyncio; đăng ký 7 dòng `pipeline_steps` (intake/gap thật, 5 bước còn lại `pending` + note "chưa triển khai ở M2"); chạy `intake` → `gap`; persist từng bước; phát SSE; chuyển trạng thái bid; chặn chạy đồng thời (409) |
| `backend/app/pipeline/steps/__init__.py` | — |
| `backend/app/pipeline/steps/b1_intake.py` | `run_intake(bid, ctx)` — dựng prompt (text đã mask), gọi `complete_with_retry(schema=IntakeExtraction)`, persist `output_json`, phát SSE `step:intake:completed` |
| `backend/app/pipeline/steps/b2_gap.py` | `run_gap(bid, ctx)` — nếu `rounds_used >= 2` → **không gọi LLM**, kết thúc bước (FR-010.4); ngược lại gọi `complete_with_retry(schema=GapQuestions)`, validate ≤ 7, lưu câu hỏi qua `clarify_service`, nếu `needs_clarification` → bid `waiting_clarification` + SSE `clarify` + dừng pipeline; ngược lại → `gap` completed + SSE `done` |
| `backend/app/pipeline/sse.py` | `SSEManager` — in-process: `subscribe(bid_id)` → async generator (replay trạng thái hiện tại từ `pipeline_steps` rồi stream live); `publish(bid_id, event, data)`; heartbeat 15s; xóa subscriber khi disconnect |
| `backend/app/pipeline/runner.py` | registry task đang chạy theo bid_id (guard 409 STATE_CONFLICT); `resume(bid_id, from_step=None)` — tìm bước `failed` đầu tiên, chạy lại từ đó (giữ bước `completed`) |
| `backend/app/llm/prompts/__init__.py` | — |
| `backend/app/llm/prompts/b1_intake.py` | `build_intake_prompt(request_content_masked, customer_language)` — tiếng Việt, dặn BR-01 (không xuất số/ngày), dặn `related_req_codes` rỗng (B2) |
| `backend/app/llm/prompts/b2_gap.py` | `build_gap_prompt(intake_output, rounds_used, previous_answers, customer_language)` — glossary tiếng Nhật cho câu hỏi (NFR-004), dặn ≤ 7 câu, ngôn ngữ khách + lý do tiếng Việt |
| `backend/app/llm/mock_client.py` | bổ sung fixture `IntakeExtraction` + `GapQuestions` (§3.3) |
| `backend/app/api/routers/bids.py` | `POST /bids`, `GET /bids`, `GET /bids/{id}`, `POST /bids/sample` |
| `backend/app/api/routers/pipeline.py` | `POST /bids/{id}/pipeline/start`, `GET /bids/{id}/pipeline/events` (StreamingResponse SSE), `POST /bids/{id}/rerun` |
| `backend/app/api/routers/questions.py` | `GET /bids/{id}/questions`, `POST /bids/{id}/questions/{round}/answers` |
| `backend/app/api/routers/__init__.py` | include 3 router mới |
| `backend/tests/conftest.py` | giữ nguyên (mock LLM + DB tạm) |
| `backend/tests/test_bids.py` | create/list/get: happy path; `request_content` < 30 ký tự → 400 + `details.min_length`; thiếu trường → 400; lọc status; tìm q; phân trang |
| `backend/tests/test_sample_data.py` | 2 mẫu nạp được (201, trạng thái `draft`); dữ liệu hư cấu (không tên công ty thật); có ghi chú "giả lập" (BR-06); `sample_key` lạ → 400 |
| `backend/tests/test_clarifying_questions.py` | **xem §5(a)** — gap: ≤ 7 câu, tiếng Nhật cho khách ja + reason_vi tiếng Việt, vòng ≤ 2, `needs_clarification=false` → questions rỗng, retry schema xấu, vòng 2 không gọi LLM |
| `backend/tests/test_pipeline_resume.py` | **xem §5(a)** — persist từng bước; mock fail intake → rerun từ intake; fail gap → rerun từ gap; bước `completed` không chạy lại; 409 khi đang chạy; 409 CLARIFY_PENDING khi chưa trả lời |
| `backend/tests/test_pipeline_sse.py` | SSE: thứ tự event `step:intake:running → completed → gap:running → clarify/done`; `heartbeat`; reconnect replay trạng thái hiện tại |
| `backend/tests/test_llm_schema_no_numbers.py` | **mở rộng:** assert `IntakeExtraction` + `GapQuestions` không chứa trường man-day/giá/ngày (BR-01) |
| `backend/tests/test_pii_mask.py` | **mở rộng:** thêm mẫu email/SĐT trong thân email tiếng Việt + tiếng Nhật (≥ 10 mẫu mới) |
| `backend/tests/fixtures/ja_samples.py` | **20 câu tiếng Nhật** (chuẩn + lỗi cố ý) — fixture cho FR-025, dùng ở M7 (`test_ja_check.py`) |

### 4.2 Frontend (React 18 + Vite + TypeScript + Tailwind)

| File | Nội dung |
|---|---|
| `frontend/src/api/types.ts` | bổ sung `Bid`, `BidCreate`, `BidListItem`, `BidDetail`, `PipelineProgress`, `StepState`, `Question`, `QuestionsResponse`, `AnswerItem`, `PipelineStartResponse`, `RerunRequest`, `SampleKey` (§2.3) |
| `frontend/src/api/client.ts` | bổ sung `createBid`, `listBids(status?, q?)`, `getBid(id)`, `loadSample(key?)`, `startPipeline(id)`, `getQuestions(id)`, `submitAnswers(id, round, answers)`, `rerunPipeline(id)`; xử lý lỗi envelope `{error:{code,message,details}}` → hiển thị tiếng Việt |
| `frontend/src/api/events.ts` | `subscribePipelineEvents(bidId, handlers)` — EventSource `GET /api/bids/{id}/pipeline/events`; parse `event:` + `data:`; tự reconnect; trả unsubscribe |
| `frontend/src/hooks/usePipelineEvents.ts` | hook quản lý SSE: state `steps: Record<step_key, status>`, `clarifyQuestions`, `done`, `error`; cập nhật khi nhận event |
| `frontend/src/pages/BidNewPage.tsx` | **form thật:** project_name, customer_name, submission_deadline (date), customer_language (select vi/en/ja), request_content (textarea, hint "tối thiểu 30 ký tự", đếm ký tự), budget_amount/budget_currency (tùy chọn); validate client + hiển thị lỗi server tiếng Việt; submit → `createBid` → navigate `/bids/{id}`; **2 nút mẫu:** "Nạp mẫu tiếng Nhật" (`loadSample('ja_email')`), "Nạp mẫu tiếng Việt" (`loadSample('vi_email')`) → navigate tới hồ sơ mẫu |
| `frontend/src/pages/BidsPage.tsx` | danh sách: bảng (tên dự án, khách hàng, trạng thái, hạn nộp, ngôn ngữ); filter `status` (dropdown) + search `q` (debounce); phân trang; row click → `/bids/{id}`; trạng thái rỗng "Chưa có hồ sơ — bấm Tạo hồ sơ hoặc Nạp hồ sơ mẫu" |
| `frontend/src/pages/BidDetailPage.tsx` | chi tiết hồ sơ: thông tin + **kết quả phân tích** (B1: mục tiêu/người dùng/dữ liệu/ràng buộc/ngân sách/thời hạn/ngôn ngữ phát hiện — từ `pipeline_progress` + `GET /api/bids/{id}`); nút **"Phân tích"** (start pipeline; disabled khi đang `analyzing` hoặc `waiting_clarification` chưa trả lời — hint "Hãy trả lời câu hỏi làm rõ trước"); `PipelineProgress` + `ClarifySection` |
| `frontend/src/components/PipelineProgress.tsx` | danh sách 7 bước với badge trạng thái (running spinner / completed ✓ / failed ✗ / waiting_clarification ⏸ / pending "chưa triển khai ở M2" mờ); lỗi/retry hiển thị message tiếng Việt |
| `frontend/src/components/ClarifySection.tsx` | hiển thị câu hỏi (question ngôn ngữ khách + reason_vi tiếng Việt + impact badge); form trả lời từng câu + checkbox "Trả lời theo giả định" (nhãn "giả định — cần khách xác nhận"); nút "Gửi trả lời" → `submitAnswers` → pipeline resume (SSE cập nhật); lỗi thiếu câu → highlight câu thiếu |
| `frontend/src/components/StepBadge.tsx` | badge trạng thái bước (dùng chung) |
| `frontend/src/App.tsx` | thêm route `/bids/:id` → `BidDetailPage` |
| `frontend/src/App.test.tsx` | mở rộng smoke: render BidsPage với mock list; render BidDetailPage với mock detail + questions |

### 4.3 Sample data + fixtures

| File | Nội dung |
|---|---|
| `sample_data/ja_email.md` | **Mẫu 1 — email tiếng Nhật (hư cấu):** khách "株式会社デモ商事（仮名・架空）", dự án CRM, có mục tiêu/người dùng/dữ liệu/ràng buộc, đề cập ngân sách + thời hạn, **kèm email + SĐT Nhật** (để minh chứng mask PII); header ghi chú "DỮ LIỆU GIẢ LẬP" (BR-06) |
| `sample_data/vi_email.md` | **Mẫu 2 — email tiếng Việt (hư cấu):** khách "Công ty TNHH Minh Phát (giả lập)", yêu cầu hệ thống quản lý kho; có email + SĐT VN; header ghi chú "DỮ LIỆU GIẢ LẬP" |
| `backend/tests/fixtures/ja_samples.py` | 20 câu tiếng Nhật (10 chuẩn + 10 có lỗi cố ý: Latin lẫn, sai thuật ngữ, sai chính tả tên) — fixture FR-025 |
| `backend/tests/fixtures/pii_samples.py` | **mở rộng:** + 10 mẫu email/SĐT trong thân email tiếng Việt/Nhật |

### 4.4 Shared contract giữa backend ↔ frontend (M2)

- **9 endpoint** (§2.1) — FE gọi qua `client.ts` base `/api` (BR-10); BE trả theo contract; envelope lỗi `{error:{code,message,details}}` message tiếng Việt.
- **SSE:** FE dùng `EventSource`; BE phát đúng event name + JSON `data:` (§2.3). FE **không** tự suy diễn trạng thái — luôn lấy từ event + `GET /api/bids/{id}` (`pipeline_progress`).
- **Trạng thái hồ sơ** (data_model §18): `draft → analyzing → waiting_clarification → analyzing → waiting_tech_approval` — FE hiển thị nhãn tiếng Việt: Nháp / Đang phân tích / Chờ làm rõ / Chờ duyệt kỹ thuật.
- **Ngôn ngữ:** UI + lỗi + lý do câu hỏi tiếng Việt; nội dung câu hỏi theo `customer_language` (BR-07, NFR-004).

---

## 5. Acceptance criteria

### (a) Shell commands — bắt buộc exit 0

```bash
# Một lệnh chạy TOÀN BỘ test
make test

# Tương đương — từng phần (cho CI/dev)
cd backend && pytest -q                                          # toàn bộ test backend (mock LLM)
cd frontend && npm run build                                     # type-check + build production
curl -f http://localhost:8000/api/bids                           # backend đang chạy → 200 (danh sách rỗng ok)
curl -f http://localhost:8000/api/bids/1                         # chi tiết hồ sơ → 200
cd backend && LLM_PROVIDER=mock pytest -q tests/test_clarifying_questions.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_pipeline_resume.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_pipeline_sse.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_bids.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_sample_data.py
cd backend && pytest -q tests/test_llm_schema_no_numbers.py     # BR-01 (mở rộng M2)
cd backend && pytest -q tests/test_pii_mask.py                  # ≥ 50 mẫu, tỷ lệ ≥ 99% (mở rộng M2)

# Quality gate (CI sơ bộ)
make quality-gate
```

> Lưu ý: `curl -f http://localhost:8000/api/bids/1` yêu cầu tồn tại hồ sơ id=1 — chạy sau khi nạp mẫu hoặc tạo hồ sơ (kịch bản b dưới đây). Port 8000 theo `architecture.md` §6.

### (b) Manual scenario (Preview) — từng bước + kết quả mong đợi

Chạy stack theo skill `app-preview` (podman-compose; backend :8000, frontend proxy `/api`).

| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| 1 | Mở app → **Tạo hồ sơ** | Form đầy đủ; textarea có hint "tối thiểu 30 ký tự" + bộ đếm; 2 nút "Nạp mẫu tiếng Nhật" / "Nạp mẫu tiếng Việt" |
| 2 | Điền thiếu nội dung yêu cầu (hoặc < 30 ký tự) → bấm Tạo | Lỗi tiếng Việt "Nội dung yêu cầu phải có ít nhất 30 ký tự" (client + server `400 VALIDATION_ERROR`); hồ sơ không được tạo |
| 3 | Bấm **"Nạp mẫu tiếng Nhật"** | Hồ sơ mẫu mới được tạo (trạng thái **Nháp**), tự điều hướng tới trang chi tiết; nội dung email tiếng Nhật hiển thị; có ghi chú "DỮ LIỆU GIẢ LẬP" |
| 4 | Bấm **"Phân tích"** | Web hiển thị tiến độ từng bước qua SSE: `intake` chạy → xong, `gap` chạy; cập nhật ≤ 5 giây; 5 bước còn lại mờ "chưa triển khai ở M2" |
| 5 | Pipeline dừng ở **"Chờ làm rõ"** | Hiển thị ≤ 7 câu hỏi **bằng tiếng Nhật**, mỗi câu kèm lý do **tiếng Việt** + badge mức ảnh hưởng (giải pháp/effort/giá); nút "Phân tích" bị disabled kèm hint "Hãy trả lời câu hỏi làm rõ trước" |
| 6 | Để trống 1 câu → bấm "Gửi trả lời" | Hệ thống nhắc trả lời câu còn thiếu (highlight); `400 VALIDATION_ERROR` kèm `details.missing_ids` |
| 7 | Trả lời 1 câu theo **"giả định"** (bật checkbox) | Câu đó có nhãn **"giả định — cần khách xác nhận"** |
| 8 | Trả lời đủ → bấm "Gửi trả lời" | Pipeline **tự chạy tiếp từ bước `gap`** (không làm lại `intake` — SSE chỉ thấy `gap` chạy lại); nếu không còn câu hỏi → `done`, hồ sơ chuyển **"Chờ duyệt kỹ thuật"**; màn hình phân tích hiển thị kết quả B1 (mục tiêu/người dùng/dữ liệu/ràng buộc/ngân sách/thời hạn/ngôn ngữ phát hiện) |
| 9 | Mở **Hồ sơ** → danh sách | Hồ sơ mẫu hiển thị đúng trạng thái; lọc theo trạng thái + tìm theo tên/khách hàng hoạt động |
| 10 | Mở lại hồ sơ đang **"Chờ làm rõ"** | Các câu hỏi chưa trả lời vẫn hiển thị, trả lời tiếp được (FR-007.2); trả lời xong → resume như bước 8 |
| 11 | (Tùy chọn) Giết pipeline giữa chừng (mock lỗi ở `intake` hoặc `gap`) | Hồ sơ giữ trạng thái bước lỗi; bấm "Chạy lại" (rerun) → chạy **từ bước lỗi**, bước đã xong không chạy lại (FR-023) |
| 12 | Bấm **"Nạp mẫu tiếng Việt"** | Hồ sơ mẫu tiếng Việt tạo được; câu hỏi làm rõ (nếu có) bằng **tiếng Việt** — kiểm chứng ngôn ngữ khách |

### (c) Test chứng minh từng rule AGENTS.md liên quan M2

| Rule AGENTS.md | Test bắt buộc | Assert chính |
|---|---|---|
| **1. No invented numbers** | `tests/test_llm_schema_no_numbers.py` (mở rộng) | `IntakeExtraction` + `GapQuestions` không chứa trường man-day/giá/ngày; ngân sách/thời hạn chỉ là ghi chú văn bản (BR-01) |
| **2. Structured LLM output** | `tests/test_clarifying_questions.py::test_retry_bad_schema` | Fixture xấu (Intake/Gap) → retry ≤ 2 → fail rõ (BR-02) |
| **3. One LLM gateway** | `conftest.py` + `tests/test_pipeline_resume.py` | Mọi bước pipeline gọi qua `complete_with_retry`; test dùng `LLM_PROVIDER=mock`; không request HTTP (BR-03) |
| **4. Ask instead of guess** | `tests/test_clarifying_questions.py` | `needs_clarification=true` → bid `waiting_clarification`, pipeline dừng; không sinh dữ liệu effort/giá khi Chờ làm rõ; vòng ≤ 2 — sau vòng 2 **không gọi LLM** (FR-010.4); trả lời thiếu → `missing_ids` (BR-04) |
| **6. Privacy** | `tests/test_pii_mask.py` (mở rộng) + `tests/test_bids.py` | Prompt gửi mock đã che email/SĐT (assert `last_prompt` không chứa email/SĐT gốc); ≥ 50 mẫu, tỷ lệ ≥ 99%; mẫu giả lập không tên thật (BR-06, NFR-002) |
| **7. Languages** | `tests/test_clarifying_questions.py::test_questions_in_customer_language` | Khách `ja` → câu hỏi tiếng Nhật + `reason_vi` tiếng Việt; UI/lỗi tiếng Việt (BR-07, NFR-004) |
| **8. Done means proven** | `make test` exit 0 + kịch bản (b) | Cả test tự động lẫn Preview đều pass (BR-08) |
| **9. Keep it simple** | review + `tests/test_pipeline_sse.py` | SSE in-process (asyncio queue), không WebSocket/queue/broker (BR-09, NFR-008) |
| **10. Frontend networking** | `scripts/quality_gate.sh` (grep guard) + `frontend/src/App.test.tsx` | Không `http://localhost` trong `frontend/src/`; base root-relative `/api` (BR-10, NFR-011) |

---

## 6. Test data

- **2 hồ sơ mẫu giả lập (FR-006 phần 1)** — `sample_data/ja_email.md` + `sample_data/vi_email.md` (xem §4.3). Dữ liệu 100% hư cấu, ghi chú "giả lập" (BR-06). Mỗi mẫu chứa email + SĐT để minh chứng mask PII khi gửi LLM.
- **Bộ PII mở rộng** — `backend/tests/fixtures/pii_samples.py`: thêm ≥ 10 mẫu (email/SĐT VN + Nhật lẫn trong thân email tiếng Việt/Nhật); tổng ≥ 50 mẫu, tỷ lệ che ≥ 99% (NFR-002).
- **Bộ mẫu tiếng Nhật 20 câu (FR-025)** — `backend/tests/fixtures/ja_samples.py`: 10 câu chuẩn + 10 câu có lỗi cố ý (Latin lẫn, sai thuật ngữ glossary, sai chính tả tên công ty) — **fixture xây từ M2, kiểm tra chạy ở M7** (`tests/test_ja_check.py`, ngưỡng ≥ 90%).
- **Fixture LLM mock** — `backend/app/llm/mock_client.py`: theo §3.3 (IntakeExtraction good ja/vi + bad_schema + with_number; GapQuestions good ja + no_questions + too_many + bad_schema; chế độ vòng 2 không gọi LLM).

---

## 7. Rủi ro & ghi chú cho milestone sau

| Rủi ro / ghi chú | Mức | Giảm thiểu / hành động |
|---|---|---|
| **Semantic `done` của M2:** pipeline "hoàn tất" khi chỉ `intake` + `gap` xong; bid chuyển `waiting_tech_approval` dù 5 bước còn lại `pending` | Trung bình | Ghi rõ trong UI ("các bước còn lại sẽ triển khai ở M3+"); **M3+**: orchestrator kích hoạt bước mới phải chuyển bid `waiting_tech_approval → analyzing` rồi chạy từ bước `pending` đầu tiên — ghi vào handoff M3 |
| Resume pipeline (FR-023) phức tạp — race khi user bấm rerun lúc pipeline đang chạy | Trung bình | Guard 409 ở `runner.py`; test `test_pipeline_resume.py` phủ race cơ bản; MVP chấp nhận chạy tuần tự 1 pipeline/bid |
| Chất lượng câu hỏi tiếng Nhật (R1 handoff) | Cao | Glossary thuật ngữ trong prompt B2 (NFR-004); bộ mẫu tiếng Nhật 20 câu xây sớm; FR-025 hoàn thiện ở M7 |
| SSE kết nối đồng thời giới hạn (~6/domain) | Thấp | Mỗi hồ sơ tối đa 1 luồng tiến độ (ADR-002); đóng subscriber khi disconnect |
| `create_all` không alter bảng cũ | Thấp | M2 chỉ **thêm** bảng mới (`questions`, `pipeline_steps`) — an toàn; nếu M3+ đổi cột bảng cũ → Alembic |
| Mock fixture "quá ngoan" → sót lỗi thật (ADR-004) | Trung bình | Fixture xấu (bad_schema, with_number, too_many, vòng 2) dựng sẵn ở M2 |
| Bước `evaluate`/`solution`/`wbs`/`proposal`/`ja_check` chưa có — `pipeline_progress` hiển thị 5 bước pending có thể gây hiểu nhầm | Thấp | UI ghi chú "chưa triển khai ở M2"; handoff M3 sẽ kích hoạt `solution` |
| `related_req_codes` luôn rỗng ở M2 (chưa có requirements) | Thấp | M6 sẽ nối danh sách requirement + bật kiểm tra tồn tại mã |

---

**Task Slice Spec (M2) complete. Awaiting prompt for the next role.**