# OCR and scanned-document ingestion

The offline importer accepts image files and scanned or mixed PDFs when the source register explicitly approves both \`store\` and \`ocr_and_normalize\`. OCR never bypasses the independent index/retrieval permissions.

## Install

\`\`\`bash
pip install -e ".[documents,ocr]"
\`\`\`

The host must also install the Tesseract OCR executable and Arabic and English traineddata packages. Set \`TESSERACT_CMD\` only when the executable is not discoverable on PATH. The default language is \`ara+eng\`; override with \`AMIN_OCR_LANGUAGES\` when justified by the document.

## Review and quality

Scanned PDF pages with no usable text layer and image files are processed page by page. The corpus record preserves page number, extraction method, Tesseract confidence, average confidence and a list of pages below 45%. OCR text is always marked \`needs_human_verification\`; confidence is a machine signal, not proof of accuracy. Low-confidence pages, tables, marginal notes, stamps, handwriting, dates, amounts and article numbers require visual comparison against the source image.

Mixed PDFs keep native text on pages with a usable text layer and OCR only pages without one. The importer does not silently claim that a whole scanned file is accurate.

## Run

\`\`\`bash
amin-legal ingest --input ./decision-scan.pdf --source-id <approved-source-id> --metadata '{"title":"...","document_type":"judgment","branch":"civil","source_reference":"...","publication_date":"YYYY-MM-DD","effective_from":"YYYY-MM-DD"}'
\`\`\`

No official source is approved by default. Obtain and record written permissions before changing any source permission to true. OCR output does not establish ownership or permission to store, index, display, commercialize, or train on a source.
