# API Contract — Presales Bidding Assistant (FROZEN)

| Thuộc tính | Giá trị |
|---|---|
| Tên tài liệu | API contract MVP — single source of truth cho backend & frontend |
| Phiên bản | 1.0 |
| Ngày | 2026-10-09 |
| Trạng thái | **FROZEN** — mọi thay đổi sau này phải qua ADR mới |
| Nguồn | `srs.md`, `architecture.md`, `data_model.md`, `llm_pipeline.md` |

> **Ghi chú thay đổi (2026-10-10, theo yêu cầu milestone M4 — xem ADR-006 trong `architecture.md`):**
> mở rộng Module F cho **WBS 3 cấp (nhóm / task / sub-task)** và **master schedule sửa được**:
> 1. `§8.1`/`§8.2` — item WBS thêm `parent_code` (hệ tầng, tối đa 3 cấp) và `depends_on` (phụ thuộc, code kiểm tra **không vòng**); `role` + `man_day` chỉ bắt buộc với **task lá**, `man_day` lá ≤ 10; `check` thêm `cycle_free`, `leaf_within_limit`.
> 2. `§8.4a` (mới) — `PUT /api/bids/{id}/schedule` để cập nhật tham số lịch (số người/vai trò, ngày bắt đầu, buffer, lịch nghỉ, mốc thanh toán) → code tính lại **không gọi AI**.
> 3. `§8.4` — `GET /schedule` trả thêm `tasks[]` (ngày từng task — dữ liệu cho Gantt), `by_role`, `holidays_applied`.
> Không thay đổi endpoint M1–M3; field cũ (`role`, `man_day`, `weight`) vẫn giữ, chỉ bắt buộc với task lá.

> **Ghi chú thay đổi (2026-10-10, reconcile M5):** bổ sung §10.0 gồm `GET/PUT /api/bids/{id}/proposal` để
> proposal draft do B6 tạo có thể xem/sửa trên web trước khi xuất. Đây là phần còn thiếu giữa FR-050.4,
> `proposal_drafts` trong `data_model.md` và yêu cầu M5; không thay đổi các endpoint giá/duyệt hiện có.

> **Ghi chú thay đổi (2026-10-10, reconcile M7):** bổ sung §10.4 và §10.5 để đáp ứng yêu cầu tải
> từng file hoặc gói `.zip`. Excel estimate của M7 chứa thêm sheet Q&A làm rõ; không thêm endpoint
> riêng cho Q&A để tránh tạo bản dữ liệu thứ hai. Endpoint bundle chỉ đóng gói các file đã sinh bằng
> code, giữ nguyên price gate và quy tắc tên file; không thay đổi các endpoint M1–M6.

---

## 1. Nguyên tắc chung

> **B3 (2026-10-11):** solution có thêm độ tin cậy, giả định, hướng loại trừ và điểm
> khả thi; intake giữ mốc lịch khách theo văn bản; quotation bị khóa theo trạng thái hồ sơ;
> bổ sung Q&A import/export và proposal versions. Mọi số effort, lịch, giá vẫn do code/
> reference tables tính; LLM/mock chỉ phân loại và giải thích.

> **B3 (2026-10-11):** mở rộng solution với độ tin cậy/giả định/hướng loại trừ/điểm khả thi;
> intake có ghi chú mốc lịch khách; quotation bị khóa khi hồ sơ đã khóa; bổ sung Q&A
> import/export và proposal versions. Mọi số effort, lịch, giá vẫn do code/reference tables tính.

1. **Root-relative (BR-10):** mọi endpoint có prefix `/api/...`. Frontend dùng base `/api` — **không bao giờ** hardcode `http://localhost:...` (grep CI chặn). Proxy `/api` → backend chỉ khai báo trong `vite.config.ts` (dev) / cấu hình Preview (prod).
2. **JSON:** request/response dùng `application/json` (trừ upload file và download file).
3. **Envelope lỗi:** mọi lỗi trả về:
```json
{ "error": { "code": "NOT_FOUND", "message": "Không tìm thấy hồ sơ", "details": {} } }
```
   `message` luôn bằng tiếng Việt, hành động được (NFR-010). `details` tùy chọn (danh sách lỗi validate, mã thiếu/thừa...).
4. **Thành công:** trả thẳng resource (không bọc `data`), trừ endpoint danh sách → `{ "items": [...], "total": n }`.
5. **Vai trò giả lập (MVP):** không có auth server. Client gửi header `X-Role: presales | ai_developer | manager` và `X-User: <tên người dùng>` (giả lập). Backend dùng để: chặn tự duyệt giá (FR-042.2), ghi audit (NFR-009), phân quyền hành động nhạy cảm. Header thiếu → mặc định `presales`/`anonymous` + cảnh báo.
6. **Idempotency:** `POST /pipeline/start` và `POST /rerun` khi pipeline đang chạy → `409 STATE_CONFLICT`.
7. **Khóa hồ sơ (FR-042.4):** mọi mutation trên hồ sơ `locked=true` → `409 STATE_CONFLICT` (trừ endpoint mở khóa/export/xem).

---

## 2. Error codes chuẩn

| HTTP | `code` | Ý nghĩa | Ví dụ |
|---|---|---|---|
| 400 | `VALIDATION_ERROR` | Request sai định dạng/thiếu trường bắt buộc | Thiếu hoặc ngắn hơn 30 ký tự `request_content` (FR-001.1) |
| 400 | `FILE_TOO_LARGE` | File > 20 MB (FR-002.2) | Upload 25 MB |
| 400 | `TOO_MANY_FILES` | > 10 file (FR-002.2) | Upload file thứ 11 |
| 400 | `INVALID_FILE_TYPE` | Loại file không hợp lệ | `.exe` |
| 404 | `NOT_FOUND` | Resource không tồn tại | `GET /api/bids/999` |
| 409 | `STATE_CONFLICT` | Trạng thái hồ sơ sai / hồ sơ bị khóa / pipeline đang chạy / tự duyệt | Sửa WBS khi `locked=true`; duyệt giá khi `X-User == created_by` |
| 409 | `CLARIFY_PENDING` | Còn câu hỏi chưa trả lời — pipeline không chạy tiếp (FR-010.3) | Start pipeline khi `waiting_clarification` |
| 422 | `PIPELINE_ERROR` | Pipeline lỗi (schema fail sau retry, timeout) — kèm `details.step` | Bước `evaluate` fail |
| 422 | `CHECK_FAILED` | Kiểm tra trước duyệt có mục fail — chặn duyệt (FR-044) | Thiếu requirement trong đánh giá |
| 500 | `INTERNAL_ERROR` | Lỗi không xác định | |

---

## 3. Module A — Hồ sơ & file đính kèm

### 3.0 `GET /api/health` — Health check (M1 — Foundation)

**Mô tả:** Kiểm tra backend còn hoạt động; trả về trạng thái tổng thể, phiên bản, cấu hình LLM (không lộ bí mật) và trạng thái DB. Dùng cho trang chủ (hiển thị "Backend OK") và cho CI/proxy.

> **Ghi chú thay đổi (2026-10-09):** endpoint này đã được §12 gán cho M1 nhưng chưa có định nghĩa chi tiết trong contract. Bổ sung §3.0 để backend/frontend có contract chung từ M1 — **không thay đổi** bất kỳ endpoint nào khác; không phải thay đổi phá vỡ.

**Response 200:**
```json
{
  "status": "ok",
  "app": "presales-bidding-assistant",
  "version": "0.1.0",
  "llm_provider": "mock",
  "database": "ok",
  "time": "2026-10-09T10:00:00Z"
}
```

- `status`: `ok` khi backend sẵn sàng; `degraded` khi DB lỗi (vẫn trả HTTP 200 — FE hiển thị cảnh báo, `curl -f` của quality gate không fail oan).
- `app`: tên ứng dụng cố định `presales-bidding-assistant`.
- `version`: phiên bản app (lấy từ `app.__version__`, khớp `pyproject.toml`).
- `llm_provider`: giá trị env `LLM_PROVIDER` (`mock` | `openai_compat`) — **không bao giờ** trả `LLM_API_KEY` / `LLM_BASE_URL` (BR-06, NFR-005).
- `database`: `ok` nếu kết nối SQLite thành công; `error` kèm `message` tiếng Việt nếu không.
- `time`: thời gian UTC ISO 8601.

### 3.1 `POST /api/bids` — Tạo hồ sơ (FR-001, UC-01)

> **Ghi chú thay đổi (2026-10-09, theo yêu cầu milestone M2):** bổ sung ràng buộc `request_content` tối thiểu **30 ký tự** (yêu cầu milestone: "dán email/RFP tối thiểu 30 ký tự"). Không thay đổi endpoint nào khác; `details.min_length=30` kèm trong lỗi validate.

**Request:**
```json
{
  "project_name": "Hệ thống CRM khách hàng ABC",
  "customer_name": "Công ty XYZ (giả lập)",
  "submission_deadline": "2026-12-15",
  "customer_language": "ja",
  "request_content": "<dán email / nội dung yêu cầu — bắt buộc>",
  "budget_amount": 50000000,
  "budget_currency": "JPY"
}
```
- `request_content` bắt buộc → thiếu trả `400 VALIDATION_ERROR` (FR-001.1).
- `request_content` tối thiểu **30 ký tự** (yêu cầu milestone M2) → ngắn hơn trả `400 VALIDATION_ERROR` kèm `details.min_length=30` (FR-001.1).
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

### 3.2 `GET /api/bids` — Danh sách hồ sơ (FR-007, UC-11)

**Query params:** `status` (lọc, tùy chọn), `q` (tìm theo tên dự án/khách hàng), `deal_stage` (lọc giai đoạn deal, tùy chọn), `page` (mặc định 1), `page_size` (mặc định 20).

**Response 200:**
```json
{
  "items": [
    { "id": 1, "project_name": "...", "customer_name": "...", "deal_stage": "discovery",
      "created_at": "2026-10-01T10:00:00Z", "total_price": null, "total_price_currency": null,
      "status": "draft", "submission_deadline": "2026-12-15", "customer_language": "ja",
      "locked": false, "updated_at": "2026-10-09T10:00:00Z" }
  ],
  "total": 1
}
```

- `deal_stage`, `total_price` và `total_price_currency` có thể `null` khi hồ sơ chưa có dữ liệu tương ứng.
- `total_price` lấy từ `grand_total` của quotation mới nhất đã được quotation engine tính bằng code; backend không suy diễn giá.
- `created_at` là thời điểm tạo hồ sơ, khác với `updated_at`.

### 3.3 `GET /api/bids/{id}` — Chi tiết hồ sơ (FR-007)

**Response 200:** như 3.1 + `no_requirement_file`, `data_readiness`, `display_currency`, `pipeline_progress` (tóm tắt trạng thái các bước — để UI khôi phục màn hình).

### 3.4 `POST /api/bids/{id}/attachments` — Upload file (FR-002, UC-01)

**Request:** `multipart/form-data`, field `file` (binary). Query: `file_type` tùy chọn (ép loại) — nếu thiếu, backend tự đoán (FR-002.3).

**Response 201:**
```json
{ "id": 10, "filename": "req.xlsx", "file_type": "requirement", "detected_type": "requirement",
  "size_bytes": 204800, "parse_status": "pending" }
```
**Errors:** `FILE_TOO_LARGE`, `TOO_MANY_FILES`, `INVALID_FILE_TYPE`.

### 3.5 `GET /api/bids/{id}/attachments` — Danh sách file (FR-005)

**Response 200:** `{ "items": [ { "id": 10, "filename": "...", "file_type": "requirement", "size_bytes": 204800, "parse_status": "ok|error|pending", "parse_error": null, "sheet_mappings": [...] } ] }`

### 3.6 `PUT /api/bids/{id}/attachments/{attachment_id}` — Sửa loại file / mapping cột (FR-002.3, FR-003.2)

**Request:**
```json
{ "file_type": "sample_data", "sheet_mappings": [ { "sheet_name": "Sheet1", "sheet_kind": "requirement",
  "col_map": { "code": "番号", "content": "機能要件", "priority": "区分", "category": "大分類" } } ] }
```
**Response 200:** attachment đã cập nhật (parse_status reset `pending` nếu mapping đổi).

### 3.7 `POST /api/bids/sample` — Nạp hồ sơ mẫu giả lập (FR-006, UC-10)

**Request:** `{}` (hoặc `{"sample_key": "ja_email" | "vi_email"}`; thiếu → mặc định `ja_email`). **Response 201:** như 3.1 — hồ sơ mẫu **mới** ở trạng thái `draft`; M6 sẽ bổ sung attachments mẫu. Dữ liệu 100% hư cấu, ghi chú "giả lập" (BR-06).

> **Ghi chú thay đổi (2026-10-09, theo yêu cầu milestone M2):** đường dẫn gốc `POST /api/bids/{id}/sample` ngụ ý nạp mẫu **vào hồ sơ đã tồn tại** — trái với FR-006 ("bấm một nút → hồ sơ mẫu được **tạo** đầy đủ") và kịch bản roadmap M2 (nạp mẫu → hồ sơ mẫu mới ở trạng thái Nháp). Sửa thành `POST /api/bids/sample` (tạo hồ sơ mẫu mới). Cập nhật §12 tương ứng.

### 3.8 `GET /api/bids/sample/preview` — Xem bộ mẫu trước khi tạo hồ sơ (UI Đợt 1)

**Query:** `sample_key=ja_email|vi_email` (mặc định `ja_email`).

**Response 200:** trả metadata form và danh sách file để người dùng xem trước; endpoint
không tạo hồ sơ và không chạy pipeline.

```json
{
  "sample_key": "ja_email",
  "project_name": "...",
  "customer_name": "...",
  "submission_deadline": "2026-12-15",
  "customer_language": "ja",
  "display_currency": "JPY",
  "budget_amount": 15000000,
  "budget_currency": "JPY",
  "customer_schedule_start": "2027-01-01",
  "customer_schedule_end": "2027-09-30",
  "request_content": "...",
  "files": [{"filename": "ja_email.md", "file_type": "rfp", "size_bytes": 123}]
}
```

Mẫu không hợp lệ trả `400 VALIDATION_ERROR`; dữ liệu mẫu luôn hư cấu.

Với `sample_key=ja_email`, ngân sách mẫu là `15,000,000 JPY` (tương đương ghi chú RFP
`1,500万円`, chưa thuế) và lịch khách là `2027-01-01` đến `2027-09-30`. Đây là dữ liệu
được khai báo trong fixture mẫu, không phải số do LLM sinh; quotation engine dùng các trường
đã lưu để tính chênh lệch ngân sách bằng code.

---

## 4. Module B — Đọc file & xác nhận

### 4.1 `POST /api/bids/{id}/parse` — Đọc file (FR-003, FR-004, UC-02)

**Request:** `{}` (dùng mapping đã lưu).

**Response 200:**
```json
{
  "requirements": { "count": 235, "no_requirement_file": false },
  "attachments": [ { "id": 10, "filename": "req.xlsx", "status": "ok" },
                   { "id": 11, "filename": "broken.pdf", "status": "error", "error": "Không đọc được PDF — file hỏng" } ],
  "sample_profile": { "row_count": 1200, "columns": [ { "name": "email", "type": "string", "empty_pct": 5, "pii_suspected": true } ],
                      "readiness_suggestion": "low" },
  "column_mapping_confirmed": false
}
```
**Errors:** `422 PIPELINE_ERROR` nếu parse lỗi nặng (kèm `details` từng file).

### 4.2 `PUT /api/bids/{id}/parse/confirm` — Xác nhận kết quả đọc file (FR-005, UC-02)

**Request:**
```json
{ "data_readiness": "medium", "confirmed": true }
```
- `confirmed: true` là điều kiện để chạy pipeline (FR-005.2); `data_readiness` chỉnh tay (FR-004.2).
- **Response 200:** bid mới (status vẫn `draft`).

---

## 5. Module C — Pipeline & tiến độ realtime

### 5.1 `POST /api/bids/{id}/pipeline/start` — Chạy pipeline (FR-023, UC-04)

**Request:** `{}` — pipeline chạy 7 bước (xem `llm_pipeline.md`).

**Response 202:**
```json
{ "bid_id": 1, "status": "analyzing", "steps": [
    { "step_key": "intake", "status": "completed" },
    { "step_key": "gap", "status": "running" },
    { "step_key": "evaluate", "status": "pending" },
    { "step_key": "solution", "status": "pending" },
    { "step_key": "wbs", "status": "pending" },
    { "step_key": "proposal", "status": "pending" },
    { "step_key": "ja_check", "status": "pending" }
] }
```
**Errors:** `409 STATE_CONFLICT` (đang chạy), `409 CLARIFY_PENDING` (chưa trả lời), `400 VALIDATION_ERROR` (chưa xác nhận parse).

### 5.2 `GET /api/bids/{id}/pipeline/events` — SSE tiến độ (FR-023)

**Headers:** `Accept: text/event-stream`. **Response 200:** stream sự kiện:

```
event: step
data: {"bid_id":1,"step":"evaluate","status":"running","attempt":1,"progress":{"batch":2,"total":6}}

event: step
data: {"bid_id":1,"step":"evaluate","status":"completed","attempt":1}

event: warning
data: {"bid_id":1,"step":"wbs","message":"Tổng effort lệch 25% so với midpoint — cần người duyệt ghi chú"}

event: clarify
data: {"bid_id":1,"round":1,"questions":[{"id":5,"question":"...","reason_vi":"...","impact":"effort"}]}

event: error
data: {"bid_id":1,"step":"proposal","status":"failed","message":"Output LLM chứa số tiền sau 3 lần thử"}

event: done
data: {"bid_id":1,"status":"waiting_tech_approval"}
```

- Client `EventSource` tự reconnect; server gửi `event: heartbeat` mỗi 15s (giữ kết nối).
- Yêu cầu: trạng thái bước hiển thị ≤ 5s sau khi đổi (NFR-001).

### 5.3 `POST /api/bids/{id}/rerun` — Chạy lại từ bước X (FR-041.2, FR-023)

**Request:**
```json
{ "from_step": "wbs", "reason": "Góp ý: cần tách task infra", "by": "ai_developer" }
```
- MVP: `from_step` ∈ {`wbs`} (chạy lại tùy ý ngoài phạm vi — SRS §8.2); resume lỗi dùng `from_step=null` → chạy từ bước `failed` đầu tiên.
- Rerun từ `wbs`: **snapshot WBS cũ** tự động (FR-041.2), giữ evaluation + solution.
- **Response 202:** như 5.1. **Errors:** `409 STATE_CONFLICT` (locked / đang chạy), `422 PIPELINE_ERROR` (bước `from_step` chưa từng chạy).

---

## 6. Module D — Hỏi làm rõ

### 6.1 `GET /api/bids/{id}/questions` — Danh sách câu hỏi (FR-007.2, FR-010)

**Query:** `round` (tùy chọn). **Response 200:**
```json
{ "items": [ { "id": 5, "round_no": 1, "question": "ご要望のデータ件数は？", "reason_vi": "Ảnh hưởng trực tiếp tới effort xử lý dữ liệu",
               "impact": "effort", "related_req_codes": ["REQ-012"], "answer": null, "is_assumption": false,
               "status": "awaiting_answer" } ], "rounds_used": 1, "max_rounds": 2 }
```

### 6.2 `POST /api/bids/{id}/questions/{round}/answers` — Trả lời câu hỏi (FR-011, UC-03)

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

---

## 7. Module E — Đánh giá & hướng giải pháp

### 7.1 `GET /api/bids/{id}/evaluations` — Bảng đáp ứng (FR-020, FR-021)

**Response 200:**
```json
{
  "solution_direction": { "direction": "rag", "reason_vi": "...", "selected_by": "ai_developer", "selected_at": "..." },
  "warnings": [ { "type": "missing_codes", "codes": ["REQ-099"], "message": "Thiếu 1 mã sau 3 lần thử" } ],
  "items": [
    { "req_code": "REQ-001", "content": "...", "priority": "mandatory", "category": "...",
      "rating": "○", "needs_clarification": false, "note_vi": "", "solution_direction": "rag" }
  ],
  "stats": { "total": 235, "evaluated": 234, "◎": 20, "○": 150, "△": 40, "×": 24, "cần làm rõ": 0, "needs_clarification": 3 }
}
```

### 7.2 `POST /api/bids/{id}/solution` — Chọn/đổi hướng giải pháp (FR-022, FR-041)

**Request:**
```json
{ "direction": "rag", "reason_vi": "Dữ liệu phi cấu trúc lớn, cần truy vấn ngữ nghĩa", "by": "ai_developer" }
```
- `direction` ∈ {none, traditional_ml, rag, agent, fine_tune}.
- Đổi hướng → code tính lại effort (không gọi LLM); evaluation cũ đánh dấu "theo hướng cũ" (FR-020.5).
- **Response 200:** `{ "direction": "rag", "effort_recalculated": true, "warnings": ["Đánh giá requirement đang theo hướng cũ"] }`

Solution có thể trả `reliability_vi`, `assumptions_vi`, `excluded_directions` và
`feasibility` (technical/delivery/operational, mô tả định tính). Đây chỉ là phân loại/giải thích,
không chứa effort, giá hoặc ngày.

---

## 8. Module F — WBS, Schedule, Quotation

### 8.0 `GET /api/bids/{id}/effort` — Effort theo hướng giải pháp (FR-030, FR-031, FR-033)

**Mô tả:** Trả về effort do **code tính** từ bảng chuẩn YAML theo hướng giải pháp đã chọn (FR-030), kèm hệ số đã áp dụng (FR-031) và dấu vết tính toán (FR-033). LLM không tham gia tính số (BR-01). Endpoint này phục vụ milestone M3 của roadmap (trước khi có WBS).

**Response 200:**
```json
{
  "direction": "rag",
  "factors": [ { "key": "customer_jp", "value": 1.2, "reason": "Khách Nhật" } ],
  "factor_product": 1.2,
  "cap": 2.0,
  "by_phase": { "poc": { "min": 8, "max": 12 }, "mvp": { "min": 20, "max": 30 }, "production": { "min": 10, "max": 16 } },
  "midpoint_total": 57.6,
  "trace": { "table_version": 4, "source": "reference/effort.yaml + override settings", "formula": "Σ midpoint(min,max) × factor_product" }
}
```

**Lỗi:** `404 NOT_FOUND` (hồ sơ không tồn tại) · `409 STATE_CONFLICT` (chưa chọn hướng giải pháp).

### 8.1 `GET /api/bids/{id}/wbs` — Xem WBS (FR-032, FR-041)

**Response 200:** WBS **3 cấp (nhóm / task / sub-task)** — mọi item có `parent_code`; cấp 1 = nhóm (`parent_code: null`), cấp 2 = task, cấp 3 = sub-task (lá). Chỉ **task lá** mang `role` + `man_day`; nhóm/task cha có `man_day` = tổng con (code tính) và `role: null`.

```json
{
  "items": [
    { "task_code": "WBS-001", "name_vi": "PoC — Khảo sát & thiết kế", "phase": "poc",
      "parent_code": null, "level": 1, "role": null, "weight": null, "man_day": 8.0,
      "depends_on": [], "sort_order": 1, "is_leaf": false },
    { "task_code": "WBS-001-01", "name_vi": "Khảo sát hiện trạng", "phase": "poc",
      "parent_code": "WBS-001", "level": 2, "role": null, "weight": null, "man_day": 5.0,
      "depends_on": [], "sort_order": 1, "is_leaf": false },
    { "task_code": "WBS-001-01-01", "name_vi": "Phỏng vấn khách hàng", "phase": "poc",
      "parent_code": "WBS-001-01", "level": 3, "role": "ba", "weight": 20, "man_day": 3.0,
      "depends_on": [], "sort_order": 1, "is_leaf": true }
  ],
  "totals": { "man_day": 42.0, "by_phase": { "poc": 8.0, "mvp": 22.0, "production": 12.0 } },
  "check": { "midpoint": 40.0, "deviation_pct": 5.0, "within_20pct": true, "pm_qa_ok": true,
             "cycle_free": true, "leaf_max_man_day": 8.0, "leaf_within_limit": true,
             "warning": null },
  "trace": { "direction": "rag", "factors": [ {"key": "customer_jp", "value": 1.2, "reason": "Khách Nhật"} ],
             "factor_product": 1.2, "cap": 2.0, "range": { "min": 32, "max": 48 },
             "formula": "midpoint(range) × Σweight → man_day/task lá (≤ 10); nhóm = Σ con" }
}
```

- `level` ∈ {1,2,3} — code suy từ chuỗi `parent_code`; độ sâu tối đa **3** (vi phạm → `400 VALIDATION_ERROR`).
- `is_leaf` = item không có item nào nhận nó làm `parent_code`. `role`/`weight`/`man_day` chỉ hợp lệ trên lá; lá có `man_day ≤ 10` (FR-032.1, `check.leaf_within_limit`).
- `depends_on`: danh sách `task_code` phụ thuộc (tối đa 5, không tự tham chiếu); code kiểm tra **không vòng** (`check.cycle_free`).
- `check.pm_qa_ok`: mỗi phase (`poc`/`mvp`/`production`) có ≥ 1 lá role `pm` và ≥ 1 lá role `qa` (FR-032.2).
- `check.within_20pct`: |Σ man_day − midpoint| / midpoint ≤ 20% (FR-032.3); sai → `warning` (không chặn; override phải ghi chú — BR-12).
- `totals.by_phase` = tổng man-day theo phase (tính từ lá).

**Errors:** `404 NOT_FOUND` · `409 STATE_CONFLICT` (chưa có WBS — hãy chạy bước "Tạo WBS").

### 8.2 `PUT /api/bids/{id}/wbs` — Sửa WBS (FR-041, UC-06)

**Request:**
```json
{ "changes": [
    { "op": "add", "task": { "task_code": "WBS-010", "name_vi": "Test chấp nhận", "phase": "production",
                             "parent_code": null, "role": "qa", "man_day": 3.0, "depends_on": [] } },
    { "op": "add", "task": { "task_code": "WBS-010-01", "name_vi": "UAT với khách", "phase": "production",
                             "parent_code": "WBS-010", "role": "qa", "man_day": 2.0, "depends_on": ["WBS-010"] } },
    { "op": "update", "task_code": "WBS-001-01-01", "fields": { "man_day": 5.0 } },
    { "op": "update", "task_code": "WBS-001-01", "fields": { "depends_on": ["WBS-002-01"] } },
    { "op": "remove", "task_code": "WBS-001-01" }
  ],
  "by": "ai_developer", "note": "Bổ sung QA giai đoạn production" }
```
- `add`: `task_code` duy nhất; `parent_code` phải tham chiếu item đã tồn tại (hoặc `null`); độ sâu ≤ 3; `role` + `man_day` bắt buộc khi tạo **lá** (`man_day ≤ 10`); `weight` tùy chọn (thêm tay → `null`).
- `update`: `fields` ⊆ {`name_vi`, `phase`, `parent_code`, `role`, `man_day`, `depends_on`, `sort_order`}; đổi `parent_code` không tạo vòng cây / vượt độ sâu 3; đổi `role`/`man_day` chỉ hợp lệ trên lá.
- `remove`: xóa item **cùng toàn bộ sub-tree**; code dọn `depends_on` trỏ tới item đã xóa.
- Sửa xong → code **tự tính lại** tổng, check, lịch — **không gọi AI** (FR-041.1). Response kèm `recalculated: { schedule: {...} }` (mục `quotation` bổ sung ở M5).
- Override ngoài ±20% → bắt buộc `note` (BR-12); thiếu → `400 VALIDATION_ERROR`.
- **Response 200:** WBS mới như §8.1 + `recalculated`.
- **Errors:** `409 STATE_CONFLICT` (locked — FR-042.4) · `400 VALIDATION_ERROR` (trùng mã, vòng phụ thuộc, lá > 10 md, thiếu PM/QA khi override không ghi chú, depth > 3).

### 8.3 `POST /api/bids/{id}/wbs/snapshot` — Chụp snapshot WBS (FR-041.2)

**Request:** `{ "reason": "Trước khi chạy lại từ WBS", "by": "ai_developer" }`
**Response 201:** `{ "snapshot_id": 3, "diff_summary": null }`
- `diff_summary` (khi so với WBS hiện tại) tính ở mức item: `{added: [...], removed: [...], modified: [{task_code, field, old, new}]}` — `field` gồm cả `parent_code`, `depends_on`, `man_day` (ADR-005).

### 8.4 `GET /api/bids/{id}/schedule` — Master schedule (FR-034)

**Response 200:** lịch do **code tính** từ WBS × số người/vai trò, ngày bắt đầu, buffer, lịch nghỉ; kèm `tasks[]` (ngày từng task — dữ liệu Gantt).

```json
{
  "start_date": "2026-11-01", "buffer_days": 5, "working_calendar": "jp",
  "team_allocation": { "pm": 1, "ba": 1, "ai_engineer": 1, "backend": 2, "frontend": 1, "qa": 1 },
  "payment_milestones": [ { "name": "Kickoff", "percent": 20, "due_offset_days": 0 } ],
  "by_role": { "backend": { "man_day": 20.0, "headcount": 2, "duration_days": 10 },
               "qa": { "man_day": 6.0, "headcount": 1, "duration_days": 6 },
               "pm": { "man_day": 4.0, "headcount": 1, "duration_days": 4 } },
  "tasks": [
    { "task_code": "WBS-001-01-01", "phase": "poc", "role": "ba", "man_day": 3.0,
      "start_date": "2026-11-02", "end_date": "2026-11-04" }
  ],
  "holidays_applied": ["2026-11-03", "2026-11-23"],
  "end_date": "2026-12-10", "deadline_violation": false,
  "warning": null,
  "trace": { "formula": "end = start + Σ(ceil(man_day/task ÷ headcount[role])) theo phase + buffer (trừ T7/CN + nghỉ lễ)" }
}
```

- **Mô hình MVP (giữ đơn giản — BR-09):** phase tuần tự `poc → mvp → production`; trong phase, task xếp theo thứ tự topo của `depends_on` (rồi `sort_order`), chạy **tuần tự**; thời lượng task = `ceil(man_day ÷ headcount[role])` ngày làm việc; ngày bắt đầu task ≥ ngày kết thúc của mọi task trong `depends_on`.
- `working_calendar` ∈ {`vn`, `jp`, `both`} — mặc định theo `customer_language` (ja→`jp`, vi/en→`vn`); ngày nghỉ lấy từ `reference/holidays.yaml`; cuối tuần T7/CN luôn nghỉ.
- `by_role.duration_days` = Σ thời lượng task của role (ngày làm việc); `end_date` = ngày làm việc cuối cùng sau buffer; `deadline_violation = end_date > submission_deadline` → `warning` (FR-034).
- `payment_milestones` mặc định từ `reference/payment.yaml`; ngày đến hạn = `start_date + due_offset_days` (ngày lịch).
- **Errors:** `404 NOT_FOUND` · `409 STATE_CONFLICT` (chưa có lịch — hãy gọi `PUT /schedule` trước).

### 8.4a `PUT /api/bids/{id}/schedule` — Cập nhật tham số lịch (FR-034, UC-06)

**Request:**
```json
{ "start_date": "2026-11-01", "buffer_days": 5, "working_calendar": "jp",
  "team_allocation": { "pm": 1, "ba": 1, "ai_engineer": 1, "backend": 2, "frontend": 1, "qa": 1 },
  "payment_milestones": [ { "name": "Kickoff", "percent": 20, "due_offset_days": 0 } ],
  "by": "ai_developer" }
```
- `team_allocation`: key ⊆ 8 vai trò, headcount ≥ 0; **mọi role xuất hiện trong WBS phải có headcount ≥ 1** (thiếu → `400 VALIDATION_ERROR` kèm `details.missing_roles`).
- `payment_milestones` tùy chọn; thiếu → mặc định `reference/payment.yaml`; tổng `percent` ≤ 100.
- Lưu tham số → code **tính lại lịch ngay, không gọi AI**; ghi changelog (`edit_schedule`).
- **Response 200:** schedule mới như §8.4. **Errors:** `409 STATE_CONFLICT` (locked) · `400 VALIDATION_ERROR`.

### 8.5 `GET /api/bids/{id}/quotation` — Báo giá (FR-040, FR-042)

**Response 200:**
```json
{
  "contract_model": "fixed_price", "contingency_percent": 20.0,
  "fx_rate": { "value": 1.0, "date": "2026-10-01", "pair": "VND/VND" },
  "valid_until": "2026-11-08", "tax_mode": "tax_excluded",
  "totals": { "by_role": { "backend": { "man_day": 20.0, "rate": 3500000, "amount": 70000000 } },
              "overhead": { "pm": 7000000, "brse": 0 }, "contingency_amount": 15400000,
              "operating_cost": 0, "subtotal": 92400000, "tax_excluded": 92400000, "grand_total": 92400000 },
  "budget": { "amount": 50000000, "currency": "JPY", "difference": null },
  "payment_milestones": [ { "name": "Kickoff", "percent": 20, "due_offset_days": 0 } ],
  "trace": { "formula": "Σ(man_day × rate) + overhead + contingency; làm tròn yen: round_half_up(1000)" }
}
```
- `budget.difference` chỉ hiển thị khi có ngân sách (FR-042.1); quy đổi theo tỉ giá có ngày hiệu lực.
- `payment_milestones` lấy từ master schedule đã lưu; nếu chưa cấu hình thì trả mảng rỗng. Backend không tính lại giá trị từ phía client.

**Dot 6a quotation settings:** `PUT /api/bids/{id}/quotation` accepts `contract_model`
(`fixed_price`, `tm`, `odc`), `currency` (`VND`, `JPY`, `USD`), `contingency_percent`,
`onsite_percent`, and code-only `price_to_win_percent` constrained to `-50..200`.
T&M accepts `tm_months`; ODC accepts `odc_fte` and `odc_months`; the response includes
a code-computed monthly `totals.payment_plan`. When budget exists, `budget` includes
`difference_percent` and `adjustment_suggestion_percent`. All settings are rejected
after price approval lock.

**Dot 6a schedule settings:** `PUT /api/bids/{id}/schedule` accepts editable
`go_no_go_gap_working_days` (default `10`) and `gantt_break_interval` (`day`, `week`,
or `month`). The response includes `earliest_mvp_start` and
`earliest_production_start`, computed from the schedule and constrained by customer
intake schedule dates. Recalculation is code-only and does not call the LLM.

---

## 9. Module G — Duyệt

### 9.1 `POST /api/bids/{id}/approvals/tech` — Duyệt kỹ thuật (FR-041, FR-044, UC-06)

**Request:**
```json
{ "decision": "approved", "by": "ai_developer", "comment": "OK", "skip_with_reason": null }
```
- `decision` ∈ {approved, rejected, skip}. `skip` = bỏ qua duyệt kỹ thuật → bắt buộc `skip_with_reason` (FR-044.3).
- `rejected` → bắt buộc `comment` (lý do từ chối — FR-041.4) → hồ sơ chuyển `rejected`.
- **Response 200:** `{ "status": "waiting_price_approval" | "rejected", "approval_id": 7 }`

### 9.2 `POST /api/bids/{id}/approvals/price` — Duyệt giá (FR-042, FR-043, FR-044, UC-07)

**Request:**
```json
{ "decision": "approved", "by": "manager_linh", "contract_model": "fixed_price",
  "contingency_percent": 20.0, "comment": "Đồng ý mức giá" }
```
- **Chặn tự duyệt (FR-042.2):** `by == bids.created_by` → `409 STATE_CONFLICT` kèm message "Người tạo hồ sơ không được tự duyệt giá".
- Trước khi duyệt: chạy kiểm tra tự động (FR-044) — có mục `fail` → `422 CHECK_FAILED` kèm `details.checks_report`.
- `rejected` → bắt buộc `comment` (FR-042.3) → hồ sơ chuyển `rejected` (vẫn xuất proposal với `[Presales điền]`).
- `approved` → hồ sơ `price_approved` + `locked=true` (FR-042.4).

**Response 200:**
```json
{ "status": "price_approved", "locked": true, "checks_report": [
    { "check": "no_missing_requirement", "status": "pass" },
    { "check": "effort_within_20pct", "status": "warning", "detail": "Lệch 25% — đã có ghi chú override" },
    { "check": "schema_valid", "status": "pass" },
    { "check": "pm_qa_present", "status": "pass" } ] }
```

### 9.3 `POST /api/bids/{id}/unlock` — Mở khóa hồ sơ (FR-042.4)

**Request:** `{ "reason": "Khách thay đổi phạm vi", "by": "manager_linh" }`
- Chỉ role manager; bắt buộc `reason` (ghi changelog). Sau khi sửa → phải duyệt lại giá.
- **Response 200:** `{ "locked": false, "status": "waiting_price_approval" }`

---

## 10. Module H — Xuất file (FR-025, FR-043, FR-050–052)

### 10.0 `GET /api/bids/{id}/proposal` và `PUT /api/bids/{id}/proposal` — Draft proposal trên web (FR-050.4)

`GET` trả draft proposal hiện tại, trạng thái cổng giá và các mục văn bản để UI chỉnh sửa. `PUT` chỉ cập nhật
các trường văn bản của draft; backend không nhận và không tin số tiền, man-day, ngày hoặc trạng thái duyệt từ
client. Mọi số trong proposal được code render từ quotation/schedule; trước duyệt giá cổng vẫn là
`[Presales điền]`.

**GET response 200:**
```json
{
  "bid_id": 1,
  "sections": {
    "introduction": "...",
    "solution_overview": "...",
    "approach": "...",
    "risks": "...",
    "conclusion": "..."
  },
  "assumptions_phrased": ["..."],
  "scope_out_phrased": ["..."],
  "price_gate": "placeholder",
  "editable": true,
  "updated_at": "2026-10-10T10:00:00Z"
}
```

**PUT request:**
```json
{
  "sections": {
    "introduction": "...",
    "solution_overview": "...",
    "approach": "...",
    "risks": "...",
    "conclusion": "..."
  },
  "by": "presales"
}
```

- Các section bắt buộc không rỗng; `assumptions_phrased` và `scope_out_phrased` do code giữ/tổng hợp,
  không cho client ghi đè trong M5.
- Hồ sơ `locked=true` vẫn cho sửa draft văn bản không làm thay đổi số liệu; sửa WBS/effort/giá vẫn bị chặn.
- **Response 200:** như GET. **Errors:** `404 NOT_FOUND`, `400 VALIDATION_ERROR`, `409 STATE_CONFLICT` nếu
  draft đang ở trạng thái không cho sửa.

### 10.1 `GET /api/bids/{id}/exports/proposal.docx` — Xuất proposal Word (FR-050)

**Response 200:** `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (file binary, `Content-Disposition: attachment`).
- Khi `customer_language=ja`: chạy kiểm tra tiếng Nhật trước (FR-025); kết quả trả trong header `X-Ja-Check-Result: {"result":"warning","issues":[...]}` (URL-encoded) — FE hiển thị cảnh báo sau khi tải (không chặn).
- Cổng giá (FR-043): chưa duyệt → mọi số tiền là `[Presales điền]`.

### 10.2 `GET /api/bids/{id}/exports/estimate.xlsx` — Xuất Excel ước tính (FR-051)

**Response 200:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`. Tổng là **công thức** `=SUM(...)` (FR-051.1).

### 10.3 `GET /api/bids/{id}/exports/proposal.pdf` — Xuất PDF (FR-052)

**Response 200:** `application/pdf` (chuyển từ Word bằng code — LibreOffice headless).

### 10.4 `GET /api/bids/{id}/exports/bundle.zip` — Gói file xuất (M7)

**Mô tả:** Sinh một gói ZIP deterministic chứa các file M7 đã sinh cho cùng hồ sơ theo thứ tự cố định: proposal
Word, estimate Excel (gồm sheet `Q&A`), proposal PDF và slide PowerPoint. Nếu một file chưa từng được sinh,
backend sinh file đó trước khi đóng gói; không đưa file tạm, đường dẫn máy chủ hay secret vào ZIP.

**Response 200:** `application/zip`, `Content-Disposition: attachment`.

- Tên entry bên trong và tên ZIP tuân theo quy tắc `<Khách>_<Dự án>_<Loại>_v<phiên bản>_<ngày>`;
  ký tự không an toàn được chuẩn hóa deterministic.
- Gói giữ nguyên cổng giá: hồ sơ chưa duyệt có `[Presales điền]`, không có số tiền thực.
- Gói không gọi LLM và không làm thay đổi WBS, lịch, báo giá hoặc trạng thái duyệt.

### 10.5 Nội dung sheet `Q&A` trong `estimate.xlsx` — Câu hỏi làm rõ

Không phải endpoint riêng. Backend dựng sheet từ câu hỏi đã persist trong `questions`, với cột:
`Mã câu hỏi`, `Vòng`, `Câu hỏi`, `Lý do (tiếng Việt)`, `Ảnh hưởng`, `Trả lời`, `Là giả định`,
`Trạng thái`. Câu hỏi và trả lời khách dùng `customer_language`; lý do và nhãn nội bộ dùng tiếng
Việt. Sheet này cho khách điền rồi presales nhập lại qua endpoint M2 hiện có, không được dùng để
ghi đè trực tiếp DB khi upload lại trong M7.

### 10.6 `GET /api/bids/{id}/exports/proposal.pptx` — Slide tóm tắt proposal

**Response 200:** `application/vnd.openxmlformats-officedocument.presentationml.presentation`.

- Slide 16:9 theo `customer_language`: bìa, nội dung, các section của draft, giả định/ngoài phạm vi, tổng hợp
  effort, Gantt và báo giá. Gantt/mốc thanh toán vẽ bằng shape sửa được (không phải ảnh).
- Mọi số lấy từ WBS/schedule/quotation đã persist; không gọi LLM để dựng file.
- Cổng giá như Word: chưa duyệt → slide báo giá chỉ có `[Presales điền]`.
- Ghi `export_logs` với `kind=pptx`; header `X-Ja-Check-Result` như §10.1.

### 10.7 Quy tắc chung cho file xuất

- Ngày trong tên file là ngày xuất thực tế, dùng chung cho mọi file của cùng request.
- `Content-Disposition` gồm `filename` ASCII và `filename*=UTF-8''...` (áp dụng cả `requirements.xlsx`
  và `questions/export`).
- Endpoint từng file chỉ sinh file đó (tải Word/Excel/PPTX không phụ thuộc bộ chuyển PDF).

---

## 11. Module I — Bảng chuẩn & cài đặt (FR-060, FR-061)

### 11.1 `GET /api/settings` — Xem bảng chuẩn

**Response 200:**
```json
{ "keys": [
    { "key": "effort", "source": "repo|db", "version": 3, "updated_by": "manager_linh", "updated_at": "...",
      "yaml_preview": "# effort.yaml — min–max man-day theo direction × phase\n..." },
    { "key": "rate_card", "source": "repo", "version": 1, "yaml_preview": "..." }
] }
```

### 11.2 `PUT /api/settings/{key}` — Sửa bảng chuẩn (FR-060)

**Request:**
```json
{ "yaml_content": "direction:\n  rag:\n    poc: {min: 10, max: 15}\n...", "by": "manager_linh" }
```
- Validate toàn vẹn (FR-060.2): mọi tổ hợp direction × phase có min–max; mọi vai trò có đơn giá offshore + onsite; trần hệ số > 1. Sai → `400 VALIDATION_ERROR` kèm `details.errors[]`, **giữ giá trị cũ**.
- **Response 200:** `{ "key": "effort", "version": 4, "source": "db" }`.
- Không ảnh hưởng hồ sơ đã duyệt giá (FR-061, BR-11 — nhờ `reference_snapshots`).

---

### 10.0a `GET/POST /api/bids/{id}/proposal/versions` và `PUT .../versions/{version_id}/sent` — Phiên bản gửi khách (B3-06)

`POST` chụp proposal draft hiện tại thành phiên bản tăng dần `1.0`, `2.0`...; `GET` liệt kê
theo thứ tự tạo; `PUT .../sent` đánh dấu phiên bản đã gửi. Phiên bản giữ ngôn ngữ khách và
sections đã được server render; không nhận số effort/giá/lịch từ client và không bypass price gate.

### 10.0b `GET/POST /api/bids/{id}/questions/export|import` — Q&A sheet (B3-05)

`GET` trả workbook `Q&A` theo ngôn ngữ khách, gồm mã câu hỏi, `Vòng`, câu hỏi, lý do và câu trả lời;
toàn bộ ô cột answer được tô vàng để khách điền. Sheet `Q&A` bị khóa (không mật khẩu) trừ cột answer; kèm sheet
hướng dẫn theo ngôn ngữ khách; tên file theo quy tắc `<Khách>_<Dự án>_QA_v1_<ngày>.xlsx`; ghi `export_logs`
`kind=qa_xlsx`. Khi nhập lại, backend ưu tiên sheet tên `Q&A`. `POST` nhận multipart field `file`, giới hạn 5 MB
và 200 dòng, chỉ nhập câu trả lời cho cặp mã câu hỏi + vòng đang chờ. Dòng trống, câu đã đóng hoặc
mã không tồn tại được bỏ qua và trả trong `warnings`; file thiếu cột, hỏng hoặc vượt giới hạn trả
`400 VALIDATION_ERROR`. Nhập lại file không tạo câu trả lời trùng.

### 10.0c `POST /api/bids/{id}/questions/email-draft` — Email nháp (Dot 6a)

Sinh nội dung email bằng gateway LLM và schema JSON `EmailDraft`; mock được dùng trong test/CI.
Tên khách và người gửi do backend điền, không lấy từ output LLM. Nội dung prompt được mask PII
trước khi gửi. Response trả `bid_id`, `customer_name`, `sender`, `customer_language`, `subject`
và `body`; người dùng có thể chỉnh sửa nội dung trả về trước khi gửi.

### 10.0d — Dot 6a schedule and quotation extensions

Quotation responses expose `contract_model`, `currency`, budget comparison fields,
`totals.payment_plan`, and for ODC `totals.odc_fte_months` computed as `FTE × months`.
T&M payment rows include a code-computed monthly `amount`. Intake persists separate
customer MVP and Production start months when explicitly present in the RFP; schedule
responses expose those dates alongside the computed earliest dates. The Gantt interval
and go/no-go working-day gap are persisted schedule settings, with a default gap of 10.
Schedule responses also expose `go_no_go_start` and `go_no_go_end` so the Gantt can render
the post-PoC break interval without deriving dates in the browser.

## 12. Ánh xạ milestone → endpoint (đã reconcile với roadmap PM — 8 milestone)

| Milestone (roadmap PM) | Endpoint cần |
|---|---|
| M1 — Foundation (skeleton, health, LLM mock, DB, test, README) | `GET /api/health` (xem `architecture.md`) |
| M2 — Phân tích yêu cầu + hỏi làm rõ (FR-001, FR-007, FR-010, FR-011, FR-023, FR-006*) | POST/GET `/api/bids`, GET `/api/bids/{id}`, POST `/api/bids/sample`, POST `/api/bids/{id}/pipeline/start`, GET `/api/bids/{id}/pipeline/events` (SSE), POST `/api/bids/{id}/rerun`, GET `/api/bids/{id}/questions`, POST `/api/bids/{id}/questions/{round}/answers` |
| M3 — Hướng giải pháp + effort (FR-022, FR-030, FR-031, FR-033) | POST `/api/bids/{id}/solution`, GET `/api/bids/{id}/effort` (§8.0), GET `/api/bids/{id}/evaluations` (bản tối thiểu — đầy đủ ở M6) |
| M4 — WBS + schedule (FR-032, FR-034, FR-041) | GET/PUT `/api/bids/{id}/wbs`, POST `/api/bids/{id}/wbs/snapshot`, GET/PUT `/api/bids/{id}/schedule` |
| M5 — Proposal + giá + duyệt (FR-040, FR-042, FR-043, FR-044) | GET/PUT `/api/bids/{id}/proposal`, GET `/api/bids/{id}/quotation`, POST `/api/bids/{id}/approvals/tech`, POST `/api/bids/{id}/approvals/price`, POST `/api/bids/{id}/unlock` |
| M6 — Đính kèm + ma trận đáp ứng (FR-002..006*, FR-020, FR-021) | POST/GET `/api/bids/{id}/attachments`, PUT `/api/bids/{id}/attachments/{attachment_id}`, POST `/api/bids/{id}/parse`, PUT `/api/bids/{id}/parse/confirm`, GET `/api/bids/{id}/evaluations` (đầy đủ) |
| M7 — Xuất file (FR-025, FR-050, FR-051, FR-052) | GET `/api/bids/{id}/exports/proposal.docx`, `/exports/estimate.xlsx`, `/exports/proposal.pdf`, `/exports/proposal.pptx`, `/exports/bundle.zip` |
| M8 — Hoàn thiện (FR-060, FR-061) | GET `/api/settings`, PUT `/api/settings/{key}` |

**Ghi chú reconcile:**
- **FR-020/021 (ma trận đáp ứng)** đặt ở M6 (roadmap PM); M3 chỉ cần bản đánh giá tối thiểu làm nền cho hướng giải pháp — endpoint `GET evaluations` triển khai tối thiểu ở M3, đầy đủ ở M6.
- **FR-044 (kiểm tra trước duyệt)** ở M5: mục "không sót requirement" cần ma trận đáp ứng (M6) — M5 triển khai các mục còn lại (schema, ±20%, PM/QA), M6 nối dữ liệu; giao diện báo cáo kiểm tra thống nhất ngay từ M5.
- **PowerPoint:** đã đưa vào phạm vi theo yêu cầu người dùng (2026-10-15) — endpoint `GET /api/bids/{id}/exports/proposal.pptx` (§10.6); bundle gồm 4 file.

---

## 13. Tuân thủ AGENTS.md rules (tường minh)

| Rule | Cách contract tuân thủ |
|---|---|
| 1 — No invented numbers | Contract không có endpoint cho LLM "điền số"; mọi con số trong response đều kèm `trace` (FR-033); schema LLM (xem `llm_pipeline.md`) không chứa man-day/giá/ngày. WBS: LLM chỉ đề xuất cấu trúc + trọng số, **code gán man-day** cho task lá (≤ 10) từ midpoint bảng chuẩn (FR-032, ADR-006) |
| 2 — Structured LLM output | Lỗi schema → `422 PIPELINE_ERROR` với `details.step`; retry ≤ 2 ở backend |
| 3 — One LLM gateway | Không endpoint nào lộ LLM; gateway nội bộ, config env |
| 4 — Ask instead of guess | `409 CLARIFY_PENDING`; vòng hỏi ≤ 2 (trả trong GET questions) |
| 5 — Price gate | Export trả `[Presales điền]` khi chưa duyệt; `price_gate` ghi trong export_logs |
| 6 — Privacy | Không endpoint trả API key; upload có giới hạn; dữ liệu mẫu giả lập |
| 7 — Languages | Message lỗi tiếng Việt; nội dung câu hỏi/proposal theo `customer_language` |
| 8 — Done means proven | Contract là cơ sở test: pytest (backend) + MSW/Vitest (FE) + smoke Preview |
| 9 — Keep it simple | Không endpoint auth server; X-Role header giả lập; không queue/WS |
| 10 — Frontend networking | Mọi path bắt đầu `/api`; FE dùng base root-relative; grep CI cấm `http://localhost` |
