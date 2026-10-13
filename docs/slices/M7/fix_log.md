# Nhật ký sửa lỗi — M7 Fix Test Failures

## 1. F-M7-001 — Backend exporter import/runtime

### Nguyên nhân

Handoff QA ghi nhận một lần backend Preview khởi động lỗi tại `proposal_docx.py:2` với
`ModuleNotFoundError: No module named 'docx'`. Dependency `python-docx` và `openpyxl` đã có
trong `backend/requirements.txt`, nhưng image Preview cũ chưa được cài lại ổn định.
### Đã sửa

- Rebuild/restart Preview để cài lại `backend/requirements.txt`.
- Backend hiện khởi động thành công, log có `Application startup complete` và healthcheck trả 200.
- Sửa `backend/app/exporters/pdf.py` để tìm cả executable `libreoffice` và `soffice`; smoke test
  PDF trả bytes bắt đầu bằng `%PDF`.
- Loại bỏ câu lệnh symlink shell tạm thời trong compose sau khi phát hiện cú pháp không tương thích;
  không cần symlink vì converter đã xử lý cả hai tên executable.

## 2. Bổ sung acceptance coverage bị thiếu

Các file test M7 được spec yêu cầu trước đó chưa tồn tại. Đã bổ sung:

- `backend/tests/test_japanese_check.py`
- `backend/tests/test_export_word.py`
- `backend/tests/test_export_word_language.py`
- `backend/tests/test_export_excel_formulas.py`
- `backend/tests/test_export_deterministic.py`
- `backend/tests/test_export_price_gate.py`
- `backend/tests/test_export_bundle.py`

Các test kiểm tra rule ja-check, Word mở được và có bìa/mục lục/section, locale vi/en/ja,
Excel có đủ sheet và công thức `SUM`, Gantt/Q&A, filename an toàn, bundle đúng 3 entry,
deterministic bytes và price gate placeholder.

## 3. Kết quả kiểm tra cuối

| Kiểm tra | Kết quả |
|---|---|
| `pytest -q tests/test_japanese_check.py` | PASS, 3 tests |
| Bộ 7 lệnh test M7 bằng `pytest` trực tiếp | PASS, 11 tests |
| `pytest -q` toàn bộ backend | PASS, 178 tests |
| `npm run build` | PASS |
| `npm run test -- --run` | PASS, 6 tests |
| `npm run type-check` | PASS |
| `docx_to_pdf` với `soffice` | PASS, output `%PDF` |
| Preview backend health | PASS, `/api/health` 200 |
| Preview frontend shell | PASS, HTTP 200 |
| `podman-compose ... ps` | Backend/frontend Up; backend healthcheck vẫn hiển thị `starting` dù endpoint đã trả 200 |

## 4. Blocker môi trường không thể sửa trong code

- `make test` và `make quality-gate` chưa chạy được vì binary `make` không có trong runtime.
- Đã thử cài `make` một lần bằng apt nhưng upstream trả `403 Forbidden`; không retry-loop.
- Các lệnh chạy qua wrapper `rtk` báo sai `No tests collected`; đã chạy lại bằng `pytest` trực tiếp
  và nhận kết quả pass đáng tin cậy.
- Playwright click-through vẫn cần browser executable; đây là blocker môi trường QA, không phải
  lỗi backend đã sửa.
- Preview image `python:3.11-slim` không có LibreOffice/Noto CJK; Python converter đã hỗ trợ
  `soffice` ở runtime agent, nhưng image triển khai vẫn cần dependency PDF/CJK nếu muốn kiểm thử
  PDF tiếng Nhật end-to-end trong container.

## 5. Kết luận

Lỗi code/runtime đã được sửa và toàn bộ test hiện có cùng bộ acceptance test M7 đều pass khi chạy
bằng toolchain trực tiếp. Hai acceptance command dùng `make` không thể đạt exit 0 do thiếu binary
và apt bị chặn 403 trong runtime; đây là blocker hạ tầng được ghi nhận, không phải lỗi bị che hoặc
tiêu chí bị nới lỏng.

Task Fix Failures complete. Awaiting prompt for the next role.
