# Model selection — AMIN's general Egyptian-law reasoning engine

**Review date:** 2026-11-20  
**Decision:** No production base model has been selected. AMIN must serve every branch of Egyptian law. The model supplies reasoning and language ability; current law and judicial materials must come from a versioned, cited legal knowledge system ([coverage policy](EGYPTIAN_LAW_COVERAGE.md)).

## Required capabilities

Modern Standard Arabic, Egyptian Arabic, formal legal Arabic and Arabic-English terminology; analysis of long statutes and case files; cross-reference, exception, amendment and transitional-rule reasoning; accurate structured output and tool use; source-grounded reasoning and abstention; practical inference/fine-tuning cost; mature deployment and commercially usable licensing.

## Candidate comparison (screening only, not benchmark results)

| Candidate | Relevant evidence | License screening | Initial position |
|---|---|---|---|
| **Qwen3** | Official project offers multiple sizes, long-context variants, tool-use integrations and fine-tuning recipes. Promising balance for Arabic, reasoning and deployment experiments. | Qwen3 repository states Apache 2.0 for its open-weight models. Verify exact checkpoint, tokenizer, code and dependencies. | **First baseline family to test**, not a winner yet. |
| **DeepSeek-R1 / distilled variants** | Reasoning-focused release; distilled Qwen variants enable smaller experiments. Must test citation discipline, verbosity and factual grounding. | DeepSeek states MIT for R1 code and weights; distilled variants may carry upstream obligations. Verify exact artifact. | Strong reasoning comparator. |
| **Llama 4 Scout / Maverick** | Meta lists Arabic among supported languages and very long context windows. Scout: 17B active / 109B total; Maverick: 17B active / 400B total. | Custom Llama 4 Community License, not Apache/MIT. Review commercial and redistribution conditions. | Important multilingual/long-context comparator; hardware and license review required. |
| **Mistral open models** | Mistral lists Arabic among supported languages. | Model-specific: some use Apache 2.0; others may use modified MIT or other terms. Never assume a family-wide license. | Include an Arabic-capable current checkpoint after exact license review. |
| **Jais** | Arabic-focused family worth testing for formal Arabic and Egyptian usage. | Exact checkpoint's current commercial license was not conclusively established in this screening. | Include only after verifying weights, tokenizer, code and terms. |
| **Aya Expanse 8B / 32B** | Model card lists Arabic among 23 languages; useful multilingual comparator. | Published model card specifies CC-BY-NC (non-commercial). | Research comparison only unless separate written commercial permission is obtained. |
| **Gemma 3** | Google describes multilingual support across 140+ languages and 128K context. | Google Gemma terms are model-specific, not Apache 2.0. Review exact terms and redistribution/fine-tuning conditions. | Optional comparator; license review required. |

“Open weights” does not mean unrestricted commercial use or permission to redistribute. Language-support lists do not prove Egyptian legal competence.

## Recommended selection path

1. Build a reproducible cross-branch Egyptian-law evaluation harness first.
2. Run a practical Qwen3 checkpoint as baseline; compare DeepSeek reasoning and a license-cleared Arabic-capable Mistral or Jais checkpoint.
3. Add Llama 4 Scout if hardware and license terms make the test meaningful.
4. Use Aya only for non-commercial research unless separate commercial permission applies.
5. Test all candidates with identical Egyptian legal tasks, retrieved sources, prompts, context limits, decoding settings and hardware.
6. Select by measured legal correctness, citation fidelity, temporal reasoning, abstention, Arabic quality, latency and total cost—not leaderboard rank.
7. Fine-tune only after lawful, reviewed, representative data exists. Compare retrieval/prompt improvements first; then test LoRA/QLoRA against the unchanged baseline.

## Egyptian-law benchmark

Balance cases across constitutional, civil, commercial, criminal, criminal procedure, civil procedure, administrative/State Council, labor/social insurance, tax/customs, real estate, Muslim personal status, non-Muslim personal status, and specialist laws.

Test: party and procedural-posture extraction; separation of allegations/admissions/evidence/findings; jurisdiction; applicable statutory version on the facts date; amendment and transitional rules; accurate retrieval/characterization of Cassation, Supreme Administrative Court and Supreme Constitutional Court decisions; binding versus persuasive authority; drafting without invented facts or sources; strongest counterargument; missing evidence; abstention when sources do not support an answer.

Score separately: legal correctness, citation precision, temporal correctness, issue coverage, hallucination rate, Arabic terminology, reasoning traceability, completeness, latency and cost. Egyptian-lawyer review is mandatory for gold answers.

## Hardware and cost

Do not publish fixed GPU requirements or costs before choosing the exact checkpoint, quantization, context, concurrency, serving engine and training method. Measure separately for inference, LoRA/QLoRA, embeddings/reranking, retrieval storage and document processing. Record peak VRAM, tokens/second, time-to-first-token, stable context, failure rate and cost per completed legal task.

## Sources checked 2026-11-20

- Qwen3 project/license: https://github.com/QwenLM/Qwen3
- Qwen3 release/context: https://qwen.ai/blog?id=qwen3
- DeepSeek-R1 release/license: https://deepseek.com/en/news/deepseek-r1/
- DeepSeek-R1 repository: https://github.com/deepseek-ai/DeepSeek-R1
- Meta Llama 4 cards: https://dev.meta.ai/llama/docs/model-cards-and-prompt-formats/llama4
- Mistral language support: https://docs.mistral.ai/resources/languages
- Mistral license overview: https://help.mistral.ai/en/articles/347393-under-which-license-are-mistral-s-open-models-available
- Aya Expanse card: https://huggingface.co/CohereLabs/aya-expanse-32b
- Gemma 3 card: https://gemma.ai/models/gemma-3/

This is a screening snapshot, not a substitute for rechecking licenses at deployment time.
