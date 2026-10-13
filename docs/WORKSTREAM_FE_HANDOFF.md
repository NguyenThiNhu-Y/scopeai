# Workstream FE — runtime verification handoff

## Scope

- Frontend tests and production build.
- Preview verification of bid sample creation, parse/confirm, pipeline progress and
  proposal/quotation API views.
- Browser automation was attempted but the configured Playwright browser executable was
  unavailable in this session, so no screenshot or DOM evidence was fabricated.

## Verification evidence

- `frontend`: `npm test -- --run` — **PASS**, 1 file / 16 tests.
- `frontend`: `npm run build` — **PASS**, TypeScript build and Vite production bundle.
- Supported Preview stack — **UP**; `GET /` returned 200 and proxied `GET /api/health`
  returned 200 JSON.
- Sample flow through the Preview origin succeeded:
  - `GET /api/bids/sample/preview?sample_key=ja_email` → 200, 3 files listed.
  - `POST /api/bids/sample` → 201, bid created.
  - `GET /api/bids/{id}` → 200, pipeline steps returned.
  - `POST /api/bids/{id}/parse` → 200, 36 requirements and parsed attachments.
  - `PUT /api/bids/{id}/parse/confirm` → 200.
  - `POST /api/bids/{id}/pipeline/start` → 202.
- Error and proposal/quotation mapping checks:
  - `GET /api/bids/{id}/quotation` before WBS → 409 JSON envelope with
    `STATE_CONFLICT` and Vietnamese message.
  - `GET /api/bids/{id}/proposal` → 200 JSON proposal draft with placeholder content.
  - `GET /api/bids/999999` → 404 JSON envelope with `NOT_FOUND`.

## Blocker

The Preview pipeline reaches `intake: failed` because the Preview environment is using
the `openai_compat` provider without an `LLM_API_KEY`. Backend logs show three bounded
retry attempts followed by `LLMSchemaError`; this is a runtime configuration blocker,
not a frontend/API mapping failure. No credential was read or printed.

## Notes for next role

- Existing frontend error rendering is wired to the backend error envelope and failed
  pipeline step (`PipelineProgress` displays `error_message` and exposes `Chạy lại`).
- Existing frontend API calls are root-relative under `/api`; no localhost URL was
  introduced.
