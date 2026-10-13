# Handoff — Backend: OpenRouter RFP fixtures and parser fixes

Ngày: 2026-10-13  
Bước: Implement fixtures and backend fixes

## Deliverables

- Created fictional Tokai Minato fixtures under `sample_data/rfp_tokai_minato/fixtures/`:
  - `RFP_tokai_minato_poc.docx`
  - `request_tokai_minato.txt`
  - `requirements_tokai_minato.xlsx`
  - `fault_history_tokai_minato.csv`
  - `MC-850H_manual_excerpt.pdf`
- Preserved the mandatory source email at `sample_data/rfp_tokai_minato/email_yeu_cau_khach.txt`.
- Added parser regression coverage for all fixture formats and the mixed Japanese/English requirement and fault-history data.
- TXT coverage explicitly reads `request_tokai_minato.txt` and asserts the Japanese project name and proposal deadline.
- CSV detection coverage includes the Japanese attachment naming pattern `別紙2_故障履歴サンプル_2025-2026.csv` from the source email.

## Backend fixes

1. `backend/app/parsers/detect.py`
   - Kept the existing CSV requirement default for compatibility.
   - Detects clearly named fault-history CSV files as `sample_data`, allowing the existing profile/readiness path to run.
2. `backend/app/parsers/sample_profile.py`
   - PII column detection now recognizes Japanese contact labels `連絡先`, `メール`, and `電話`, in addition to existing Vietnamese/English labels.

## Verification

- `python3 -m pytest -q tests/test_file_reader.py tests/test_real_llm_contract.py tests/test_bids.py tests/test_pii_mask.py`
  - **PASS: 31 tests** after the completeness review.
- Fixture file-type inspection:
  - **PASS:** PDF, DOCX, CSV, TXT, and XLSX files created with the expected formats.
- `python3 scripts/smoke_real_llm.py`
  - **BLOCKED:** runtime reported `LLM_PROVIDER` is not `openai_compat`.
  - No API key value was read, printed, or added to any file.
- The compact `rtk pytest` wrapper reported `No tests collected`; the direct Python module runner is the authoritative result above.
- The same wrapper continued to report `No tests collected` during the review; `python3 -m pytest` exited successfully and is the authoritative result.

## Handoff to next role

- Continue with frontend/Preview verification and the full regression suite using the project's normal Python test runner.
- Re-run the real-LLM smoke only after project settings select `openai_compat` and the preview/runtime has been restarted as required by the environment configuration. Keep the key out of logs and reports.
- The backend role is complete; no frontend changes were made because no frontend bug was identified during this backend-focused step.

## Verification update — backend focused role

Date: 2026-10-13

- Authoritative full suite:
  - Command: `python3 -m pytest -q` (working directory `backend/`)
  - Result: **PASS — 263 tests** (`100%`), with one existing Starlette/httpx deprecation warning.
- Parser/upload, schema/retry/privacy, sample, profile, settings, proposal, and bid regression set:
  - Command: `python3 -m pytest -q tests/test_file_reader.py tests/test_real_llm_contract.py tests/test_evaluation_retry.py tests/test_solution_direction.py tests/test_llm_gateway.py tests/test_llm_schema_no_numbers.py tests/test_proposal_schema.py tests/test_pii_mask.py tests/test_sample_data.py tests/test_data_profile.py tests/test_settings_integrity.py tests/test_m3_sample_and_mock.py tests/test_bids.py`
  - Result: **PASS — 67 tests**, same non-blocking deprecation warning.
- Real provider smoke:
  - Command: `python3 scripts/smoke_real_llm.py` (working directory `backend/`)
  - Result: **BLOCKED before any provider request** because runtime configuration is not `openai_compat` (`[FAIL] provider: LLM_PROVIDER phải là openai_compat`). No credential value or raw PII was accessed or printed.
- The `rtk pytest` wrapper repeatedly returned `No tests collected`; direct `python3 -m pytest` is the authoritative runner and passes. No backend regression was found and no additional code fix was required in this verification step.
