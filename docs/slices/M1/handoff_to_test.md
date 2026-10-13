# Handoff — Coordinator → Tester (M1 Foundation)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Parallel Dispatch Coordinator (Backend Dev + Frontend Dev đã chạy song song, đã reconcile) |
| Cho | Tester (bước tiếp theo) |
| Ngày | 2026-10-09 |
| Nguồn | `docs/slices/M1/spec.md`, `docs/slices/M1/handoff_to_build.md`, code `backend/` + `frontend/` |

---

## 1. Đã build những gì (M1 — Foundation)

| Phần | Nội dung | Trạng thái |
|---|---|---|
| **Backend** (`backend/`) | FastAPI :8000, `GET /api/health` (contract đóng băng), LLM gateway 2 chế độ (`MockLLMClient` mặc định + `OpenAICompatClient` httpx, đọc `LLM_*`), validate schema + retry ≤ 2, `privacy/mask.py` che PII trước khi gửi, SQLite + bảng `bids` (`create_all`, không Alembic), CORS `*` (Preview), CLI demo `python -m app.llm.demo` | ✅ 18 test pass |
| **Frontend** (`frontend/`) | React 18 + Vite + TS + Tailwind; menu trái **Tạo hồ sơ / Hồ sơ / Cài đặt**; trang chủ gọi `/api/health` (base root-relative, BR-10) hiển thị "Backend OK" + chip "LLM: mock"; 3 trang placeholder; Vitest smoke test | ✅ build + 2 test pass |
| **Root** | `Makefile` (`make test` = MỘT lệnh chạy toàn bộ test; `make run`; `make quality-gate`; `make preview`), `scripts/quality_gate.sh`, `README.md`, `.gitignore` (thêm `backend/data/`, `*.db`, `.vibeflow-preview.hash`) | ✅ `make test` + `make quality-gate` pass |
| **Preview** | `podman-compose.preview.vibeflow.yaml` + `frontend/vite.preview.config.ts` — backend :8000 (không publish port) + frontend :5173 (proxy `/api` → backend:8000, publish duy nhất) | ✅ Đang chạy |

## 2. Cách chạy

```bash
# Toàn bộ test — MỘT lệnh
make test

# Quality gate (CI-style)
make quality-gate

# Chạy app local (dev)
make run                # backend :8000 + frontend :5173 (Ctrl+C dừng)

# Preview (podman-compose)
make preview            # = podman-compose -f podman-compose.preview.vibeflow.yaml up --build -d
```

- Preview hiện đang chạy: frontend `http://127.0.0.1:5173` (qua proxy VibeFlow → tab Preview), `/api/health` proxy về backend.
- Backend không publish port trực tiếp (một origin duy nhất — theo skill app-preview).

## 3. Kịch bản test tay (Preview) — spec §5(b)

| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| 1 | Mở app (Preview) | Badge **"Backend OK"** (xanh), chip **"LLM: mock"**, menu trái 3 mục **Tạo hồ sơ / Hồ sơ / Cài đặt** |
| 2 | Bấm **Tạo hồ sơ** | Placeholder "Tạo hồ sơ — sẽ triển khai ở M2" |
| 3 | Bấm **Hồ sơ** | Placeholder "Hồ sơ — sẽ triển khai ở M2" |
| 4 | Bấm **Cài đặt** | Placeholder "Cài đặt — sẽ triển khai ở M8" |
| 5 | (CLI) `cd backend && python -m app.llm.demo` | JSON đúng schema `RfpSummary` từ **mock** (không gọi LLM thật); prompt đã che email/SĐT |

## 4. E2E đã kiểm chứng (bởi Coordinator)

- `curl http://127.0.0.1:5173/` → **200**; `curl http://127.0.0.1:5173/api/health` → `{"status":"ok","app":"presales-bidding-assistant","version":"0.1.0","llm_provider":"mock","database":"ok","time":"..."}` — frontend thật sự nói chuyện với backend qua proxy, mock LLM.
- Playwright (headless): trang chủ render **"Backend OK"** + 3 menu + chip **"LLM: mock"** — không lỗi console nào của app (1 cảnh báo `ERR_CERT_AUTHORITY_INVALID` do Google Fonts bị chặn trong sandbox — fallback font hệ thống, không ảnh hưởng).

## 5. Known gaps / lưu ý cho Tester

1. **Google Fonts** (Be Vietnam Pro) tải từ CDN — bị chặn trong sandbox → fallback font hệ thống; không phải lỗi app.
2. **`OpenAICompatClient` chưa test với LLM thật** — M1 chỉ test bằng mock (đúng BR-03); smoke test `openai_compat` để milestone cuối (ADR-004).
3. **PII fixtures** dùng định dạng số "an toàn" (`0xx`, `(+84)`, `0X-XXXX-XXXX`) do môi trường redact dãy `+84/+81` khi ghi file — code mask xử lý đủ định dạng, tỷ lệ che 100% (50/50); cần mở rộng bộ mẫu ở M2.
4. **`rtk` wrapper của môi trường làm hỏng `pytest`** ("No tests collected") — luôn chạy `pytest`/`python3 -m pytest` trực tiếp (Makefile đã dùng trực tiếp, không qua wrapper).
5. **Migration `create_all`** không alter bảng cũ — nếu M2+ đổi cột bảng `bids` cần Alembic (quyết định ở M2).
6. **Chưa có CRUD hồ sơ / pipeline / SSE** — thuộc M2; M1 chỉ là nền tảng (health + gateway + DB + layout).
7. Preview files (`podman-compose.preview.vibeflow.yaml`, `vite.preview.config.ts`) **được commit** theo skill app-preview; `.vibeflow-preview.hash` không commit (đã gitignore).

---

**Task Build complete. Awaiting prompt for the next role.**