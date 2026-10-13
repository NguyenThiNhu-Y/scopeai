# Fix Log — M1 Foundation

| Thuộc tính | Giá trị |
|---|---|
| Vai trò | Developer (Fix Test Failures) |
| Ngày | 2026-10-09 |
| Nguồn | `docs/slices/M1/spec.md` §5, `docs/slices/M1/test_report.md` |

## Kết luận

**Không có lỗi cần sửa.**

## Chi tiết

- `docs/slices/M1/test_report.md` ghi nhận: **14 PASS / 0 FAIL / 0 BLOCKED**.
- Toàn bộ 7 lệnh acceptance (spec §5a) exit 0:
  - `make test` → 0 (pytest 18 passed + vitest 2 passed + build OK)
  - `cd backend && pytest -q` → 0 (18 passed)
  - `LLM_PROVIDER=mock pytest -q tests/test_llm_gateway.py` → 0
  - `pytest -q tests/test_pii_mask.py` → 0
  - `cd frontend && npm run build` → 0
  - `curl -f …/api/health` → 0 (HTTP 200, contract đúng)
  - `make quality-gate` → 0 (`==> Quality gate PASSED`)
- Kịch bản tay trên Preview (TC-M1-01..06) và các rule AGENTS.md (TC-M1-07..14) đều PASS.

## Ghi chú

- Lượt chạy đầu của TC-M1-03 dùng selector `text=` khớp nhầm chuỗi con ("Tạo hồ sơ") — **lỗi script test, không phải lỗi sản phẩm**; chạy lại với `getByRole('link', {name:'Hồ sơ', exact:true})` → PASS. Không cần sửa code app, không làm yếu test.
- Các rủi ro đã biết (Google Fonts CDN bị chặn trong sandbox → fallback font; `OpenAICompatClient` chưa test với LLM thật theo ADR-004) nằm ngoài phạm vi M1, không phải FAIL.

---

**Task Fix Failures complete. Awaiting prompt for the next role.**