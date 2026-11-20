# Local inference runtime

The API can use a locally staged Hugging Face causal language model through the Transformers provider. It loads lazily on the first inference request.

## Install and configure

\`\`\`bash
pip install -e ".[inference]"
\`\`\`

Stage an exact, reviewed checkpoint and tokenizer on the inference host. Set \`AMIN_MODEL_ID\` to the local model directory. By default \`AMIN_MODEL_LOCAL_ONLY=true\`, so Transformers will not download weights. Set it to \`false\` only when a deliberate, approved model download is intended. \`trust_remote_code\` is disabled.

Relevant settings:
- \`AMIN_DEVICE_MAP=auto\` lets Accelerate place layers on available devices. Use \`none\` to load on CPU.
- \`AMIN_MAX_INPUT_TOKENS\` defaults to 8192; oversized requests are rejected rather than silently truncating legal facts or instructions.
- \`AMIN_MAX_NEW_TOKENS\` defaults to 2048.
- \`AMIN_TEMPERATURE\` defaults to 0.2; set 0 for deterministic greedy decoding.

This is an execution adapter, not a model-selection decision. Do not load a checkpoint until its exact weight, tokenizer, model-code and dependency licenses have been reviewed for the intended commercial use, and its Arabic Egyptian-law benchmark and memory requirements have been measured. A checkpoint name alone is not a license review.

The current API passes the Egyptian-law strategic system instruction to the provider. To ground an answer, set `AMIN_LEGAL_INDEX_PATH` to a built SQLite index and send `retrieval_query` (plus `as_of_date` when relevant) to `/v1/legal/respond`. Every result is rechecked against source permissions and returned in the `sources` field; missing indexes and empty retrieval are reported as warnings. The search baseline is lexical FTS5, not semantic retrieval. The health endpoint distinguishes a configured provider from weights actually loaded. A successful health response does not mean inference is ready.
