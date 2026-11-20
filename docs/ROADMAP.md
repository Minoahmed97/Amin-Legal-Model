# Roadmap

AMIN is a general-purpose Egyptian-law engine, not limited to one branch, court, or legal task. The full scope is defined in [EGYPTIAN_LAW_COVERAGE.md](EGYPTIAN_LAW_COVERAGE.md).

## Phase 1 — Foundation
- [x] Create repository documentation and safe project skeleton.
- [x] Define provider boundary, initial legal prompt, retrieval contract, API skeleton.
- [ ] Validate configuration and API health endpoint in a reproducible environment.
- [ ] Run automated tests and verify CI results.

## Phase 2 — Model selection
- [x] Establish cross-branch model criteria and initial open-weight screening comparison.
- [ ] Verify exact checkpoint, tokenizer, code and dependency licenses for commercial use.
- [ ] Build Egyptian-law cross-branch benchmark and lawyer-reviewed gold answers.
- [ ] Measure Arabic/legal quality, citation fidelity, temporal reasoning, latency, VRAM and cost.
- [ ] Select baseline only after benchmark results.

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
- [ ] Implement hybrid retrieval, reranking, passage-level citations and date-aware retrieval.
- [ ] Support law in force today and law applicable on the facts date.
- [ ] Separate binding authority, persuasive judgments, official commentary and secondary materials.
- [ ] Add abstention and conflict handling for incomplete or inconsistent sources.

## Phase 5 — Model adaptation
- [ ] Compare retrieval/prompt improvements before fine-tuning.
- [ ] Prepare lawful, de-identified, reviewed datasets.
- [ ] Run LoRA/QLoRA experiments against the unchanged baseline.
- [ ] Validate regressions across every legal branch before accepting changes.

## Phase 6 — Inference service and integration
- [x] Implement optional local Transformers inference adapter with lazy loading and local-only default.
- [ ] Select, license-review, stage and benchmark an exact checkpoint before production use.
- [ ] Integrate permission-gated legal retrieval into generated answers with verified citations.
- [ ] Add authentication, rate limits, observability, privacy and deployment controls.
- [ ] Run security, reliability and load tests.
- [ ] Expose a stable API for future use by the existing Ameen app and other clients, without coupling this repository to that app during engine development.

No model training, complete legal corpus, successful test run, or production deployment is claimed by this roadmap.
