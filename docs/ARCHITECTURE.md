# AMIN Legal AI Engine — Architecture

## Product boundary

This repository builds the reusable legal AI engine, not the end-user web or Android application. Other applications will call the engine through a secured API.

## Request flow

1. A client sends a task and case text to the API.
2. The service validates the request and identifies the legal task.
3. A legal retriever searches approved, provenance-tracked Egyptian legal sources.
4. The selected model receives the task, user text, and retrieved source excerpts.
5. The response is returned with source metadata and uncertainty warnings.

## Replaceable components

- Model provider: adapter interface; no vendor is selected yet.
- Legal retriever: interface defined; no legal database is connected yet.
- API: FastAPI service.
- Evaluation: reviewed Egyptian-law test cases, kept separate from production data.

## Important current limitation

The repository currently contains interfaces and a foundation API only. It does not yet load model weights, search a real legal corpus, or generate legal answers. Those capabilities must be implemented and tested before the engine is described as operational.
