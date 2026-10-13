# Handoff — Main verification: OpenRouter fixtures, backend, and frontend

Date: 2026-10-13  
Step: Main parallel verification and reconciliation

## Scope completed

- Read the authoritative customer request at `sample_data/rfp_tokai_minato/email_yeu_cau_khach.txt`.
- Verified the fictional Tokai Minato fixtures for TXT, DOCX, XLSX, CSV, and PDF.
- Ran backend parser/upload, schema/retry, privacy, sample-data, settings, proposal, and bid checks.
- Ran frontend tests and production build.
- Exercised the supported Preview API flow for sample bid creation, attachment parsing, parse confirmation, pipeline start, proposal, quotation state conflict, and not-found errors.
- Reconciled backend and frontend findings without exposing credentials or raw PII.

## Backend evidence

- Command: `python3 -m pytest -q` from `backend/`
  - **PASS — 263 tests**, with one existing Starlette/httpx deprecation warning.
- Focused command covering file readers, real-LLM contract, retries, solution direction, gateway, no-invented-numbers schema, proposal, PII masking, sample data, profiling, settings, M3 sample behavior, and bids:
  - **PASS — 67 tests**.
- Fixture parsing and upload validation:
  - **PASS** for TXT, DOCX, PDF, XLSX, and CSV.
  - **PASS** for path-traversal rejection.
  - **PASS** for Japanese/English requirements and fault-history data.
- Backend code changes were already covered by regression tests:
  - CSV fault-history detection, including the Japanese `故障履歴` filename pattern.
  - Japanese contact/PII column detection, including `連絡先`.
  - Explicit TXT fixture content assertions.
- The compact `rtk pytest` output reported `No tests collected`; this is not the authoritative result. Direct `python3 -m pytest -q` passed all 263 backend tests.

## Frontend and Preview evidence

- Frontend tests: **PASS — 1 file / 16 tests**.
- Frontend production build: **PASS — TypeScript and Vite bundle**.
- Supported Preview stack:
  - `GET /`: **200**.
  - `GET /api/health`: **200**.
- Sample bid flow:
  - Sample preview: **200**, three files listed.
  - Create sample bid: **201**.
  - Bid detail: **200**.
  - Parse attachments: **200**, 36 requirements returned.
  - Confirm parse: **200**.
  - Start pipeline: **202**.
- Error and state mapping:
  - Quotation before WBS: **409**, `STATE_CONFLICT` envelope.
  - Proposal: **200**, draft with price placeholder.
  - Missing bid: **404**, `NOT_FOUND` envelope.
- Frontend API calls remain root-relative under `/api`; no localhost URL was introduced.
- Pipeline failure rendering is connected to `error_message` and exposes `Chạy lại`.
- Browser automation could not run because the Playwright browser executable was unavailable. No screenshot or DOM evidence was fabricated.

## Real OpenRouter status

Real-provider verification is **BLOCKED, not passed**.

- Backend smoke command: `python3 scripts/smoke_real_llm.py` from `backend/`.
  - It stopped before any provider request because that process did not receive `LLM_PROVIDER=openai_compat`.
- Preview runtime:
  - It did use `openai_compat`.
  - Pipeline reached `intake: failed` after three bounded retries because `LLM_API_KEY` was unavailable to the Preview runtime.
- These observations are consistent: configuration was not available in the two execution contexts at the time of verification. No API key was read, printed, or written.
- Consequently, the required real-LLM smoke request remains outstanding. Local structured-output, retry, privacy, and no-invented-numbers contracts are verified independently.

## Reconciliation result

- No conflicting implementation changes were reported by the two branches.
- No new backend or frontend bug was identified after the full regression and Preview API checks.
- The misleading `rtk pytest` result is superseded by the direct Python test result.
- The only unresolved item is runtime/provider configuration for an actual OpenRouter request, plus browser evidence once a supported browser executable is available.

## Actionable final regression list

1. Configure the project/Preview runtime to use `openai_compat` and make the API key available through the supported secret configuration without printing it.
2. Restart Preview if required by the configuration mechanism.
3. Run `python3 scripts/smoke_real_llm.py` and record only status, provider/model metadata that is non-secret, latency, and schema-validation outcome.
4. Re-run the sample Preview pipeline through intake and confirm the pipeline reaches the expected next stage.
5. Re-run the browser flow and capture real screenshots/DOM evidence if the browser executable is available.

## Handoff status

Backend and frontend local verification are complete. Provider validation is explicitly pending configuration. The next role should perform only the provider/runtime re-test and final Preview/browser evidence collection; it should not treat the current local PASS results as proof of a successful OpenRouter call.
