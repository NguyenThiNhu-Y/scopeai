# Fix Log — M3

| Thuộc tính | Giá trị |
|---|---|
| Vai trò | Senior Backend Developer |
| Ngày | 2026-10-10 |
| Slice | M3 |
| Phạm vi | Sửa các lỗi acceptance test được ghi trong `test_report.md`; không sửa tiêu chí acceptance |

## Lỗi và nguyên nhân

### FIX-M3-001 — Năm acceptance command trả `No tests collected`

- Nguyên nhân: `docs/slices/M3/spec.md` yêu cầu các module `test_effort.py`, `test_factors.py`, `test_solution_direction.py` và `test_trace.py`, nhưng implementation trước đó chỉ đặt một phần assertion vào `backend/tests/test_m3_backend.py`. Vì vậy các command exact của spec không có file test tương ứng.
- Cách sửa: thêm bốn module test đúng tên trong `backend/tests/`, bao phủ effort theo phase/direction, factor combinations và cap, solution enum/retry/no-number, cùng trace provenance. Không thay đổi acceptance criterion.
- Kết quả: các command M3 trước đây exit code 5 nay đều exit code 0.

### FIX-M3-002 — Expected raw factor product trong test mới sai

- Nguyên nhân: test mới ghi expected `1.44`, nhưng `backend/app/reference/factors.yaml` quy định `customer_jp=1.2` và `data_not_ready=1.3`; tích đúng là `1.56`.
- Cách sửa: sửa expected của test về `1.56`, bám theo YAML reference hiện hành; không sửa production code hoặc YAML.
- Kết quả: factor test và toàn bộ suite pass.

### BLK-M3-003 — Playwright UI không khởi động được Chromium

- Nguyên nhân: test report ghi nhận môi trường không có browser executable. Đây là blocker runtime, không phải lỗi backend và không được khắc phục bằng cách sửa mã ứng dụng trong vai trò này.
- Xử lý: giữ nguyên trạng thái Blocked của 5 UI cases và evidence tại `docs/slices/M3/playwright-blocker.txt`. API acceptance và automated backend/frontend gates vẫn được chạy độc lập.

## Verification cuối

| Command | Kết quả |
|---|---:|
| `cd backend && pytest -q tests/test_effort.py` | PASS, 3 tests |
| `cd backend && pytest -q tests/test_factors.py` | PASS, 3 tests |
| `cd backend && pytest -q tests/test_solution_direction.py` | PASS, 4 tests |
| `cd backend && pytest -q tests/test_trace.py` | PASS, 1 test |
| `cd backend && LLM_PROVIDER=mock pytest -q tests/test_llm_schema_no_numbers.py` | PASS, 6 tests |
| `cd backend && pytest -q` | PASS, 72 tests |
| `make test` | PASS, backend 72 tests + frontend 4 tests + build |
| `make quality-gate` | PASS |

Các warning còn lại là deprecation warning của Starlette/httpx và npm config warning; không làm command fail.

## Handoff

- Các lỗi command collection và test expected đã được sửa.
- Không có FAIL automated nào còn lại.
- UI cases vẫn cần chạy lại khi Preview session có Chromium executable; xem `handoff_to_review.md` và `test_report.md`.
