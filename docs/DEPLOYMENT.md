# Deployment notes

The repository now contains an optional local inference adapter, an API-key guard, OCR ingestion and a permission-gated legal retrieval baseline. It is **not yet a production-ready legal AI service**.

## Runtime configuration

- Install the base package with \`pip install -e ".[dev]"\`; add \`[documents]\`, \`[ocr]\`, and/or \`[inference]\` only where needed.
- Stage a reviewed model checkpoint and tokenizer on a dedicated inference host. Configure \`AMIN_MODEL_ID\`; the runtime defaults to \`AMIN_MODEL_LOCAL_ONLY=true\` and \`trust_remote_code=False\`.
- Set \`AMIN_LEGAL_INDEX_PATH\` to the SQLite index built from lawfully acquired and reviewed documents.
- Set \`AMIN_ENV=production\` and a strong \`AMIN_API_KEY\`. The \`/v1\` routes fail closed in production when no key exists and require the \`X-Amin-Api-Key\` header when configured.
- For OCR, install Tesseract plus Arabic and English traineddata on the host; configure \`TESSERACT_CMD\` only when necessary.
- Never commit private keys, credentials, model tokens, case files or personal data.

## Required production controls still to complete

- Add distributed rate limiting, request quotas and abuse controls at the API gateway.
- Add authentication integration, tenant isolation, authorization scopes and audited access to client data.
- Add structured observability with sensitive-data redaction, retention/deletion policy, encrypted storage, backups and incident handling.
- Test model memory, throughput, latency, cancellation, concurrency and long-document behavior on the actual selected checkpoint.
- Add load, security, dependency and supply-chain scans; pin deployment artifacts and verify model/tokenizer checksums.
- Define backup/restore and legal-data correction/revocation procedures.

Do not assume a serverless web deployment can host long-running model inference or GPU workloads. A green health check proves only that the API process responds, not that weights load, legal sources are complete, or the service is safe for public use.
