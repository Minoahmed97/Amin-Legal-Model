# Controlled Legal Document Ingestion

This stage adds an offline importer for files that AMIN is lawfully authorized to process. It does not scrape websites, bypass subscriptions, or download judgments.

## Supported inputs

- TXT and Markdown: UTF-8 / UTF-8 with BOM.
- HTML: extracts visible text and ignores script/style/noscript content.
- PDF: extracts an existing text layer when the optional `pypdf` package is installed.
- DOCX: extracts paragraphs and tables when the optional `python-docx` package is installed.

Scanned/image-only PDFs are rejected when no usable text layer exists. OCR is a separate stage and must retain an unverified status until human review.

## Permission gate

Before extraction or writing, the importer calls the source permission guard for `store`. The source must be marked `approved` and the exact `store: true` permission must be present. The importer never treats a personal subscription or browser visibility as authorization.

## Required metadata

Every import requires:
- `title`
- `document_type` (for example: law, regulation, ministerial_decision, judgment)
- `branch` (one of the coverage taxonomy labels)
- `source_reference` (official publication / source record reference)

Optional dates must use ISO `YYYY-MM-DD`. Additional fields include instrument number, year, Gazette issue, amendment and repeal references.

## Output

The importer appends one record per document to `legal_documents.jsonl`. Each record stores source identity, provenance, dates, SHA-256 hashes, extracted text, and explicit review/OCR status. Duplicate file hashes are skipped. Writes use a temporary file and atomic replacement.

This JSONL file is an ingestion staging corpus, not yet a searchable production database. Human verification, amendment-chain resolution, chunking, indexing, and retrieval remain later stages.
