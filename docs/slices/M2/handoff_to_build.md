# Handoff — Solution Architect → Build (M2 Phân tích yêu cầu + hỏi làm rõ)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Solution Architect |
| Cho | Backend Dev, Frontend Dev, Cloud/Infra (bước tiếp theo) |
| Ngày | 2026-10-09 |
| Nguồn | `docs/slices/M2/spec.md`, `docs/04_architecture/` (4 file), `docs/05_roadmap/roadmap.md` §4, `docs/03_requirements/srs.md` (FR-001/006*/007/010/011/023), `AGENTS.md` |

---

## 1. Việc cần làm (tóm tắt)

Dựng **M2 — Phân tích yêu cầu + hỏi làm rõ** theo `docs/slices/M2/spec.md` (kế thừa M1 đã xong):

1. **Hồ sơ (FR-001, FR-007):** `POST /api/bids` (request_content **≥ 30 ký tự**), `GET /api/bids` (lọc status, tìm q, phân trang), `GET /api/bids/{id}` (+ `pipeline_progress`); UI tạo hồ sơ + danh sách + mở lại.
2. **Pipeline M2 (FR-023):** orchestrator đăng ký **7 bước**, triển khai **2 bước** — B1 Intake (trích xuất 7 nhóm thông tin, schema `IntakeExtraction`) và B2 Gap (≤ 7 câu hỏi, ngôn ngữ khách + lý do tiếng Việt, ≤ 2 vòng); 5 bước còn lại `pending` "chưa triển khai ở M2"; persist từng bước; **resume từ bước lỗi** (`rerun` `from_step=null`).
3. **Hỏi làm rõ (FR-010, FR-011):** `GET /api/bids/{id}/questions`, `POST /api/bids/{id}/questions/{round}/answers` (thiếu câu → `missing_ids`; giả định → `is_assumption`); trả lời đủ → pipeline tự chạy tiếp từ `gap`.
4. **SSE (FR-023, NFR-001):** `GET /api/bids/{id}/pipeline/events` — event `step`/`clarify`/`error`/`done`/`heartbeat`; cập nhật ≤ 5s; in-process (asyncio), không WebSocket/broker.
5. **Hồ sơ mẫu (FR-006 phần 1):** `POST /api/bids/sample` với **2 mẫu text** (`sample_data/ja_email.md`, `sample_data/vi_email.md`) — hư cấu, ghi "giả lập".
6. **Fixture:** bộ PII mở rộng (≥ 10 mẫu email/SĐT trong thân email) + **20 câu tiếng Nhật** (`tests/fixtures/ja_samples.py`) cho FR-025 (dùng ở M7).

## 2. Bắt buộc tuân theo

- **Contract FROZEN + 3 thay đổi đã ghi vào `api_contract.md`** (spec §2.2):
  1. `request_content` tối thiểu **30 ký tự** (§3.1, `details.min_length=30`);
  2. **`POST /api/bids/sample`** — path cũ `POST /api/bids/{id}/sample` đã sửa (FR-006 tạo hồ sơ mẫu **mới**); `sample_key` ∈ {`ja_email`, `vi_email`};
  3. §12 cập nhật theo.
- **BR-01 (nhạy nhất):** schema LLM B1 (`IntakeExtraction`) **không chứa trường số/ngày** — ngân sách/thời hạn trích xuất là **ghi chú văn bản** (`budget_note_vi`/`deadline_note_vi`) + boolean; mở rộng `test_llm_schema_no_numbers.py`.
- **BR-02:** mọi output LLM validate schema, retry ≤ 2, fail rõ.
- **BR-03:** mọi bước pipeline gọi qua gateway `complete_with_retry`; test/CI `LLM_PROVIDER=mock`.
- **BR-04:** `needs_clarification=true` → bid `waiting_clarification`, pipeline dừng; **vòng ≤ 2** — sau vòng 2 **không gọi LLM**; trả lời thiếu → `400` + `details.missing_ids`.
- **BR-06:** `request_content` mask PII trước khi vào prompt (gateway đã chặn từ M1); mẫu giả lập hư cấu.
- **BR-07/NFR-004:** câu hỏi bằng **ngôn ngữ khách** + lý do **tiếng Việt**; UI/lỗi tiếng Việt.
- **BR-10:** FE base root-relative `/api`; không hardcode localhost.
- **BR-09:** SSE in-process (asyncio queue), không thêm hạ tầng; migration `create_all` (chỉ thêm bảng mới `questions`, `pipeline_steps`).

## 3. Contract chia sẻ BE ↔ FE (M2)

- **9 endpoint** (spec §2.1): POST/GET `/api/bids`, GET `/api/bids/{id}`, POST `/api/bids/sample`, POST `/api/bids/{id}/pipeline/start`, GET `/api/bids/{id}/pipeline/events` (SSE), POST `/api/bids/{id}/rerun`, GET `/api/bids/{id}/questions`, POST `/api/bids/{id}/questions/{round}/answers`.
- **Shape `pipeline_progress`** (làm rõ, không phá vỡ contract): `{steps:[{step_key,status}], waiting_clarification, rounds_used, max_rounds}` — spec §2.1.
- **SSE event names + JSON `data:`** theo contract §5.2 (spec §2.1): `step`/`clarify`/`error`/`done`/`heartbeat`.
- **Trạng thái hồ sơ:** `draft → analyzing → waiting_clarification → analyzing → waiting_tech_approval` (nhãn tiếng Việt: Nháp / Đang phân tích / Chờ làm rõ / Chờ duyệt kỹ thuật).

## 4. Acceptance (phải exit 0)

```bash
make test
cd backend && pytest -q
cd frontend && npm run build
curl -f http://localhost:8000/api/bids
curl -f http://localhost:8000/api/bids/1
cd backend && LLM_PROVIDER=mock pytest -q tests/test_clarifying_questions.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_pipeline_resume.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_pipeline_sse.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_bids.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_sample_data.py
cd backend && pytest -q tests/test_llm_schema_no_numbers.py
cd backend && pytest -q tests/test_pii_mask.py
make quality-gate
```

Kịch bản Preview: spec §5(b) — 12 bước (tạo hồ sơ → lỗi < 30 ký tự → nạp mẫu Nhật → Phân tích → Chờ làm rõ → trả lời thiếu/giả định → resume → danh sách → mở lại → rerun lỗi → mẫu Việt).

## 5. Điểm cần lưu ý

- **`done` semantic của M2:** pipeline "hoàn tất" khi `intake` + `gap` xong; bid chuyển `waiting_tech_approval`; 5 bước còn lại `pending` hiển thị mờ "chưa triển khai ở M2". **Handoff M3:** kích hoạt bước mới phải chuyển bid `waiting_tech_approval → analyzing` rồi chạy từ bước `pending` đầu tiên.
- **"Câu hỏi chặn"** (yêu cầu milestone) = mọi câu hỏi sinh ra đều chặn pipeline (FR-010.3) — **không thêm** trường `is_blocking` vào schema (tránh phá vỡ contract).
- **`related_req_codes` luôn rỗng ở M2** (chưa có bảng requirements — M6); prompt dặn LLM không sinh mã; bỏ qua kiểm tra tồn tại khi danh sách requirement rỗng.
- Lỗi `400` "chưa xác nhận parse" của §5.1 **chưa áp dụng** ở M2 (không có attachments).
- `rerun` M2 chỉ hỗ trợ `from_step=null` (resume lỗi); `from_step=wbs` thuộc M4.
- Bảng mới `questions`, `pipeline_steps` tạo bằng `create_all` (không đổi cột bảng cũ — an toàn).
- Sau khi build xong: chạy đủ test + kịch bản Preview, tự review, ghi handoff cho milestone M3 và dừng.

---

**Task Slice Spec (M2) complete. Awaiting prompt for the next role.**