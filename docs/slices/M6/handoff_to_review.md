# Handoff — QA Test → Test/Review (M6)

| Thuộc tính | Giá trị |
|---|---|
| Từ | QA / Test |
| Cho | Test / Review |
| Ngày | 2026-10-10 |
| Phạm vi | M6 attachment, parse, confirm gate, evaluation matrix |

## Deliverables

- Test cases IPA: `docs/slices/M6/test_cases.md`
- Test report: `docs/slices/M6/test_report.md`

## Kết quả

- Automated regression: PASS, backend `158 passed`, frontend `6 passed`.
- `make test`: PASS.
- `make quality-gate`: PASS.
- Preview health: PASS, database `ok`, `llm_provider=mock`.
- Sample bid API: PASS, tạo được hồ sơ `draft` với `budget_amount=null`.
- Acceptance commands theo bảy tên file trong spec: đều exit `5` vì file test không tồn tại/không thu thập được.
- UI click-through: 12 ca `BLOCKED` vì Chromium executable không tồn tại trong môi trường Playwright.
- FAIL chức năng: chưa kết luận được do chưa chạy qua browser; BLOCKED không được tính PASS.

## Việc cần làm tiếp

1. Cung cấp Chromium executable cho môi trường Playwright.
2. Rerun `TC-M6-001` đến `TC-M6-012` độc lập, chụp screenshot cho mọi ca fail.
3. Bổ sung hoặc xác nhận phạm vi của bảy file acceptance test còn thiếu trong `backend/tests/`.
4. Chỉ đóng acceptance M6 sau khi click-through và file-level acceptance đều có bằng chứng PASS.

**QA Test step complete. Awaiting Test/Review.**
