# Presales Bidding Assistant

Web app hỗ trợ presales làm hồ sơ dự thầu: phân tích yêu cầu khách, hỏi làm rõ, chọn hướng giải pháp, tính effort bằng code, dựng WBS + lịch, báo giá, soạn proposal và xuất bộ hồ sơ. **Milestone hiện tại: M7 — xuất Word/Excel/PDF hoặc ZIP bằng code** (báo giá do code tính từ rate card giả lập; artifact giữ price gate; frontend gọi API root-relative).

> Tài liệu đầy đủ: `docs/` (SRS, kiến trúc, API contract, roadmap, slice spec tại `docs/slices/M1/`…`docs/slices/M4/`).

## Yêu cầu môi trường

- Python 3.11+
- Node.js 18+ (npm)
- `make`

## Cài đặt

```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

## Chạy app trong Preview (một lệnh)

```bash
make preview
```

- Trong VibeFlow, dùng nút **Preview** hoặc `make preview`. Stack production chạy frontend qua proxy `/api` tới backend; không truy cập trực tiếp bằng localhost.
- Bắt đầu bằng **Tạo hồ sơ** hoặc bấm nút **"Nạp mẫu tiếng Nhật / tiếng Việt"** để thử ngay; trả lời các câu hỏi làm rõ (tối đa 2 vòng), sau đó mở **Rà soát hướng giải pháp** → **WBS & lịch trình** (bảng WBS 3 cấp sửa được + Gantt).
- Với M5–M7, sau khi pipeline tạo WBS/schedule, mở **Báo giá**, **Proposal**, **Cổng duyệt** rồi **Xuất hồ sơ**. M7 cung cấp Word, Excel (WBS, công thức SUM, Gantt tuần, Q&A), PDF và ZIP; cảnh báo ja-check không chặn tải. Dữ liệu rate card trong `backend/app/reference/rate_card.yaml` là giả lập; Preview mặc định dùng mock LLM.

> Preview chạy qua `podman-compose -f podman-compose.preview.vibeflow.yaml up --build -d`. LLM mặc định `mock` (không gọi LLM thật) — pipeline M2–M7 chạy được ngay với dữ liệu giả lập. PDF cần LibreOffice headless và font Noto CJK trong image triển khai.

## Chạy toàn bộ test (một lệnh)

```bash
make test
```

Tương đương: `cd backend && pytest -q` + `cd frontend && npm run test` + `cd frontend && npm run build`.

Quality gate (CI-style, gồm grep guards BR-06/BR-10):

```bash
make quality-gate
```

## Cấu hình LLM

Mọi lời gọi LLM đi qua **một gateway duy nhất** (`backend/app/llm/`) — xem `docs/04_architecture/llm_pipeline.md` §10. Cấu hình bằng biến môi trường:

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `LLM_PROVIDER` | `mock` | `mock` (test/CI/demo, không gọi LLM thật) hoặc `openai_compat` |
| `LLM_BASE_URL` | _(trống)_ | Base URL endpoint tương thích OpenAI (khi `openai_compat`) |
| `LLM_API_KEY` | _(trống)_ | API key — **không commit, không in ra log** (BR-06) |
| `LLM_MODEL` | _(trống)_ | Tên model |
| `LLM_MAX_RETRIES` | `2` | Số lần retry tối đa khi output sai schema (BR-02) |
| `LLM_VERIFY_SSL` | `true` | Kiểm tra chứng chỉ TLS khi gọi provider; đặt `false` cho endpoint nội bộ self-signed |
| `LLM_CA_BUNDLE` | _(trống)_ | Đường dẫn CA bundle tùy chỉnh (thay vì tắt hẳn verify khi endpoint self-signed) |
| `DATABASE_URL` | `sqlite:///./data/bidding.db` | Chuỗi kết nối SQLite |

Template: `backend/.env.example` (sao chép sang `.env` / `.env.preview`; trong VibeFlow dùng Cài đặt dự án → biến môi trường). Backend tự đọc thêm file `.env` trong thư mục chạy (qua `python-dotenv`) — env vars thật (Preview/CI/container) vẫn ưu tiên hơn.

Thử gateway mock + che PII:

```bash
cd backend && python -m app.llm.demo
```

## Cấu trúc dự án

```
backend/    FastAPI + SQLAlchemy (SQLite) + LLM gateway (mock/openai_compat) + privacy/mask.py + pipeline (intake/gap/solution/wbs) + engines (effort/wbs/check/schedule)
frontend/   React 18 + Vite + TypeScript + Tailwind (menu trái: Tạo hồ sơ / Hồ sơ / Cài đặt; WBS 3 cấp + Gantt)
sample_data/ 2 hồ sơ mẫu giả lập (ja_email.md, vi_email.md) — dữ liệu hư cấu (BR-06)
docs/       SRS, kiến trúc, API contract (FROZEN), roadmap, slice spec
scripts/    quality_gate.sh
Makefile    test / run / quality-gate / preview
```

## Quy tắc bất biến (AGENTS.md)

1. LLM **không bao giờ** xuất man-day/giá/ngày — con số do code tính từ bảng chuẩn YAML.
2. Output LLM là JSON theo schema, retry ≤ 2.
3. Một LLM gateway duy nhất, có mock; test/CI không gọi LLM thật.
4. Hỏi thay vì đoán; ≤ 7 câu/vòng.
5. Giá chỉ hiển thị sau khi có người duyệt (cổng giá).
6. Che PII trước khi gửi LLM; không commit key; dữ liệu mẫu giả lập.
7. UI tiếng Việt; tài liệu gửi khách theo ngôn ngữ khách.
8. "Done" = test tự động pass **và** chạy được trong Preview.
9. Giữ đơn giản — không vector DB, queue, auth server.
10. Frontend gọi API **root-relative** `/api/...` — không hardcode localhost.
