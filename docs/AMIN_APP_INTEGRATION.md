# AMIN Legal Model ↔ existing Ameen app integration contract

## Confirmed target application

The current application repository is `Minoahmed97/Amin-smart-lawyer-assistant`, default branch `main`. Its current central Vercel API router is `api/index.ts`, which dispatches existing legal routes including:

- `/api/gemini/deconstruct`
- `/api/gemini/counter-brief`
- `/api/gemini/qualify`
- `/api/gemini/chat`
- `/api/gemini/refine`
- `/api/gemini/jobs`

The main shared generation function is `generateDeepLegalResponse` in `backend/gemini/counter-brief.ts`. The deconstruction, qualification, drafting and chat handlers call this shared function for at least part of their model work. Some routes stream SSE chunks; the shared generator also implements continuation, deduplication, completion-marker validation and a 270-second deadline.

## Integration rule: add a provider, do not replace application workflows

The eventual integration should be a server-side provider branch behind the existing shared generation boundary. It must not replace the app, route names, request/response contracts, authentication, session checks, cooldowns, rate limits, credits, saved-job lifecycle, queue worker, notifications, uploads, OCR, document extraction, or UI.

Required behavior:

1. Keep the current Gemini/Groq route as the default until AMIN has passed live model and legal benchmark tests.
2. Add a server-only feature flag such as `AMIN_LEGAL_MODEL_ENABLED=false`. Never expose the AMIN API key or model-server key to Vite/browser code.
3. The app's Vercel server function calls the AMIN API over HTTPS/private networking. It forwards the app's already-constructed legal prompt, including its existing Egyptian legal system instruction and any task-specific context already assembled by the app. The engine may append its own anti-fabrication and source-provenance safeguards.
4. Preserve streaming semantics. The current app expects incremental text, continuation without duplicated prefixes, and a clear completion condition. Do not silently replace this with a single long non-streaming response.
5. Preserve the app's existing completion marker and continuation policy, or introduce a tested adapter that translates between the two protocols without exposing internal markers to the user.
6. Preserve authentication and billing at the app boundary. The model service must not independently charge credits or accept unauthenticated browser traffic.
7. Preserve all existing API paths and response shapes. No direct browser-to-model-server calls.
8. Add a controlled fallback to the existing provider only when explicitly enabled and only for retryable model-service failures. Record which provider produced the final answer without logging case text, prompts, secrets or client documents.
9. Keep OCR and PDF/DOCX extraction in the existing app pipeline unless a separately tested reason requires moving them. The legal model receives extracted text and structured task context.
10. Test draft, deconstruct, qualify, chat, long outputs, interruption/retry, saved jobs, queue worker, cross-account isolation, credits and failure paths before enabling the flag.

## API compatibility gap to close before wiring the app

The current AMIN engine exposes `POST /v1/legal/respond` as a non-streaming response and applies its own default legal system prompt. That is not yet a drop-in replacement for the app's shared streaming generator, which passes a richer app-specific legal prompt and uses a completion marker plus continuation logic.

Before connecting the app, the engine needs a versioned streaming endpoint and an explicit, bounded server-to-server prompt/context contract. The streaming endpoint must emit well-formed SSE chunks, a terminal success event only after a complete answer, and a terminal error event on failure. It must never mark a truncated answer as complete. The prompt/context field must be accepted only over the authenticated server-to-server API and must have strict size limits.

## Deployment and activation gates

Do not enable the integration until all of these are true:

- A private GPU host exists and the pinned model checkpoint loads successfully.
- `/health` reports `model_server_ready: true`.
- Real inference and streaming smoke tests pass on the live host.
- The Egyptian legal corpus has been lawfully acquired, reviewed, indexed and tested; the current source register is default-deny.
- Lawyer-reviewed benchmark results meet the acceptance criteria in `PERSONAL_MODEL_SELECTION.md`.
- The app-side adapter passes regression tests with the feature flag off and on.
- The private service is reachable only through authenticated TLS/private networking; no secret is placed in frontend code.

## Current status

This document is an integration contract based on inspection of the current app repository. It is not a claim that the app is already connected. No application files were changed as part of documenting this contract.
