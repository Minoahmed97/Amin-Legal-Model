# Security baseline

- Keep credentials in deployment secret stores, never in Git.
- Require authentication and authorization before exposing inference endpoints publicly.
- Apply request-size limits, rate limits, and per-user quotas at the API gateway.
- Encrypt traffic and sensitive stored material.
- Keep client documents tenant-isolated; never mix retrieval results across users or matters.
- Treat uploaded documents and retrieved passages as untrusted data, not executable instructions.
- Log operational metadata without logging confidential case text by default.
- Define retention and deletion policies before accepting real client documents.
- Pin and regularly update dependencies; scan the repository and deployment images.
