# Handoff — Final Deliverables Review

Ngày: 2026-10-13  
Vai trò: Senior reviewer, code/document review  
Nguồn bắt buộc: `sample_data/rfp_tokai_minato/email_yeu_cau_khach.txt`

## Kết luận

Deliverables local đã đầy đủ và không phát hiện thiếu fixture hoặc regression
test trong phạm vi repository. Tài liệu cũ có số liệu lỗi thời, đã được cập nhật.
Không sửa application code trong bước review vì không phát hiện bug mới sau khi
chạy regression trực tiếp.

## Testcase Matrix

| ID | Kết quả | Bằng chứng |
|---|---|---|
| A-01 | PASS | Preview/API sample bid trả 201, customer language `ja` |
| A-02 | PASS | `backend/tests/test_file_reader.py`; đủ DOCX/TXT/XLSX/CSV/PDF |
| A-03 | PASS | Fixture parser test; PDF/DOCX/TXT/XLSX/CSV đọc được |
| A-04 | PASS | Requirement workbook test và backend suite |
| A-05 | PASS | CSV profile có row count/columns và PII `連絡先` |
| A-06 | PASS | Parse confirmation gate và pipeline start API evidence |
| A-07 | PASS | Path traversal, extension và file-size regression tests |
| B-01 | BLOCKED | Smoke dừng vì process không nhận `LLM_PROVIDER=openai_compat` |
| B-02 | PASS (contract) | `backend/tests/test_real_llm_contract.py` |
| B-03 | PASS (contract) | JSON mode/request-format contract tests |
| B-04 | PASS | Pydantic structured-output validation tests |
| B-05 | PASS | Bounded retry tests |
| B-06 | PASS | PII masking tests và không in secret |
| B-07 | PASS | No-invented-numbers schema tests |
| B-08 | BLOCKED | Chưa có request OpenRouter thật thành công |
| C-01..C-09 | PASS | Backend suite và Preview/API evidence; price gate được kiểm tra |
| D-01..D-05 | PASS (automated/API) | Frontend 16 tests, build và API contract evidence |
| D-06 | BLOCKED | Playwright browser executable không khả dụng |

## Commands And Results

- `cd backend && python3 -m pytest -q`: **PASS — 263 tests**.
- `cd frontend && npm run test -- --run`: **PASS — 16 tests**.
- `cd frontend && npm run build`: **PASS**.
- `bash scripts/quality_gate.sh`: **PASS**.
- `make test`: **NOT RUN — `make` không có trong runtime**; equivalent đã pass.
- `cd backend && python3 scripts/smoke_real_llm.py`: **BLOCKED trước provider
  request**; không đọc/in API key.

## Deliverables

- `sample_data/rfp_tokai_minato/fixtures/RFP_tokai_minato_poc.docx`
- `sample_data/rfp_tokai_minato/fixtures/request_tokai_minato.txt`
- `sample_data/rfp_tokai_minato/fixtures/requirements_tokai_minato.xlsx`
- `sample_data/rfp_tokai_minato/fixtures/fault_history_tokai_minato.csv`
- `sample_data/rfp_tokai_minato/fixtures/MC-850H_manual_excerpt.pdf`
- `docs/quality/deliverables_review_main_verification.md`
- `docs/quality/handoff_main_verification.md`

## Remaining External Blockers

1. Runtime provider configuration must expose `openai_compat` and the configured
   secret through supported project settings; the value must remain unread and
   absent from logs.
2. A supported browser executable is required for D-06 and screenshot/DOM proof.
3. Overall verdict remains **NO-GO** until B-08 and D-06 are proven or formally
   accepted as external blockers.

## HANDOFF NOTE

Local fixture, backend, frontend, parser, schema/retry, privacy, no-number and
price-gate deliverables are complete and verified. Updated stale QA documents and
saved this final review. Real OpenRouter and browser evidence remain explicitly
blocked by runtime configuration/browser availability. Step complete.
