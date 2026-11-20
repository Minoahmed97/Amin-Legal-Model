# Personal model selection — private Egyptian-law engine

## First runnable baseline candidate

Use **Google Gemma 4 31B IT QAT W4A16 compressed-tensors** as the first deployment candidate:

- Exact checkpoint: \`google/gemma-4-31B-it-qat-w4a16-ct\`
- Model card/license: Apache 2.0.
- Instruction-tuned checkpoint, not base weights.
- QAT compressed-tensors variant is explicitly provided for optimized vLLM inference.
- Supports Arabic as part of Gemma 4's multilingual training, long context, image input and reasoning mode.
- This is a first baseline candidate, not a claim that it is the best Egyptian-law model. It must pass the project's Arabic/Egyptian-law benchmark before acceptance.

Official references:
- Model card: https://huggingface.co/google/gemma-4-31B-it-qat-w4a16-ct
- QAT checkpoint details: https://huggingface.co/google/gemma-4-31B-it-qat-w4a16-ct/blob/main/README.md
- Gemma 4 overview and memory estimates: https://ai.google.dev/gemma/docs/core
- vLLM Gemma 4 serving recipe: https://docs.vllm.ai/projects/recipes/en/stable/Google/Gemma4.html

The official Gemma overview estimates about 17.5 GB for 4-bit Q4_0 weights for the 31B model; that is weights only, not a full server capacity guarantee. KV cache, context length, runtime overhead and concurrent requests require additional memory. vLLM's BF16 recipe lists 1×80 GB NVIDIA GPU for the unquantized 31B model. The QAT compressed-tensors checkpoint is the chosen initial route to reduce the weight-memory requirement.

## Arabic-specialist challenger

Benchmark **Jais-2-70B-Chat** as a serious challenger, not an assumed winner:
- Model card: https://huggingface.co/inception42/Jais-2-70B-Chat
- The developers describe it as Arabic-English, trained from scratch with an Arabic-centric vocabulary.
- Its repository lists Apache 2.0, but access to weights is gated by an acceptance step.
- The 70B model and its reported 8K context create different hardware and long-document trade-offs.
- It must be tested on Egyptian legal drafting, procedural reasoning, statute retrieval, dialect, OCR correction and citation fidelity against Gemma 4.

## Acceptance rule

Do not call a model "the AMIN model" merely because it loads. Compare the exact pinned checkpoints on a lawyer-reviewed, de-identified Egyptian benchmark covering all legal branches. Score separately:
1. Correct identification of applicable law and its date.
2. Exactness of statutory text, article number, amendment and repeal status.
3. Binding/persuasive status and provenance of judgments.
4. Correct client-side identification and burden/evidence analysis.
5. Adversarial analysis of the opponent's strongest argument.
6. Strategic choice: respond, stay silent, narrow reply, full brief, or procedural step.
7. No invented case facts, statutes, judgments, quotations or citations.
8. Egyptian Arabic terminology, drafting quality and consistency.
9. Long-document completeness, latency, memory and failure recovery.

A lawyer must review the answer and citations. A model score never overrides a verified official source. The final checkpoint remains replaceable through environment configuration after benchmark results.
