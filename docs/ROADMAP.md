# Roadmap

AMIN is a general-purpose Egyptian-law engine, not limited to one branch, court, or legal task. The full scope is defined in [EGYPTIAN_LAW_COVERAGE.md](EGYPTIAN_LAW_COVERAGE.md).

## Phase 1 — Foundation
- [x] Create repository documentation and safe project skeleton.
- [x] Define provider boundary, initial legal prompt, retrieval contract, API skeleton.
- [x] Validate API health behavior and the no-fake-answer path with automated tests.
- [x] Run automated tests in GitHub Actions; continue to require a green run for each change.

## Phase 2 — Model selection
- [x] Establish cross-branch model criteria and initial open-weight screening comparison.
- [ ] Verify exact checkpoint, tokenizer, code and dependency licenses for personal deployment.
- [ ] Build Egyptian-law cross-branch benchmark and lawyer-reviewed gold answers.
- [ ] Measure Arabic/legal quality, citation fidelity, temporal reasoning, latency, VRAM and cost.
- [x] Select Gemma 4 31B IT QAT as the first runnable private-server baseline candidate; keep Jais-2-70B as Arabic-specialist challenger.
- [ ] Accept final model only after Egyptian-law benchmark results.

## Phase 3 — Comprehensive Egyptian legal corpus
- [x] Define all-branches coverage map, source hierarchy and temporal versioning.
- [ ] Inventory legislation, regulations, decisions and official publications across every branch.
- [ ] Inventory Cassation, Supreme Administrative Court, Supreme Constitutional Court, Economic Courts and other available judgments.
- [x] Define a default-deny source license register and operation-specific permission guard.
- [ ] Verify access terms, copyright/database rights and lawful reuse before collection.
- [x] Implement a permission-gated offline document importer with provenance, hashing and duplicate detection.
- [x] Implement optional, permission-gated Arabic/English Tesseract OCR with page-level source mapping and confidence review.
- [x] Implement article-aware text chunking and permission-gated SQLite full-text indexing/search.
- [x] Implement metadata-based effective-date, full-repeal and partial-amendment reference resolution.
- [ ] Implement semantic embeddings, hybrid retrieval and reranking.
- [ ] Track coverage gaps by branch, authority, year and document type.
- [ ] Monitor new laws, amendments, repeal and newly published judgments.

## Phase 4 — Retrieval and legal reasoning
- [x] Specify adversarial strategic-lawyer reasoning: opponent modeling, omission/gap analysis, response selection, timing and procedural-risk checks.
- [x] Implement a transparent rule-based strategy triage endpoint with deadline/silence safeguards.
- [ ] Evaluate strategy decisions against lawyer-reviewed Egyptian case scenarios before relying on them in practice.
- [x] Implement lexical passage retrieval, provenance in API responses and metadata-based date-aware filtering.
- [ ] Implement semantic embeddings, hybrid retrieval and reranking.
- [ ] Support law in force today and law applicable on the facts date.
- [ ] Separate binding authority, persuasive judgments, official commentary and secondary materials.
- [ ] Add abstention and conflict handling for incomplete or inconsistent sources.

## Phase 5 — Model adaptation
- [ ] Compare retrieval/prompt improvements before fine-tuning.
- [ ] Prepare lawful, de-identified, reviewed datasets.
- [ ] Run LoRA/QLoRA experiments against the unchanged baseline.
- [ ] Validate regressions across every legal branch before accepting changes.

- [x] Inspect the existing Ameen app API boundary and document a provider-based, streaming-safe integration contract without modifying app workflows.
## Phase 6 — Inference service and integration
- [x] Implement optional local Transformers inference adapter with lazy loading and local-only default.
- [x] Add private vLLM-compatible provider and single-user Docker deployment recipe.
- [ ] Provision the private GPU host, stage exact weights and pass live health/inference tests (server path is not the selected zero-budget phone path).
- [ ] Integrate permission-gated legal retrieval into generated answers with verified citations.
- [x] Add an API-key gate for versioned API routes, failing closed when production has no key.
- [ ] Add per-user authentication, tenant isolation, distributed rate limits, observability and privacy controls.
- [ ] Run security, reliability and load tests.
- [x] Add a private API connector with independent client and model-server keys; keep API loopback-bound in the personal deployment.
- [ ] Connect the existing Ameen app through a server-side authenticated proxy after the private service is live (only if a server deployment is later selected).

No live private-server deployment, complete Egyptian legal corpus, or completed Egyptian-law benchmark is claimed by this roadmap.

## Phase 7 — Single-user Android local runtime (new target)
- [x] Record the actual target device: Infinix HOT 60 5G, Dimensity 7060, 6 GB physical RAM.
- [x] Add a separate Android-local runtime plan and isolated candidate profile; preserve the existing server profile.
- [ ] Verify available device storage and Android/Termux compatibility before building.
- [ ] Build or install a compatible ARM64 llama.cpp runtime on the phone.
- [ ] Download and verify the Qwen3-1.7B Q4_K_M GGUF candidate.
- [ ] Pass real on-device inference, stability, speed, thermal and battery tests.
- [ ] Benchmark Egyptian legal Arabic and source fidelity; reject the candidate if quality is insufficient.
- [ ] Design and test a private local Android bridge to the existing Ameen UI without exposing a public endpoint.
- [ ] Integrate only after model and local bridge acceptance; preserve existing Gemini/Groq behavior.

The Android profile is a smoke-test candidate, not a claim of a trained or production-ready Egyptian legal model.
