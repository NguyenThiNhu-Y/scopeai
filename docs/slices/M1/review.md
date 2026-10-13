# Review — M1 Foundation (Slice Review)

| Thuộc tính | Giá trị |
|---|---|
| Vai trò | Reviewer (code + document review) |
| Ngày | 2026-10-09 |
| Phạm vi | Toàn bộ code M1 (backend/ + frontend/ + Makefile + scripts/quality_gate.sh + README + compose preview) |
| Nguồn | `AGENTS.md`, `docs/slices/M1/spec.md`, `test_report.md`, `fix_log.md`, `docs/04_architecture/` |
| Kết quả | **PASS** (không có CRITICAL / HIGH) |

---

## 1. Tuân thủ AGENTS.md rules 1–10

| Rule | Kiểm tra | Kết quả |
|---|---|---|
| 1. No invented numbers | `RfpSummary` không có trường số; `extra="forbid"` chặn `man_day`; `test_llm_schema_no_numbers.py` quét mọi schema | ✅ |
| 2. Structured output + retry ≤ 2 | `complete_with_retry` validate Pydantic, retry `max_retries+1` lần; `test_retry_on_invalid_schema` assert call_count == 3 | ✅ |
| 3. One LLM gateway | `get_llm_client()` factory duy nhất; conftest ép `LLM_PROVIDER=mock`; `_block_real_http` chặn httpx trong test | ✅ |
| 4. Ask instead of guess | Không áp dụng ở M1 (chưa có pipeline) | — |
| 5. Price gate | Không áp dụng ở M1 (chưa có giá) | — |
| 6. Privacy | `mask_text` điểm chặn trong cả 2 client; `RedactingFormatter` chặn key trong log; health không trả key/base_url; quality gate grep guard | ✅ |
| 7. Languages | UI/lỗi tiếng Việt; README tiếng Việt | ✅ |
| 8. Done means proven | `make test` exit 0 + Preview chạy được (test_report TC-M1-01..04) | ✅ |
| 9. Keep it simple | `create_all`, không Alembic/queue/vector DB; deps đúng stack | ✅ |
| 10. Root-relative API | `API_BASE='/api'`; proxy chỉ ở vite config; quality gate grep guard BR-10 | ✅ |

## 2. Conformance contract (api_contract.md §3.0 / spec §2.1)

- `GET /api/health` → HTTP 200, đủ 6 trường, `status` ok/degraded, `app` cố định, `version` khớp `pyproject.toml`, `llm_provider` không lộ key, `database` ok/error tiếng Việt, `time` ISO 8601 UTC. ✅
- Degraded vẫn trả 200 (test `test_health_degraded_when_db_down`). ✅
- FE dùng base root-relative `/api`; menu 3 mục đúng đường dẫn. ✅

## 3. Findings

### MEDIUM

**M1. `backend/app/llm/openai_compat_client.py:77` — `response.json()` nằm ngoài try**
Provider trả HTTP 200 với body không phải JSON → `json.JSONDecodeError` không được bọc thành `LLMProviderError`; gateway sẽ coi đây là lỗi schema và retry (sai ngữ nghĩa). Client này chưa có test (ADR-004 ghi nhận).
*Fix:* bọc `data = response.json()` trong `try/except json.JSONDecodeError` → `raise LLMProviderError(...)`; thêm test đơn vị (mock httpx) cho trường hợp này.

**M2. `backend/app/privacy/mask.py:21-23` — thiếu 2 định dạng SĐT Nhật phổ biến**
- `0123-456-789` (landline Nhật 4 số mã vùng) — không khớp regex nào (JP local yêu cầu 4-4-4, VN group không ăn).
- `0312345678` (10 số liền, Tokyo) — `_JP_UNSEP_RE` yêu cầu 11 số (`0\d{2}\d{4}\d{4}`).
Hai dạng này rất hay gặp trong RFP thật → nguy cơ lọt PII khi gửi LLM (BR-06). Spec §7 đã ghi "mở rộng bộ PII ở M2", nhưng regex bổ sung rẻ và nên làm sớm.
*Fix:* thêm `_JP_LANDLINE4_RE = (?<!\d)0\d{2}-\d{3}-\d{4}(?!\d)` và `_JP_10DIGIT_RE = (?<!\d)0\d{9}(?!\d)` (cẩn thận không nuốt SĐT VN 10 số liền `0912345678` — đã có `_VN_GROUP_RE` chạy sau, thứ tự JP→VN hiện tại giữ đúng); kèm mẫu test.

### LOW

**L1. `backend/app/main.py:33-38` — CORS `allow_origins=["*"]`**
Chấp nhận được ở M1 (chưa auth, không dùng credentials, Preview single-origin). Siết lại danh sách origin khi M2+ có auth.

**L2. `backend/app/api/routers/health.py:44` — `time` serialize `+00:00` (kèm microsecond)**
Ví dụ contract ghi `"2026-10-09T10:00:00Z"`. Cả hai đều hợp lệ ISO 8601; FE chỉ đọc chuỗi nên không ảnh hưởng. Nếu muốn khớp đúng ví dụ: format `%Y-%m-%dT%H:%M:%SZ`.

**L3. `backend/app/llm/gateway.py:62-75` — retry chỉ áp dụng cho lỗi schema**
`LLMProviderError` (mạng/HTTP) không được retry. Đúng phạm vi BR-02 (retry schema), ghi nhận để M2+ cân nhắc retry mạng riêng.

**L4. Mask PII nằm trong từng client (mock + openai_compat), không tập trung**
Thêm client mới quên mask sẽ lọt PII. Cân nhắc chuyển mask vào `complete_with_retry` (điểm chặn duy nhất thực sự) hoặc thêm test cho `OpenAICompatClient` (hiện chưa có — ADR-004).

**L5. `backend/app/models/bid.py:61` — `budget_amount` dùng `Float`**
Tiền nên dùng `Decimal`/int (đơn vị nhỏ nhất) khi bước giá (M7) để tránh sai số. Ghi nhận, không chặn M1 (chỉ lưu trữ).

**L6. `frontend/src/App.test.tsx` — chỉ test trạng thái `ok`**
Thiếu test cho badge `degraded`/`error`. Bổ sung 2 case với `getHealth` mock trả degraded / reject.

**L7. `backend/tests/test_health.py:23-24` — assert `tzinfo` tồn tại nhưng không assert là UTC**
Có thể assert `dt.utcoffset() == timedelta(0)` để khóa đúng "UTC" theo contract.

**L8. `scripts/quality_gate.sh:21-24` — grep BR-06 không loại trừ `docs/`/`.env.example`**
Hiện pass (không có key thật); nếu tài liệu sau này chứa key mẫu sẽ fail — hành vi hợp lý, chỉ lưu ý.

## 4. Điểm tốt

- Điểm chặn mask PII nằm đúng trong `complete()` của từng client — mọi đường gọi đều qua.
- `RedactingFormatter` thay cả giá trị key thật lẫn pattern `sk-`/`Bearer` — phòng key lọt log.
- `conftest.py` ép env mock TRƯỚC khi import app; DB test tách biệt từng test (tmp_path).
- Retry đếm đúng "1 lần đầu + 2 retry" (call_count == 3) — khớp BR-02.
- Quality gate grep guard BR-10/BR-06 hoạt động đúng, không fail oan.
- Không có dead code, không có secret trong repo, không có input surface đáng ngại ở M1.

## 5. Kết luận

**PASS** — không có vấn đề CRITICAL/HIGH. Toàn bộ acceptance criteria và rules AGENTS.md liên quan được đáp ứng và có test chứng minh. Các mục MEDIUM/LOW nên xử lý ở M2 (ưu tiên M2 — regex PII bổ sung; M1 — bọc `response.json()`).

---

**Task Review complete. Awaiting prompt for the next role.**