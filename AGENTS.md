# AGENTS.md — Presales Bidding Assistant: Project Rules

This repository builds a web app that helps presales engineers answer customer RFPs:
analyse the request, ask clarifying questions, estimate effort, build a WBS and schedule,
price it, and write the proposal. Work is done in steps by different roles; each role only
does its assigned part.

## Non-negotiable product rules (the "constitution")

1. **No invented numbers.** Effort, man-days, schedule dates and prices are NEVER produced by
   the LLM. The LLM classifies and explains; numbers are computed by code from editable
   reference tables (YAML) and covered by unit tests.
2. **Structured LLM output.** Every LLM call returns JSON validated against a schema; invalid
   output is retried a bounded number of times, then the step fails with a clear error.
3. **One LLM gateway.** All LLM calls go through a single client interface with a `mock`
   implementation. Unit tests and CI never call a real LLM. Config comes from env vars
   `LLM_PROVIDER` (mock|openai_compat), `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`.
4. **Ask instead of guess.** When information that changes the solution or the estimate is
   missing, the pipeline stops and asks the user clarifying questions, then continues.
5. **Price gate.** A price is never shown in customer-facing output before a human approves
   it. Until then the proposal shows a placeholder.
6. **Privacy.** Mask emails / phone numbers before sending customer text to the LLM. Never
   commit or print API keys. Sample data is fictional — no real company or customer names.
7. **Languages.** The app UI and internal analysis are Vietnamese. Customer-facing documents
   (questions, proposal) follow the customer's language (vi / en / ja).
8. **Done means proven.** A feature is done only when its automated tests pass AND it works
   in the running app (Preview). Never report "done" without running the checks.
9. **Keep it simple.** No heavy infrastructure (vector DB, queues, auth servers) unless a
   requirement truly needs it. Prefer the standard library and the agreed stack.
10. **Frontend networking.** The frontend calls the backend with a ROOT-RELATIVE API base
    (requests go to `/api/...`); never hardcode `http://localhost:...` (Preview forwards ports).

## Working protocol for every role

- Before starting: read this file, the latest handoff note, and the docs it points to.
- Documents go under `docs/` (Vietnamese). Code goes under `backend/` and `frontend/`.
- Use the todo tool to show progress; use the question tool when something is unclear —
  do not assume.
- At the end of a step: self-review, write the handoff note named in your instructions,
  print it, and STOP. The next step is triggered by the workflow, not by you.
- **Never fabricate evidence.** Screenshots must come from the real running app. If a browser
  is unavailable, state that limitation in the handoff and do not create placeholder images.
- The shell may add an `rtk` prefix to commands (an output-compacting wrapper). This is normal:
  trust its output and never retry a command just to avoid `rtk`. The acceptance gate is
  `make test` exiting 0. Never run the same command more than twice in a row.
- Shell commands may be wrapped by `rtk`, which can wrongly print "Pytest: No tests collected".
  Never retry the same command more than twice. To get real test results: read the log path printed
  in "[full output: ...]" or run the test suite as a background command.


## Document map

| Path | Content |
|---|---|
| `docs/01_idea.md` | Product idea and MVP scope (input) |
| `docs/02_research.md` | Market / domain research (optional input) |
| `docs/03_requirements/` | SRS, review notes |
| `docs/04_architecture/` | Architecture, data model, API contract, LLM pipeline schemas |
| `docs/05_roadmap/` | Milestones M1..Mn with acceptance criteria |
| `docs/slices/Mx/` | Per-milestone spec, test report, review |
| `docs/quality/` | Quality gate reports |
