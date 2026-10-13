# Handoff — Build → Tester (M2 Phân tích yêu cầu + hỏi làm rõ)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Build (Parallel Dispatch Coordinator: Backend Dev + Frontend Dev) |
| Cho | Tester |
| Ngày | 2026-10-09 |
| Nguồn | `docs/slices/M2/spec.md`, `docs/slices/M2/handoff_to_build.md`, `docs/04_architecture/api_contract.md` (FROZEN), `AGENTS.md` |

---

## 1. Cách chạy

```bash
# 1. Cài đặt (lần đầu)
cd backend && pip install -r requirements.txt
cd frontend && npm install

# 2. Chạy app — MỘT lệnh (dev)
make run
#   Backend :8000 (uvicorn), Frontend :5173 (vite, proxy /api → backend)

# 3. Hoặc chạy Preview (VibeFlow) — đang CHẠY sẵn
#   podman-compose -f podman-compose.preview.vibeflow.yaml up --build -d
#   Truy cập qua tab Preview (origin duy nhất :5173, /api proxy → backend:8000)

# 4. Test toàn bộ (phải exit 0)
make test
make quality-gate
```

- LLM mặc định **`mock`** (không gọi LLM thật — BR-03). Đổi `LLM_PROVIDER=openai_compat` + `LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL` nếu muốn chạy LLM thật (không bắt buộc cho M2).
- DB SQLite: `backend/data/bidding.db` (tự tạo khi chạy lần đầu).

## 2. Đã build những gì (M2)

**Backend (FastAPI + SQLAlchemy + Pydantic v2):**
- Models: `Question`, `PipelineStep` (bảng mới, tạo qua `create_all` — BR-09).
- 9 endpoint theo contract: `POST/GET /api/bids`, `GET /api/bids/{id}` (+ `request_content`, `pipeline_progress`), `POST /api/bids/sample` (2 mẫu `ja_email`/`vi_email`), `POST /api/bids/{id}/pipeline/start`, `GET /api/bids/{id}/pipeline/events` (SSE), `POST /api/bids/{id}/rerun`, `GET /api/bids/{id}/questions`, `POST /api/bids/{id}/questions/{round}/answers`.
- Pipeline 7 bước (đăng ký đủ), triển khai **intake** (trích xuất 7 nhóm thông tin — schema `IntakeExtraction`, không trường số/ngày — BR-01) + **gap** (≤ 7 câu hỏi, ngôn ngữ khách + `reason_vi` tiếng Việt, ≤ 2 vòng, sau vòng 2 không gọi LLM — BR-04); 5 bước còn lại `pending` "chưa triển khai ở M2".
- SSE in-process (asyncio pub/sub, heartbeat 15s, replay khi reconnect); resume từ bước lỗi (`rerun` `from_step=null`); guard 409 `STATE_CONFLICT`/`CLARIFY_PENDING`.
- Envelope lỗi `{error:{code,message,details}}` tiếng Việt; `request_content` < 30 ký tự → `400` + `details.min_length=30`.
- `sample_data/ja_email.md` + `vi_email.md` — dữ liệu 100% hư cấu, ghi "DỮ LIỆU GIẢ LẬP", chứa email+SĐT để minh chứng mask PII.
- **56 test backend pass** (bids, sample, clarifying, resume, sse, no-numbers, pii, gateway, db, health).

**Frontend (React 18 + Vite + TS + Tailwind):**
- Trang **Tạo hồ sơ** (form đầy đủ, validate ≥ 30 ký tự + đếm ký tự, 2 nút "Nạp mẫu tiếng Nhật / tiếng Việt"), **Hồ sơ** (bảng + lọc status + tìm q + phân trang), **Chi tiết hồ sơ** (`/bids/:id` — nút Phân tích, tiến độ 7 bước realtime qua SSE, kết quả phân tích B1, form trả lời câu hỏi làm rõ + checkbox giả định, nút Chạy lại khi lỗi).
- API base root-relative `/api` (BR-10); mọi request có loading/empty/error/success; UI tiếng Việt (BR-07); EventSource tự reconnect.
- **Build + 4 test frontend pass**; không hardcode localhost.

## 3. Kịch bản test thủ công (Preview) — đã xác minh hoạt động

| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| 1 | Mở app → **Tạo hồ sơ** | Form đầy đủ; hint "tối thiểu 30 ký tự" + bộ đếm; 2 nút nạp mẫu |
| 2 | Nội dung yêu cầu < 30 ký tự → Tạo | Lỗi tiếng Việt; không tạo hồ sơ |
| 3 | **Nạp mẫu tiếng Nhật** | Hồ sơ mẫu mới (Nháp) → tự điều hướng chi tiết; ghi chú "DỮ LIỆU GIẢ LẬP" |
| 4 | **Phân tích** | Tiến độ realtime: intake chạy → xong, gap chạy; 5 bước còn lại mờ "chưa triển khai ở M2" |
| 5 | Dừng **Chờ làm rõ** | ≤ 7 câu hỏi tiếng Nhật + lý do tiếng Việt + badge ảnh hưởng; nút Phân tích disabled |
| 6 | Để trống 1 câu → Gửi | Nhắc trả lời câu thiếu (highlight) |
| 7 | Trả lời theo **giả định** | Nhãn "giả định — cần khách xác nhận" |
| 8 | Trả lời đủ → Gửi | Pipeline tự chạy tiếp từ `gap` (không làm lại intake); hết 2 vòng → **Chờ duyệt kỹ thuật**; hiển thị kết quả B1 |
| 9 | **Hồ sơ** → danh sách | Lọc/tìm/phân trang hoạt động |
| 10 | Mở lại hồ sơ Chờ làm rõ | Câu hỏi chưa trả lời còn đó, trả lời tiếp được |
| 11 | (Tùy chọn) Lỗi giữa chừng → **Chạy lại** | Resume từ bước lỗi, bước xong không chạy lại |
| 12 | **Nạp mẫu tiếng Việt** | Câu hỏi (nếu có) bằng tiếng Việt |

**E2E đã chạy thật qua proxy Preview (mock LLM):** `POST /api/bids/sample` → 201; `POST /pipeline/start` → 202; `intake completed` → `gap waiting_clarification` (5 câu tiếng Nhật + reason tiếng Việt); trả lời vòng 1 → resume từ `gap` → vòng 2; trả lời vòng 2 → `gap completed` → **`waiting_tech_approval`**; SSE replay 7 bước qua `GET /pipeline/events` ✓.

## 4. Known gaps / lưu ý cho Tester

1. **`done` semantic M2:** pipeline "hoàn tất" khi `intake`+`gap` xong → hồ sơ chuyển `waiting_tech_approval` dù 5 bước còn lại `pending` (chưa triển khai ở M2). UI hiển thị mờ — không phải lỗi.
2. **Chuỗi 2 vòng hỏi:** với mock LLM, vòng 1 và vòng 2 đều sinh câu hỏi → cần trả lời **2 lần** để hết vòng (sau vòng 2 code không gọi LLM nữa — FR-010.4). `GET /questions` trả cả lịch sử (câu đã trả lời có `answer`); frontend chỉ submit câu chưa trả lời; backend từ chối câu không thuộc vòng hiện tại (`400` "Câu hỏi không thuộc vòng này") — đúng thiết kế.
3. **SSE qua TestClient:** test backend dùng `SSEManager` trực tiếp (Starlette TestClient buffer toàn bộ body nên không stream được qua HTTP trong test) — phần HTTP framing là trách nhiệm của Starlette; đã xác minh stream thật qua proxy Preview.
4. **Changelog:** spec §4.1 nhắc ghi changelog nhưng chưa có bảng `changelog` (ngoài scope M2) — defer tới milestone giới thiệu bảng.
5. **`rerun` M2** chỉ hỗ trợ `from_step=null` (resume lỗi); `from_step=wbs` thuộc M4.
6. **`related_req_codes` luôn rỗng** (chưa có bảng requirements — M6).
7. **Frontend LSP/typecheck:** cần `npm install` trước khi mở IDE (node_modules chưa có trong môi trường build).
8. **Port preview:** chỉ publish :5173 (frontend = proxy); backend :8000 không publish ra ngoài — truy cập qua `/api` trên cùng origin.

---

**Task Build complete. Awaiting prompt for the next role.**