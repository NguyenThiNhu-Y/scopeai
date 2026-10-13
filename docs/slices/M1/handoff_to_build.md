# Handoff — Solution Architect → Build (M1 Foundation)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Solution Architect |
| Cho | Backend Dev, Frontend Dev, Cloud/Infra (bước tiếp theo) |
| Ngày | 2026-10-09 |
| Nguồn | `docs/slices/M1/spec.md`, `docs/04_architecture/` (4 file), `docs/05_roadmap/roadmap.md` §3, `AGENTS.md` |

---

## 1. Việc cần làm (tóm tắt)

Dựng **M1 — Foundation** theo `docs/slices/M1/spec.md`:

1. **Backend (FastAPI, port 8000):** `GET /api/health` (contract §2.1), cấu hình env tập trung, log cấm in key.
2. **LLM gateway 2 chế độ:** `LLMClient` (Protocol) + `MockLLMClient` (mặc định) + `OpenAICompatClient` (httpx, đọc `LLM_*`), validate schema + retry ≤ 2, **che PII trước khi gửi**.
3. **Bộ test PII ≥ 50 mẫu, tỷ lệ ≥ 99%** (`tests/test_pii_mask.py` + `tests/fixtures/pii_samples.py`).
4. **SQLite:** kết nối + bảng `bids` (đầy đủ theo `data_model.md` §2) qua `Base.metadata.create_all()` — **không Alembic**.
5. **Frontend (React+Vite+TS+Tailwind):** menu trái **Tạo hồ sơ / Hồ sơ / Cài đặt**, trang chủ gọi `/api/health` (base root-relative, BR-10) hiển thị "Backend OK".
6. **Một lệnh test:** `make test` + `scripts/quality_gate.sh` (pytest + build + grep guards BR-06/BR-10).
7. **README.md** hướng dẫn chạy (tiếng Việt).
8. **Preview hiển thị trang chủ** (theo skill `app-preview`).

## 2. Bắt buộc tuân theo

- **Contract FROZEN:** chỉ endpoint M1 là `GET /api/health` (đã bổ sung §3.0 vào `api_contract.md` — ghi chú thay đổi kèm lý do). Không thêm/bớt endpoint.
- **BR-03:** mọi lời gọi LLM qua gateway; test/CI luôn `LLM_PROVIDER=mock`; không module nào ngoài `llm/` gọi LLM trực tiếp.
- **BR-02:** validate JSON theo Pydantic schema; retry ≤ 2; lỗi schema → fail rõ.
- **BR-01:** schema output LLM không chứa man-day/giá/ngày — có test `test_llm_schema_no_numbers.py` ngay từ M1.
- **BR-06:** `complete()` phải mask PII trước khi gửi (một điểm chặn duy nhất); không commit/in API key; dữ liệu mẫu giả lập.
- **BR-10:** FE base root-relative `/api`; proxy `/api` → `http://127.0.0.1:8000` chỉ trong `vite.config.ts`; grep guard cấm `http://localhost` trong `frontend/src/`.
- **BR-09:** không dependency ngoài stack; không Alembic/queue/vector DB.
- **Stack:** Python 3.11 + FastAPI + uvicorn (port 8000) + SQLAlchemy 2.0 + Pydantic v2 + httpx; React 18 + Vite + TS + Tailwind + TanStack Query. (Chi tiết `architecture.md` §4.)

## 3. Contract chia sẻ BE ↔ FE (M1)

- `GET /api/health` → `HealthResponse`: `{status: ok|degraded, app, version, llm_provider: mock|openai_compat, database, time}` (chi tiết spec §2.3).
- FE chỉ hiển thị `llm_provider` từ health; **không** đọc env `LLM_*` ở FE.

## 4. Acceptance (phải exit 0)

```bash
make test
cd backend && pytest -q
cd backend && LLM_PROVIDER=mock pytest -q tests/test_llm_gateway.py
cd backend && pytest -q tests/test_pii_mask.py
cd frontend && npm run build
curl -f http://localhost:8000/api/health
make quality-gate
```

Kịch bản Preview: spec §5(b) — trang chủ "Backend OK" + chip "LLM: mock", 3 menu điều hướng được.

## 5. Điểm cần lưu ý

- Roadmap viết `tests/test_pii.py` → chuẩn hóa **`tests/test_pii_mask.py`** (khớp `architecture.md` §6.3).
- `docs/05_roadmap/handoff_to_build.md` chưa tồn tại (milestone đầu) — handoff nền là `docs/04_architecture/handoff_to_dev.md`.
- Chưa có code `backend/`/`frontend/` — dựng mới theo cấu trúc `architecture.md` §7 (chỉ phần M1, spec §4).
- `compose.yml` Preview theo skill `app-preview` (backend :8000 + frontend proxy `/api`).
- Sau khi build xong: chạy đủ test + kịch bản Preview, tự review, ghi handoff cho milestone M2 và dừng.

---

**Task Slice Spec (M1) complete. Awaiting prompt for the next role.**