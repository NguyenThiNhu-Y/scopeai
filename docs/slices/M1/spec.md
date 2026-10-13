# Slice Spec — M1 Foundation

| Thuộc tính | Giá trị |
|---|---|
| Tên tài liệu | Đặc tả milestone M1 — Foundation (slice spec) |
| Phiên bản | 1.0 |
| Ngày | 2026-10-09 |
| Trạng thái | Sẵn sàng cho bước Build |
| Vai trò | Solution Architect |
| Nguồn | `AGENTS.md`, `docs/05_roadmap/roadmap.md` (§3 M1), `docs/04_architecture/` (architecture.md, api_contract.md, data_model.md, llm_pipeline.md), `docs/04_architecture/handoff_to_dev.md`, `docs/03_requirements/srs.md` (NFR-002/003/005/006/008/011, BR-01..03, BR-06, BR-08..10) |
| Ghi chú | `docs/05_roadmap/handoff_to_build.md` chưa tồn tại (milestone đầu tiên) — handoff tương đương là `docs/04_architecture/handoff_to_dev.md`; chưa có code `backend/`/`frontend/` (repo trống ngoài `docs/`) |

---

## 1. Phạm vi (Scope)

### 1.1 Milestone này giao những gì

M1 là **milestone nền tảng** — dựng skeleton hai phía chạy được end-to-end tối thiểu, làm nền cho mọi milestone sau. Theo yêu cầu milestone + roadmap §3:

1. **Backend skeleton (FastAPI, port 8000):** app khởi động được, endpoint `GET /api/health` (định nghĩa contract §3.0), cấu hình env tập trung, log cấm in API key.
2. **LLM gateway 2 chế độ (BR-03, NFR-005):** một interface duy nhất `LLMClient` với `MockLLMClient` (mặc định, dùng cho test/CI/demo) và `OpenAICompatClient` (httpx POST tới `LLM_BASE_URL`), đọc env `LLM_PROVIDER`/`LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL`; validate JSON theo schema + retry ≤ 2 (BR-02); **che PII trước khi gửi** (BR-06, NFR-002).
3. **Bộ test PII (NFR-002):** `privacy/mask.py` che email/SĐT VN + Nhật; bộ test ≥ 50 mẫu, tỷ lệ che ≥ 99%.
4. **SQLite lưu hồ sơ:** kết nối DB (`DATABASE_URL`, mặc định `sqlite:///./data/bidding.db`) + migration tối thiểu — bảng `bids` theo `data_model.md` §2 (entity Hồ sơ dự thầu theo SRS §10).
5. **Frontend skeleton (React + Vite + TS + Tailwind):** layout menu trái với 3 mục **Tạo hồ sơ / Hồ sơ / Cài đặt**; trang chủ gọi `GET /api/health` qua base root-relative `/api` (BR-10) và hiển thị "Backend OK"; 3 trang còn lại là placeholder.
6. **Một lệnh chạy toàn bộ test:** `make test` (backend pytest + frontend vitest + build) + script quality gate `scripts/quality_gate.sh` (pytest + build + grep guards BR-06/BR-10).
7. **README.md** hướng dẫn chạy (cách chạy app, chạy test, cấu hình env LLM_*).
8. **Preview hiển thị được trang chủ** (theo skill `app-preview` — podman-compose; backend :8000, frontend proxy `/api`).

### 1.2 Milestone này KHÔNG gồm những gì (rành mạch)

- ❌ **Không có CRUD hồ sơ** (POST/GET `/api/bids`) — thuộc M2 (FR-001, FR-007). M1 chỉ tạo bảng `bids` trong DB, chưa có endpoint.
- ❌ **Không có pipeline AI** (7 bước, SSE, resume) — thuộc M2 (FR-023). M1 chỉ dựng gateway + schema validation làm nền; demo gọi gateway bằng CLI script, không có endpoint pipeline.
- ❌ **Không có hỏi làm rõ, đánh giá, WBS, effort, giá, duyệt, xuất file, cài đặt** — M2..M8.
- ❌ **Không có auth** — header `X-Role`/`X-User` giả lập chưa cần dùng ở M1 (không có endpoint nhạy cảm); middleware đọc header có thể đặt sẵn nhưng không bắt buộc.
- ❌ **Không có Alembic** — migration dùng `Base.metadata.create_all()` (BR-09 giữ đơn giản); nếu lược đồ phình ra ở milestone sau thì cân nhắc Alembic (ghi nhận rủi ro §7).
- ❌ **Không có CI server** — chỉ có script quality gate cục bộ; CI thật do bước Cloud/Infra dựng sau.
- ❌ **Không có hồ sơ mẫu giả lập** (`sample_data/`) — thuộc M2 (FR-006 phần 1).

---

## 2. Frozen API contract subset (M1)

> Contract gốc: `docs/04_architecture/api_contract.md` (**FROZEN**). M1 chỉ dùng **một** endpoint. Backend và frontend phải bám đúng contract này; mọi thay đổi sau phải qua ADR mới và cập nhật §12.

### 2.1 `GET /api/health` — Health check (M1 — Foundation)

**Mô tả:** Kiểm tra backend còn hoạt động; trả về trạng thái tổng thể, phiên bản, cấu hình LLM (không lộ bí mật) và trạng thái DB. Dùng cho trang chủ (hiển thị "Backend OK") và cho CI/proxy.

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

**Lỗi:** endpoint này luôn trả HTTP 200 (kể cả khi `status=degraded`) để proxy/`curl -f` không fail oan; trạng thái lỗi thể hiện qua trường `status`/`database`.

### 2.2 Thay đổi contract trong M1 (đã ghi vào api_contract.md)

| Thay đổi | Lý do | Ghi chú |
|---|---|---|
| **Bổ sung §3.0** định nghĩa chi tiết `GET /api/health` | §12 đã gán endpoint này cho M1 nhưng contract chưa có định nghĩa — backend/frontend cần contract chung | Không phá vỡ endpoint nào; không đổi §12; ghi chú "Bổ sung M1 2026-10-09" đã thêm vào `api_contract.md` |

### 2.3 Contract chia sẻ backend ↔ frontend (M1)

| Tên | Backend (Pydantic) | Frontend (TypeScript) | Ghi chú |
|---|---|---|---|
| `HealthResponse` | `app/schemas/api_schemas/health.py` — `status: Literal['ok','degraded']`, `app: str`, `version: str`, `llm_provider: Literal['mock','openai_compat']`, `database: str`, `time: datetime` | `src/api/types.ts` — `interface HealthResponse { status: 'ok'\|'degraded'; app: string; version: string; llm_provider: 'mock'\|'openai_compat'; database: string; time: string }` | FE chỉ đọc, không gửi; base URL root-relative `/api` (BR-10) |

---

## 3. LLM steps touched (M1)

### 3.1 Trạng thái

M1 **không triển khai bước pipeline nào** (B1..B7 thuộc M2 trở đi). M1 dựng **tầng gateway + schema validation + mock fixtures** mà mọi bước sẽ dùng. Demo schema dùng lại **schema B1 — RFP summary** (`llm_pipeline.md` §2) vì đơn giản nhất và đã đóng băng.

### 3.2 Interface gateway (BR-03)

```
LLMClient.complete(*, schema: type[BaseModel], prompt: str, context: dict | None = None) -> dict
```

- `get_llm_client() -> LLMClient` — factory đọc env `LLM_PROVIDER`; `mock` → `MockLLMClient`, `openai_compat` → `OpenAICompatClient`.
- **Bắt buộc:** trước khi gửi cho bất kỳ provider nào, `complete()` chạy `privacy/mask.py` trên `prompt` (BR-06) — một điểm chặn duy nhất, không module nào bỏ qua được.
- **Bắt buộc:** output được validate theo `schema` (Pydantic); sai schema → retry ≤ 2 → raise lỗi rõ ràng (BR-02). Lỗi ngữ nghĩa (mã trùng, ±20%...) xử lý ở bước pipeline (M2+), không nằm trong gateway.
- **Cấm:** không module nào ngoài `llm/` được import thư viện LLM hoặc gọi HTTP tới provider; test/CI luôn `LLM_PROVIDER=mock` (BR-03).

### 3.3 Demo schema (B1 — RFP summary) — input/output

**Input (prompt mẫu, đã qua mask PII):**
```
Bạn là trợ lý presales. Tóm tắt RFP sau (đã che PII) thành JSON đúng schema.
<RFP text đã mask — tối đa 8.000 ký tự>
```

**Output JSON schema (Pydantic `RfpSummary`):**
```json
{
  "summary_vi": "string, tóm tắt nội dung RFP bằng tiếng Việt, ≤ 500 từ",
  "keywords": ["string, tối đa 10 từ khóa"],
  "notes": ["string, tối đa 5 điểm cần chú ý"]
}
```

**Validation (code):**
| Rule | Hành vi |
|---|---|
| `summary_vi` không rỗng, ≤ 500 từ | sai → retry ≤ 2 → fail rõ |
| `keywords` ≤ 10, `notes` ≤ 5 | sai → retry ≤ 2 → fail rõ |
| Schema **không chứa trường man-day/giá/ngày** (BR-01) | unit test assert (test_llm_schema_no_numbers.py) |

### 3.4 Mock responses cần cho test

`MockLLMClient` có **registry fixture theo tên schema** + chế độ fixture "xấu" để test retry:

| Fixture | Mục đích test |
|---|---|
| `RfpSummary` hợp lệ (summary_vi đầy đủ, keywords 3, notes 1) | test happy path — trả JSON đúng schema |
| `RfpSummary` sai schema (thiếu `summary_vi`, `keywords` quá 10) | test retry ≤ 2 → fail rõ (BR-02) |
| `RfpSummary` chứa trường số (vd `man_day`) | test BR-01 — assert bị chặn ở schema/validate |
| Fixture "lẫn số tiền" (vd `¥1,000,000` trong `summary_vi`) | dựng sẵn cho M7 (proposal) — M1 chỉ đăng ký, chưa dùng |

Cơ chế: `MockLLMClient(fixture_mode="good"|"bad_schema"|...)` hoặc map theo tên schema; chi tiết do Backend Dev chọn nhưng **phải** đáp ứng đủ các trường hợp trên.

---

## 4. Tasks (file-level)

### 4.1 Backend (Python 3.11 + FastAPI + SQLAlchemy 2.0 + Pydantic v2 + httpx)

Theo `architecture.md` §7 (cấu trúc thư mục) — chỉ tạo phần M1:

| File | Nội dung |
|---|---|
| `backend/requirements.txt` | fastapi, uvicorn[standard], sqlalchemy>=2.0, pydantic>=2, httpx, pytest, pytest-asyncio, httpx (TestClient); **không** thêm dependency ngoài stack (BR-09) |
| `backend/pyproject.toml` | cấu hình pytest (`testpaths=tests`, `addopts=-q`), `app.__version__ = "0.1.0"` |
| `backend/app/__init__.py` | `__version__ = "0.1.0"` |
| `backend/app/main.py` | tạo FastAPI app; lifespan: `init_db()`; include router health; mount prefix `/api` |
| `backend/app/core/config.py` | `Settings` đọc env: `LLM_PROVIDER` (mặc định `mock`), `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `DATABASE_URL` (mặc định `sqlite:///./data/bidding.db`), `APP_ENV`, `LOG_LEVEL`, `LLM_MAX_RETRIES` (mặc định 2). **Cấm** log/in ra giá trị `LLM_API_KEY` (BR-06) |
| `backend/app/core/db.py` | `engine`, `SessionLocal`, `Base(DeclarativeBase)`, `init_db()` = `Base.metadata.create_all(engine)`; tạo thư mục `data/` nếu chưa có |
| `backend/app/core/logging.py` | cấu hình logging; filter chặn in API key |
| `backend/app/models/__init__.py` | import tất cả model để `create_all` thấy |
| `backend/app/models/bid.py` | `Bid` ORM theo `data_model.md` §2 (đầy đủ cột: id, project_name, customer_name, submission_deadline, customer_language CHECK(vi/en/ja), request_content, budget_amount, budget_currency, status DEFAULT 'draft', locked DEFAULT 0, lock_reason, no_requirement_file DEFAULT 0, data_readiness, display_currency DEFAULT 'VND', created_by, created_at, updated_at) |
| `backend/app/schemas/api_schemas/__init__.py` | export `HealthResponse` |
| `backend/app/schemas/api_schemas/health.py` | Pydantic `HealthResponse` (khớp §2.3) |
| `backend/app/schemas/llm_schemas/__init__.py` | export `RfpSummary` |
| `backend/app/schemas/llm_schemas/rfp_summary.py` | Pydantic `RfpSummary` (§3.3) |
| `backend/app/api/routers/__init__.py` | router aggregation |
| `backend/app/api/routers/health.py` | `GET /api/health` — gọi `check_db()` (SELECT 1), đọc `settings.llm_provider`; trả `HealthResponse` (§2.1) |
| `backend/app/llm/__init__.py` | export `get_llm_client`, `LLMClient` |
| `backend/app/llm/gateway.py` | `LLMClient` (Protocol), `get_llm_client()` factory, `complete_with_retry(client, schema, prompt, context, max_retries=2)` — validate + retry ≤ 2 (BR-02) |
| `backend/app/llm/mock_client.py` | `MockLLMClient` + fixture registry (§3.4) |
| `backend/app/llm/openai_compat_client.py` | `OpenAICompatClient` — httpx POST `{LLM_BASE_URL}/chat/completions`, header `Authorization: Bearer {LLM_API_KEY}`, body `{"model": LLM_MODEL, ...}`; không in key |
| `backend/app/privacy/__init__.py` | export `mask_text` |
| `backend/app/privacy/mask.py` | `mask_email`, `mask_phone_vn`, `mask_phone_jp`, `mask_text` (che email + SĐT VN `+84/0xx` + Nhật `0X-XXXX-XXXX/+81`); deterministic |
| `backend/app/llm/demo.py` | CLI demo (`python -m app.llm.demo`): gọi `get_llm_client().complete(schema=RfpSummary, prompt=<văn bản mẫu có email+SĐT>)`, in JSON kết quả + prompt đã mask ra stdout — minh chứng mock + mask (roadmap M1 acceptance b) |
| `backend/tests/conftest.py` | ép `LLM_PROVIDER=mock`; DB test tạm (tmp_path, `sqlite:///`); `TestClient` |
| `backend/tests/test_health.py` | `GET /api/health` → 200, đủ 6 trường, `llm_provider == "mock"`, `database == "ok"` |
| `backend/tests/test_db.py` | `init_db()` tạo bảng `bids` (introspect: tên bảng, cột `status` CHECK, `locked` DEFAULT 0); insert 1 dòng `Bid` hợp lệ → đọc lại được |
| `backend/tests/test_llm_gateway.py` | (1) `get_llm_client()` mặc định trả `MockLLMClient`; (2) mock trả JSON đúng `RfpSummary`; (3) fixture xấu → retry ≤ 2 → lỗi rõ (BR-02); (4) trong test không có request HTTP ra ngoài (monkeypatch httpx, assert không gọi) (BR-03); (5) prompt gửi vào mock đã được mask (BR-06) |
| `backend/tests/test_llm_schema_no_numbers.py` | assert schema output LLM (`RfpSummary` + mọi schema trong `schemas/llm_schemas/`) **không chứa** trường/kiểu man-day, giá, ngày lịch (BR-01) — bản M1 khởi tạo kỷ luật, mở rộng ở M3 |
| `backend/tests/test_pii_mask.py` | bộ ≥ 50 mẫu PII (xem §6), tỷ lệ che ≥ 99% (NFR-002/BR-06) |
| `backend/.env.example` | template env: `LLM_PROVIDER=mock`, `LLM_BASE_URL=`, `LLM_API_KEY=`, `LLM_MODEL=`, `DATABASE_URL=sqlite:///./data/bidding.db` — **không có giá trị key thật** |

### 4.2 Frontend (React 18 + Vite + TypeScript + Tailwind)

| File | Nội dung |
|---|---|
| `frontend/package.json` | react, react-dom, react-router-dom, @tanstack/react-query (theo stack architecture.md §4), typescript, vite, tailwindcss, vitest |
| `frontend/vite.config.ts` | proxy `/api` → `http://127.0.0.1:8000` (**chỉ ở dev config**, không hardcode trong code FE — BR-10) |
| `frontend/tsconfig.json` | strict TS |
| `frontend/tailwind.config.js` | Tailwind |
| `frontend/index.html` | entry, lang="vi", title "Trợ lý dự thầu" |
| `frontend/src/main.tsx` | mount App + QueryClientProvider |
| `frontend/src/App.tsx` | Router + layout: `Sidebar` trái + `<Outlet/>`; routes `/` (trang chủ), `/bids/new` (Tạo hồ sơ), `/bids` (Hồ sơ), `/settings` (Cài đặt) |
| `frontend/src/api/client.ts` | fetch wrapper — **base root-relative `/api`** (BR-10); hàm `getHealth(): Promise<HealthResponse>`; xử lý lỗi hiển thị tiếng Việt |
| `frontend/src/api/types.ts` | `HealthResponse` (§2.3) |
| `frontend/src/hooks/useHealth.ts` | TanStack Query gọi `getHealth`, refetch định kỳ (vd 30s) |
| `frontend/src/components/Sidebar.tsx` | menu trái: **Tạo hồ sơ** (`/bids/new`), **Hồ sơ** (`/bids`), **Cài đặt** (`/settings`); active state; nhãn tiếng Việt (NFR-004) |
| `frontend/src/pages/HomePage.tsx` | trang chủ: badge "Backend OK" (xanh) / "Backend suy giảm" (vàng, khi `status=degraded`) / "Không kết nối được backend" (đỏ) từ `useHealth`; chip "LLM: mock" lấy từ `llm_provider`; hướng dẫn ngắn 3 menu |
| `frontend/src/pages/BidNewPage.tsx` | placeholder "Tạo hồ sơ — sẽ triển khai ở M2" |
| `frontend/src/pages/BidsPage.tsx` | placeholder "Hồ sơ — sẽ triển khai ở M2" |
| `frontend/src/pages/SettingsPage.tsx` | placeholder "Cài đặt — sẽ triển khai ở M8" |
| `frontend/src/App.test.tsx` | Vitest smoke: render App, thấy 3 mục menu, mock `getHealth` trả ok → thấy "Backend OK" |

### 4.3 Root (một lệnh test + README + quality gate)

| File | Nội dung |
|---|---|
| `Makefile` | `make test` = backend pytest + frontend vitest + frontend build (một lệnh chạy toàn bộ test — yêu cầu milestone); `make quality-gate` = chạy `scripts/quality_gate.sh` |
| `scripts/quality_gate.sh` | exit 0 khi: (1) `cd backend && pytest -q`; (2) `cd frontend && npm run build`; (3) grep guard BR-10: không có `http://localhost` trong `frontend/src/`; (4) grep guard BR-06: không có pattern key (`LLM_API_KEY=`, `sk-`, `Bearer `) trong file commit (loại trừ `.env.example`/docs) |
| `README.md` | hướng dẫn: yêu cầu môi trường, cài đặt backend/frontend, cấu hình env `LLM_*`/`DATABASE_URL`, chạy app (`uvicorn app.main:app --port 8000` + `npm run dev`), chạy test (`make test`), chạy demo mock LLM (`python -m app.llm.demo`), trỏ tới `docs/`; **tiếng Việt** (NFR-004) |
| `.gitignore` | bổ sung: `backend/.venv/`, `backend/data/`, `frontend/node_modules/`, `frontend/dist/`, `.env`, `*.db` |
| `compose.yml` (theo skill `app-preview`) | backend uvicorn :8000 + frontend serve static/proxy `/api` — chi tiết theo skill `app-preview` của bước Build |

### 4.4 Shared contract giữa backend ↔ frontend (M1)

- **Một endpoint duy nhất:** `GET /api/health` (§2.1) — FE gọi qua `client.ts` base `/api`; BE trả `HealthResponse` (§2.3).
- **Cấu hình LLM:** BE đọc env `LLM_*`; FE **không** đọc env LLM — chỉ hiển thị `llm_provider` từ health response.
- **Ngôn ngữ:** mọi chuỗi UI/lỗi tiếng Việt (NFR-004); không chuỗi tiếng Anh thô (trừ thuật ngữ kỹ thuật).

---

## 5. Acceptance criteria

### (a) Shell commands — bắt buộc exit 0

```bash
# Một lệnh chạy TOÀN BỘ test (yêu cầu milestone)
make test

# Tương đương — từng phần (cho CI/dev)
cd backend && pytest -q                                          # toàn bộ test backend (mock LLM)
cd backend && LLM_PROVIDER=mock pytest -q tests/test_llm_gateway.py
cd backend && pytest -q tests/test_pii_mask.py                   # ≥ 50 mẫu, tỷ lệ che ≥ 99%
cd frontend && npm run build                                     # type-check + build production
curl -f http://localhost:8000/api/health                         # backend đang chạy → 200

# Quality gate (CI sơ bộ)
make quality-gate
```

> Lưu ý: roadmap §3 viết `tests/test_pii.py`; chuẩn hóa là **`tests/test_pii_mask.py`** (khớp `architecture.md` §6.3 và module `privacy/mask.py`). Port 8000 theo `architecture.md` §6.

### (b) Manual scenario (Preview) — từng bước + kết quả mong đợi

Chạy stack theo skill `app-preview` (podman-compose; backend :8000, frontend proxy `/api`).

| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| 1 | Mở app (Preview) | Trang chủ hiển thị badge **"Backend OK"** (xanh) — dữ liệu từ `GET /api/health` qua proxy `/api`; chip **"LLM: mock"**; menu trái có 3 mục: **Tạo hồ sơ, Hồ sơ, Cài đặt** |
| 2 | Bấm **Tạo hồ sơ** | Trang placeholder "Tạo hồ sơ — sẽ triển khai ở M2" hiển thị; menu active chuyển đúng |
| 3 | Bấm **Hồ sơ** | Trang placeholder "Hồ sơ — sẽ triển khai ở M2" hiển thị |
| 4 | Bấm **Cài đặt** | Trang placeholder "Cài đặt — sẽ triển khai ở M8" hiển thị |
| 5 | (Dev/CLI) `cd backend && python -m app.llm.demo` | In ra JSON đúng schema `RfpSummary` từ **mock** (không gọi LLM thật); prompt in ra đã che email/SĐT (vd `[EMAIL]`, `[PHONE_VN]`) |
| 6 | (Dev/CLI) Đổi `LLM_PROVIDER=openai_compat` + `LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL` trong `.env.preview`, restart backend | `GET /api/health` trả `llm_provider: "openai_compat"`; demo gọi endpoint tương thích OpenAI (chỉ dev — Preview mặc định mock) |

### (c) Test chứng minh từng rule AGENTS.md liên quan M1

| Rule AGENTS.md | Test bắt buộc | Assert chính |
|---|---|---|
| **1. No invented numbers** | `tests/test_llm_schema_no_numbers.py` | Mọi schema output LLM không chứa trường man-day/giá/ngày (BR-01) |
| **2. Structured LLM output** | `tests/test_llm_gateway.py::test_retry_on_invalid_schema` | Fixture xấu → retry ≤ 2 → lỗi rõ (BR-02) |
| **3. One LLM gateway** | `tests/test_llm_gateway.py::test_mock_default_and_no_http` | Test dùng `LLM_PROVIDER=mock`; monkeypatch httpx → không có request HTTP; `get_llm_client()` trả `MockLLMClient` (BR-03) |
| **6. Privacy** | `tests/test_pii_mask.py` + `scripts/quality_gate.sh` | ≥ 50 mẫu, tỷ lệ che ≥ 99%; grep guard không có key trong repo; `LLM_API_KEY` không in ra log/health (BR-06, NFR-002) |
| **8. Done means proven** | `make test` exit 0 + kịch bản (b) | Cả test tự động lẫn Preview đều pass (BR-08) |
| **9. Keep it simple** | review + `tests/test_db.py` | Không dependency ngoài stack; migration bằng `create_all`, không Alembic/queue/vector DB (BR-09, NFR-008) |
| **10. Frontend networking** | `scripts/quality_gate.sh` (grep guard) + `frontend/src/App.test.tsx` | Không `http://localhost` trong `frontend/src/`; base root-relative `/api` (BR-10, NFR-011) |

---

## 6. Test data

- **Bộ PII (≥ 50 mẫu)** — đặt tại `backend/tests/fixtures/pii_samples.py` (dữ liệu 100% hư cấu, ghi chú "giả lập" — BR-06). Phân bố:
  - Email: 15 mẫu (địa chỉ thường, miền `.co.jp`, `.vn`, viết hoa, có dấu chấm/`+tag`, email lẫn trong câu tiếng Nhật).
  - SĐT VN: 15 mẫu (`+84 912 345 678`, `0912345678`, `(+84)912345678`, có/hết dấu gạch, lẫn trong câu).
  - SĐT Nhật: 15 mẫu (`03-1234-5678`, `090-1234-5678`, `+81 3-1234-5678`, `08012345678`, lẫn trong văn bản tiếng Nhật).
  - Văn bản hỗn hợp: 5 mẫu (email + SĐT VN + SĐT Nhật trong một đoạn tiếng Việt/Nhật).
  - Negative: 5 mẫu (số không phải SĐT — ngày tháng, mã số, số lượng — **không được** che nhầm).
  - **Tỷ lệ che ≥ 99%** trên toàn bộ 50 mẫu (NFR-002).
- **Không cần `samples/` ở M1:** hồ sơ mẫu giả lập (FR-006) thuộc M2 (đặt `sample_data/` theo `architecture.md` §7); PII fixtures nằm cạnh test như trên.

---

## 7. Rủi ro & ghi chú cho milestone sau

| Rủi ro / ghi chú | Mức | Giảm thiểu / hành động |
|---|---|---|
| `create_all` không alter bảng cũ khi lược đồ đổi ở M2+ | Thấp | M2+ thêm bảng mới thì `create_all` vẫn tạo được; nếu đổi cột bảng cũ → cân nhắc Alembic (quyết định ở M2) |
| Mock fixture "quá ngoan" → sót lỗi thật (ADR-004 risk) | Trung bình | Registry fixture xấu (sai schema, lẫn số) dựng sẵn từ M1; M2+ bổ sung fixture theo từng bước pipeline |
| `OpenAICompatClient` chưa được test với LLM thật | Trung bình | M1 chỉ test bằng mock; smoke test `openai_compat` ở milestone cuối (ADR-004) |
| Quality gate mới ở mức script cục bộ | Thấp | Bước Cloud/Infra dựng CI thật dùng `scripts/quality_gate.sh` |
| `docs/05_roadmap/handoff_to_build.md` chưa tồn tại | — | Handoff cho bước Build là chính file này + `docs/04_architecture/handoff_to_dev.md` |
| Bộ test PII cần mở rộng ở M2 (email trong file Excel, SĐT định dạng lạ) | Trung bình | Fixture tách file `pii_samples.py` để thêm mẫu không sửa code test |

---

**Task Slice Spec (M1) complete. Awaiting prompt for the next role.**