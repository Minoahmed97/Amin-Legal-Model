"""Controlled ingestion of lawfully acquired Egyptian legal documents.

The importer is deliberately offline: it never visits source websites. Every
document must identify a registered source and pass the operation-specific
permission guard before any text is written to the corpus.
"""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from amin_legal_model.source_policy import (
    SourcePermissionError,
    load_source_register,
    require_source_permission,
)

SUPPORTED_SUFFIXES = {".txt", ".md", ".html", ".htm", ".pdf", ".docx"}
MAX_INPUT_BYTES = 50 * 1024 * 1024


class IngestionError(ValueError):
    """Raised when a legal document cannot be safely ingested."""


class _TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._hidden_depth += 1
        elif tag in {"p", "div", "br", "li", "tr", "h1", "h2", "h3"}:
            self.parts.append("\\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._hidden_depth:
            self._hidden_depth -= 1
        elif tag in {"p", "div", "li", "tr", "h1", "h2", "h3"}:
            self.parts.append("\\n")

    def handle_data(self, data: str) -> None:
        if not self._hidden_depth:
            self.parts.append(data)


def _extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8-sig")
    if suffix in {".html", ".htm"}:
        parser = _TextHTMLParser()
        parser.feed(path.read_text(encoding="utf-8-sig"))
        parser.close()
        return "".join(parser.parts)
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise IngestionError("PDF support requires the optional 'pypdf' dependency.") from exc
        reader = PdfReader(str(path))
        return "\\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise IngestionError("DOCX support requires the optional 'python-docx' dependency.") from exc
        document = Document(str(path))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                paragraphs.append(" | ".join(cell.text for cell in row.cells))
        return "\\n".join(paragraphs)
    raise IngestionError(f"Unsupported file type: {suffix}")


def _validate_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise IngestionError("Metadata must be a JSON object.")
    required = ("title", "document_type", "branch", "source_reference")
    missing = [key for key in required if not isinstance(metadata.get(key), str) or not metadata[key].strip()]
    if missing:
        raise IngestionError(f"Missing required metadata: {', '.join(missing)}")
    for key in ("publication_date", "effective_from", "effective_to"):
        value = metadata.get(key)
        if value is not None:
            try:
                date.fromisoformat(value)
            except (TypeError, ValueError) as exc:
                raise IngestionError(f"{key} must use YYYY-MM-DD format.") from exc
    return metadata


def ingest_document(
    input_path: str | Path,
    *,
    source_id: str,
    metadata: dict[str, Any],
    output_dir: str | Path,
    register: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extract and append one authorized document to a JSONL corpus."""
    path = Path(input_path)
    if not path.is_file():
        raise IngestionError(f"Input file not found: {path}")
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise IngestionError(f"Unsupported file type: {path.suffix.lower()}")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise IngestionError("Input exceeds the 50 MiB safety limit.")

    # Check the exact operation before extraction or writing.
    active_register = register if register is not None else load_source_register()
    require_source_permission(source_id, "store", register=active_register)
    clean_metadata = _validate_metadata(metadata)

    text = _extract_text(path)
    text = re.sub(r"\\r\\n?", "\\n", text)
    text = "\\n".join(line.rstrip() for line in text.splitlines()).strip()
    if len(text) < 20:
        raise IngestionError(
            "No usable text was extracted. Scanned/image-only PDFs require OCR and human verification."
        )

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    source = next(item for item in active_register["sources"] if item["source_id"] == source_id)
    record = {
        "document_id": digest,
        "content_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "title": clean_metadata["title"].strip(),
        "document_type": clean_metadata["document_type"].strip(),
        "branch": clean_metadata["branch"].strip(),
        "jurisdiction": "EG",
        "source_id": source_id,
        "source_name": source.get("name", source_id),
        "source_reference": clean_metadata["source_reference"].strip(),
        "source_url": source.get("source_url"),
        "publication_date": clean_metadata.get("publication_date"),
        "effective_from": clean_metadata.get("effective_from"),
        "effective_to": clean_metadata.get("effective_to"),
        "instrument_number": clean_metadata.get("instrument_number"),
        "year": clean_metadata.get("year"),
        "gazette_issue": clean_metadata.get("gazette_issue"),
        "amends": clean_metadata.get("amends", []),
        "repeals": clean_metadata.get("repeals", []),
        "text": text,
        "text_review_status": "needs_human_verification",
        "ocr_status": "not_applicable" if path.suffix.lower() != ".pdf" else "pdf_text_layer_unverified",
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    corpus_file = destination / "legal_documents.jsonl"
    if corpus_file.exists():
        for line in corpus_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                existing = json.loads(line)
            except json.JSONDecodeError as exc:
                raise IngestionError("Existing corpus JSONL is malformed; refusing to append.") from exc
            if existing.get("document_id") == digest:
                return {"status": "duplicate", "document_id": digest, "output": str(corpus_file)}

    serialized = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\\n"
    # Atomic append replacement prevents a partial JSONL write on interruption.
    previous = corpus_file.read_text(encoding="utf-8") if corpus_file.exists() else ""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destination, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(previous)
        handle.write(serialized)
        handle.flush()
    temp_path.replace(corpus_file)
    return {"status": "ingested", "document_id": digest, "output": str(corpus_file)}
