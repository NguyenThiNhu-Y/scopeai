# Fix Log — M2 Phân tích yêu cầu + hỏi làm rõ

| Thuộc tính | Giá trị |
|---|---|
| Vai trò | Developer (Fix Test Failures) |
| Ngày | 2026-10-09 (bổ sung 2026-10-10) |
| Nguồn | `docs/slices/M2/test_report.md`, `docs/slices/M2/review.md`, `docs/slices/M2/spec.md`, `AGENTS.md` |

## Đợt 1 — Kết quả acceptance test M2: 29/29 PASS, không có FAIL để sửa

Chi tiết đợt 1: xem bản ghi trước — 3 observations (TC-M2-011 `details.allowed`, TC-M2-014/026 race 409, bind mount Preview) đều **không phải lỗi** (đã đối chiếu contract frozen §3.7; guard đã phủ bởi unit test; infra đã sửa).

---

## Đợt 2 — Fix test treo (SSE) + các finding từ review (H-1, M-1, M-2, M-3)

### 1. Test treo khi chạy full suite (SSE)

**Root cause:** `SSEManager.subscribe` (sse.py) stream **vô hạn** — sau sự kiện cuối (`done`/`clarify`/`error`) vẫn gửi heartbeat mãi. Test/HTTP client chờ response đầy đủ sẽ treo tới khi timeout.

**Fix:**
- `backend/app/pipeline/sse.py` — luồng **tự đóng** sau sự kiện cuối: `done`, `clarify` (pipeline dừng ở waiting_clarification), `error` (bước lỗi). Reconnect tới hồ sơ đã ở trạng thái cuối → đóng ngay sau replay (phát hiện qua trạng thái bước: có `failed` / `gap=waiting_clarification` / `intake+gap=completed`).
- Test SSE đã viết ở mức **asyncio** (không dùng HTTP test client chờ response) — giữ nguyên; bổ sung 3 test auto-close (`test_sse_stream_auto_closes_after_{done,clarify,error}`) + tăng cường `test_sse_reconnect_replays_current_state` (assert luồng kết thúc, không heartbeat).
- **Verify live (Preview):** `curl -N` tới `/pipeline/events` của bid chạy xong → nhận 7 sự kiện rồi stream **tự đóng trong 0s** (trước đây treo tới timeout).

### 2. pytest-timeout (chống treo âm thầm)

- `backend/pyproject.toml`: `[tool.pytest.ini_options] timeout = 60` (mỗi test tối đa 60s → treo thì báo FAIL thay vì đứng).
- `backend/requirements.txt`: thêm `pytest-timeout`.

### 3. H-1 (HIGH — review.md): `submit_answers` làm hỏng trạng thái bid

**Root cause:** `clarify_service.submit_answers` không kiểm tra `bid.status == "waiting_clarification"`; với `{"answers":[]}` trên bid draft → `missing=∅` → commit `bid.status="analyzing"` → `resume` sau đó mới fail (422) → bid kẹt `analyzing` vĩnh viễn (đã tái hiện live: bid 67).

**Fix:** `backend/app/services/clarify_service.py` — guard đầu hàm:
- `bid.status != "waiting_clarification"` → `400 VALIDATION_ERROR` ("Hồ sơ không ở trạng thái chờ làm rõ"), **không đổi trạng thái**.
- Không có câu hỏi chờ ở vòng → `400` ("Không có câu hỏi chờ trả lời ở vòng này").
- Commit `analyzing` chỉ sau khi toàn bộ validate qua.
- Test: `test_submit_answers_on_draft_bid_rejected`, `test_submit_answers_empty_on_waiting_bid_returns_missing_ids`, `test_submit_answers_wrong_round_rejected`.

### 4. M-1 (MEDIUM): lỗi ngoài `LLMSchemaError` làm kẹt bước `running`

**Root cause:** `orchestrator.run` bắt `Exception` chung nhưng các bước chỉ `mark_failed` với `LLMSchemaError`; lỗi provider/mạng/DB → bước ở `running`, bid ở `analyzing`, rerun không tìm thấy bước `failed`.

**Fix:** `backend/app/pipeline/orchestrator.py` — `run()` gọi `_mark_running_step_failed(bid_id, exc)`: tìm bước `running`, đánh `failed` + `error_message` + phát SSE `error`. Test: `test_provider_error_marks_step_failed_and_rerunnable`.

### 5. M-2 (MEDIUM): `_finalize` dùng `assert`

**Fix:** thay bằng `if bid is None: raise RuntimeError(...)`.

### 6. M-3 (MEDIUM): answers lưu trước khi `resume` kiểm tra 409

**Fix:** `backend/app/api/routers/questions.py` — kiểm tra `is_running(bid_id)` trước `submit_answers` → `409 STATE_CONFLICT` trước khi lưu answers. Export `is_running` từ `app/pipeline/__init__.py`.

---

## Lệnh acceptance — kết quả cuối (re-run sau fix)

| Lệnh | Exit | Kết quả |
|---|---|---|
| `timeout 300 python -m pytest -q -x --durations=10` | **0** | **71 tests pass, không treo** (thêm 7 test mới) |
| `make test` | **0** | backend 71 + frontend 4 + build OK |
| `make quality-gate` | **0** | **Quality gate PASSED** |
| Preview (podman-compose, backend recreate) | Up | `health: ok`, `llm: mock` |
| H-1 live: answers rỗng trên bid draft | 400 | status giữ `draft` (không hỏng) |
| SSE live: curl `/pipeline/events` | tự đóng | 7 events, stream đóng trong 0s |
| Full flow live: sample → analyze → clarify (2 vòng) → done | OK | `waiting_tech_approval`, rounds=2 |
| UI smoke (Playwright) | OK | Home/New/Sample/Analyze → Chờ làm rõ + câu hỏi tiếng Nhật |

## Kết luận cuối

Toàn bộ fix đã áp dụng, test xanh (71 backend + 4 frontend), Preview ghép backend–frontend hoạt động đúng spec M2 §5b. Không còn finding CRITICAL/HIGH chưa xử lý (H-1 đã fix; M-1/M-2/M-3 đã fix; M-4/L-1..L-4 là cải tiến nhỏ để milestone sau).

**Task Fix Failures complete. Awaiting prompt for the next role.**