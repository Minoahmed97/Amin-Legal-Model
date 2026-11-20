"""Controlled ingestion of lawfully acquired Egyptian legal documents.

The importer is deliberately offline: it never visits source websites. Every
document must identify a registered source and pass operation-specific guards.
OCR is optional, permission-gated, and every extracted page remains unverified
until a human reviews it.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from amin_legal_model.source_policy import (
    load_source_register,
    require_source_permission,
)

SUPPORTED_SUFFIXES = {
    ".txt", ".md", ".html", ".htm", ".pdf", ".docx",
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp",
}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
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
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._hidden_depth:
            self._hidden_depth -= 1
        elif tag in {"p", "div", "li", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._hidden_depth:
            self.parts.append(data)


def _normalize_text(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def _ocr_image(image: Any) -> dict[str, Any]:
    """OCR one Pillow image with Tesseract; requires installed ara+eng traineddata."""
    try:
        from PIL import Image
        import pytesseract
        from pytesseract import Output
    except ImportError as exc:
        raise IngestionError(
            "Image OCR requires the optional 'ocr' dependencies. Install with: pip install -e '.[ocr]'."
        ) from exc
    command = os.getenv("TESSERACT_CMD")
    if command:
        pytesseract.pytesseract.tesseract_cmd = command
    try:
        if isinstance(image, (str, Path)):
            with Image.open(image) as opened:
                source = opened.convert("RGB")
        else:
            source = image.convert("RGB")
        data = pytesseract.image_to_data(
            source,
            lang=os.getenv("AMIN_OCR_LANGUAGES", "ara+eng"),
            config="--psm 6",
            output_type=Output.DICT,
        )
    except Exception as exc:
        raise IngestionError(
            "Tesseract OCR failed. Verify that the Tesseract executable and Arabic/English "
            "traineddata (ara, eng) are installed and configured."
        ) from exc
    words: list[str] = []
    confidences: list[float] = []
    for word, confidence in zip(data.get("text", []), data.get("conf", [])):
        value = str(word).strip()
        try:
            score = float(confidence)
        except (TypeError, ValueError):
            score = -1
        if value:
            words.append(value)
            if score >= 0:
                confidences.append(score)
    return {
        "text": " ".join(words).strip(),
        "confidence": round(sum(confidences) / len(confidences), 2) if confidences else None,
    }


def _extract_pdf(path: Path, *, source_id: str, register: dict[str, Any]) -> tuple[str, list[dict[str, Any]], str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise IngestionError("PDF support requires the optional 'pypdf' dependency.") from exc
    try:
        reader = PdfReader(str(path))
        native_pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise IngestionError(f"Could not read PDF: {exc}") from exc

    missing = [index for index, text in enumerate(native_pages) if len(text.strip()) < 20]
    page_map: list[dict[str, Any]] = []
    if missing:
        require_source_permission(source_id, "ocr_and_normalize", register=register)
        try:
            import fitz
            from PIL import Image
        except ImportError as exc:
            raise IngestionError(
                "Scanned or mixed PDFs require the optional 'ocr' dependencies and Tesseract."
            ) from exc
        try:
            pdf = fitz.open(str(path))
            for index, native_text in enumerate(native_pages):
                if index in missing:
                    page = pdf.load_page(index)
                    pixmap = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
                    image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                    result = _ocr_image(image)
                    page_map.append({
                        "page": index + 1,
                        "text": _normalize_text(result["text"]),
                        "extraction_method": "tesseract_ocr",
                        "ocr_confidence": result["confidence"],
                    })
                else:
                    page_map.append({
                        "page": index + 1,
                        "text": _normalize_text(native_text),
                        "extraction_method": "pdf_text_layer",
                        "ocr_confidence": None,
                    })
            pdf.close()
        except IngestionError:
            raise
        except Exception as exc:
            raise IngestionError(f"PDF page OCR failed: {exc}") from exc
        status = "completed_needs_human_review"
    else:
        page_map = [
            {
                "page": index + 1,
                "text": _normalize_text(text),
                "extraction_method": "pdf_text_layer",
                "ocr_confidence": None,
            }
            for index, text in enumerate(native_pages)
        ]
        status = "not_required"

    combined = "\n\n".join(item["text"] for item in page_map)
    return combined, page_map, status


def _extract_document(
    path: Path, *, source_id: str, register: dict[str, Any]
) -> tuple[str, list[dict[str, Any]], str]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8-sig"), [], "not_required"
    if suffix in {".html", ".htm"}:
        parser = _TextHTMLParser()
        parser.feed(path.read_text(encoding="utf-8-sig"))
        parser.close()
        return "".join(parser.parts), [], "not_required"
    if suffix == ".pdf":
        return _extract_pdf(path, source_id=source_id, register=register)
    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise IngestionError("DOCX support requires the optional 'python-docx' dependency.") from exc
        document = Document(path)
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                paragraphs.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(paragraphs), [], "not_required"
    if suffix in IMAGE_SUFFIXES:
        require_source_permission(source_id, "ocr_and_normalize", register=register)
        result = _ocr_image(path)
        page_map = [{
            "page": 1,
            "text": _normalize_text(result["text"]),
            "extraction_method": "tesseract_ocr",
            "ocr_confidence": result["confidence"],
        }]
        return result["text"], page_map, "completed_needs_human_review"
    raise IngestionError(f"Unsupported file type: {suffix}")


def _validate_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise IngestionError("Metadata must be a JSON object.")
    required = ("title", "document_type", "branch", "source_reference")
    missing = [
        key for key in required
        if not isinstance(metadata.get(key), str) or not metadata[key].strip()
    ]
    if missing:
        raise IngestionError(f"Missing required metadata: {', '.join(missing)}")
    for key in ("publication_date", "effective_from", "effective_to"):
        value = metadata.get(key)
        if value is not None:
            try:
                date.fromisoformat(value)
            except (TypeError, ValueError) as exc:
                raise IngestionError(f"{key} must use YYYY-MM-DD format.") from exc
    for key in ("amends", "repeals", "amended_articles"):
        value = metadata.get(key, [])
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            raise IngestionError(f"{key} must be a list of non-empty strings.")
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

    active_register = register if register is not None else load_source_register()
    require_source_permission(source_id, "store", register=active_register)
    clean_metadata = _validate_metadata(metadata)

    extracted_text, page_map, ocr_status = _extract_document(
        path, source_id=source_id, register=active_register
    )
    text = _normalize_text(extracted_text)
    if len(text) < 20:
        raise IngestionError(
            "No usable text was extracted. Check scan quality, OCR language packs, and page orientation."
        )

    confidence_values = [
        item["ocr_confidence"] for item in page_map
        if isinstance(item.get("ocr_confidence"), (int, float))
    ]
    low_confidence_pages = [
        item["page"] for item in page_map
        if isinstance(item.get("ocr_confidence"), (int, float))
        and item["ocr_confidence"] < 45
    ]
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
        "legal_identifier": clean_metadata.get("legal_identifier"),
        "instrument_number": clean_metadata.get("instrument_number"),
        "year": clean_metadata.get("year"),
        "gazette_issue": clean_metadata.get("gazette_issue"),
        "amends": clean_metadata.get("amends", []),
        "repeals": clean_metadata.get("repeals", []),
        "amended_articles": clean_metadata.get("amended_articles", []),
        "text": text,
        "page_text_map": page_map,
        "text_review_status": "needs_human_verification",
        "ocr_status": ocr_status,
        "ocr_average_confidence": (
            round(sum(confidence_values) / len(confidence_values), 2)
            if confidence_values else None
        ),
        "ocr_low_confidence_pages": low_confidence_pages,
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

    serialized = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    previous = corpus_file.read_text(encoding="utf-8") if corpus_file.exists() else ""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destination, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(previous)
        handle.write(serialized)
        handle.flush()
    temp_path.replace(corpus_file)
    return {"status": "ingested", "document_id": digest, "output": str(corpus_file)}
