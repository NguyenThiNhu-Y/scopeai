# Test Report — M3 Hướng giải pháp + effort

| Thuộc tính | Giá trị |
|---|---|
| Slice | M3 |
| Tester | QA acceptance |
| Ngày | 2026-10-10 |
| Nguồn | `AGENTS.md`, `docs/slices/M3/spec.md`, `docs/slices/M3/handoff_to_test.md`, `docs/test-cases/M2-acceptance-testcases.md` |
| Môi trường | Preview production stack, proxy `http://localhost:5173`, `LLM_PROVIDER=mock` |
| Template | IPA mặc định theo template M2 trong repo; output Markdown |

## Acceptance commands

| Command | Exit/result | Ghi nhận |
|---|---:|---|
| `cd backend && pytest -q tests/test_effort.py` | 5 / no tests collected | Spec yêu cầu file không tồn tại; M3 test hiện nằm trong `tests/test_m3_backend.py`. |
| `cd backend && pytest -q tests/test_factors.py` | 5 / no tests collected | File không tồn tại. |
| `cd backend && pytest -q tests/test_solution_direction.py` | 5 / no tests collected | File không tồn tại. |
| `cd backend && pytest -q tests/test_trace.py` | 5 / no tests collected | File không tồn tại. |
| `cd backend && LLM_PROVIDER=mock pytest -q tests/test_llm_schema_no_numbers.py` | 5 / no tests collected | File có tồn tại nhưng không được pytest thu thập trong Preview/backend runtime hiện tại. |
| `make test` | 0 | Backend `67 passed`; frontend `4 passed`; frontend build pass. |
| `cd backend && pytest -q` | 0 | `67 passed`, 1 deprecation warning từ Starlette/httpx. |
| `cd frontend && npm run build` | 0 | TypeScript check và Vite production build pass. |
| `make quality-gate` | 0 | Backend pass; frontend type-check/build pass; BR-10 và BR-06 pass. |

## Test cases

| TC-ID | Function / Screen | Viewpoint | Preconditions | Procedure | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|---|---|---|
| TC-M3-001 | Màn hình Rà soát hướng giải pháp | Normal | Preview chạy, hồ sơ `73` có solution `rag` | Mở `/bids/73/solution`; đếm radio và đọc nhãn | Có đúng 5 hướng cố định: không cần AI, ML truyền thống, RAG, agent, fine-tune | Không thực thi được vì Chromium executable không tồn tại | Blocked | `docs/slices/M3/playwright-blocker.txt` |
| TC-M3-002 | EffortBreakdown | Normal | Hồ sơ 73 đã chọn RAG | Mở trang solution và quan sát effort | Có PoC/MVP/Production, dải min–max, midpoint/tổng do backend trả | Không thực thi được bằng UI; API tương đương pass | Blocked | `docs/slices/M3/playwright-blocker.txt` |
| TC-M3-003 | EffortTracePanel | Normal | Hồ sơ 73 có effort | Mở `Xem dấu vết tính toán` | Có version bảng, source YAML, raw/capped product, cap, formula và factor reason | Không thực thi được bằng UI; API response có đầy đủ các field | Blocked | `docs/slices/M3/playwright-blocker.txt` |
| TC-M3-004 | Persistence sau refresh | Semi-normal | Hồ sơ 73 đã lưu RAG | Refresh trang solution | RAG và reason vẫn khôi phục từ backend | Không thực thi được bằng UI; `GET /evaluations` xác nhận direction/reason persisted | Blocked | `docs/slices/M3/playwright-blocker.txt` |
| TC-M3-005 | Đổi hướng và tính lại effort | Normal | Hồ sơ 73 đang RAG | Đổi sang `none`, nhập reason, lưu | Response `effort_recalculated=true`; effort đổi theo YAML; không gọi LLM cho tính số | Không thực thi được bằng UI; automated backend tests pass phần deterministic calculation | Blocked | `docs/slices/M3/playwright-blocker.txt` |
| TC-M3-006 | `POST /api/bids/{id}/solution` | Abnormal / validation | Backend reachable, hồ sơ 73 | Gửi direction không thuộc enum | HTTP 400, `VALIDATION_ERROR`, message tiếng Việt, không persist | HTTP 400; envelope đúng; message `Dữ liệu gửi lên không hợp lệ`; chi tiết chỉ ra direction | PASS | API response captured in execution log |
| TC-M3-007 | `GET /api/bids/{id}/effort` | Normal / boundary | Hồ sơ 73 đã chọn RAG | Gọi effort và kiểm tra phase/factor/cap | 3 phase; factor product không vượt cap; trace raw/capped | HTTP 200; phase đủ `poc`, `mvp`, `production`; product 1.2 <= cap 2.0; trace 1.2/1.2 | PASS | API response captured in execution log |
| TC-M3-008 | `GET /api/bids/{id}/effort` | Abnormal | ID không tồn tại | Gọi `/api/bids/999999/effort` | HTTP 404, `NOT_FOUND` | Đúng HTTP 404 và `NOT_FOUND` | PASS | API response captured in execution log |
| TC-M3-009 | `GET /api/bids/{id}/evaluations` | Normal | Hồ sơ 73 đã lưu RAG | Gọi evaluations | Direction/reason persisted; stats tối thiểu có total/evaluated | HTTP 200; direction RAG; total/evaluated = 0; items rỗng | PASS | API response captured in execution log |

## Preview smoke

- `GET /api/health`: HTTP 200, `llm_provider=mock`, database `ok`.
- `POST /api/bids/sample` với sample tiếng Nhật: HTTP 201, tạo hồ sơ giả lập `id=73`.
- `POST /api/bids/73/solution` với `direction=rag`: HTTP 200, `effort_recalculated=true`.
- `GET /api/bids/73/effort`: HTTP 200, đủ 3 phase và trace.
- `GET /api/bids/73/evaluations`: HTTP 200, lựa chọn RAG được persist.

## Failures / blockers

### BLK-M3-001 — UI acceptance không khởi động được Playwright Chromium

- Reproduction: chạy Playwright với `chromium.launch(headless=True)` và mở `http://localhost:5173/bids/73/solution`.
- Actual: `BrowserType.launch: Executable doesn't exist at /home/user/.cache/ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell`.
- Impact: TC-M3-001 đến TC-M3-005 không thể thực thi UI hoặc chụp screenshot. Không có lỗi ứng dụng được kết luận từ blocker này.
- Evidence: `docs/slices/M3/playwright-blocker.txt`.
- Suspected file: không xác định là lỗi source; blocker thuộc môi trường browser runtime.

### GAP-M3-001 — Acceptance commands trỏ tới test files không tồn tại/không được collect

- Reproduction: chạy nguyên văn các command §5.1 của M3 spec.
- Actual: exit code 5, `No tests collected` cho năm command M3.
- Evidence: output acceptance command trong execution log.
- Suspected files: `docs/slices/M3/spec.md` và test layout hiện tại; implementation test M3 hiện thấy ở `backend/tests/test_m3_backend.py`.

## Summary

- Acceptance commands: 4/9 pass; 5/9 blocked/fail ở mức command collection; các quality gates tổng thể pass.
- API test cases: 4/4 pass.
- UI test cases: 0 pass, 5 blocked bởi thiếu Chromium executable.
- Tổng test cases: 4 pass, 0 fail, 5 blocked.
- Không sửa source ứng dụng trong bước QA.
