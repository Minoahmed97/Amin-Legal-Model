"""Permission-gated SQLite full-text index for the staging legal corpus.

This is a lexical retrieval baseline (SQLite FTS5), not a vector/semantic
index. It preserves document provenance and rechecks retrieval permission.
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from amin_legal_model.source_policy import (
    SourcePermissionError,
    load_source_register,
    require_source_permission,
)

DEFAULT_CHUNK_CHARS = 1800
DEFAULT_OVERLAP_CHARS = 180


class LegalIndexError(RuntimeError):
    """Raised when the searchable legal index cannot be built or queried."""


def split_legal_text(text: str, *, max_chars: int = DEFAULT_CHUNK_CHARS,
                     overlap_chars: int = DEFAULT_OVERLAP_CHARS) -> list[str]:
    if max_chars < 200 or overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("Chunk sizes must satisfy max_chars >= 200 and 0 <= overlap < max.")
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    # Prefer article/paragraph boundaries before falling back to a hard split.
    units = re.split(r"(?=(?:المادة|مادة)\s*[（(]?\d+|(?:Article)\s+\d+)", normalized, flags=re.IGNORECASE)
    chunks: list[str] = []
    current = ""
    for unit in units:
        unit = unit.strip()
        if not unit:
            continue
        if len(unit) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            start = 0
            while start < len(unit):
                end = min(start + max_chars, len(unit))
                piece = unit[start:end].strip()
                if piece:
                    chunks.append(piece)
                if end == len(unit):
                    break
                start = end - overlap_chars
            continue
        candidate = f"{current} {unit}".strip() if current else unit
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = unit
    if current:
        chunks.append(current)
    return chunks


def _connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS legal_chunks_fts "
            "USING fts5(chunk_text, title, branch, source_reference, tokenize='unicode61')"
        )
        connection.execute(
            """CREATE TABLE IF NOT EXISTS legal_chunks (
                rowid INTEGER PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                branch TEXT NOT NULL,
                document_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                source_reference TEXT NOT NULL,
                source_url TEXT,
                publication_date TEXT,
                effective_from TEXT,
                effective_to TEXT,
                chunk_text TEXT NOT NULL,
                UNIQUE(document_id, chunk_number)
            )"""
        )
        connection.commit()
    except sqlite3.OperationalError as exc:
        connection.close()
        raise LegalIndexError(f"SQLite FTS5 is unavailable: {exc}") from exc
    return connection


def build_legal_index(
    corpus_path: str | Path,
    db_path: str | Path,
    *,
    register: dict[str, Any] | None = None,
) -> dict[str, int]:
    active_register = register if register is not None else load_source_register()
    source_map = {item["source_id"]: item for item in active_register.get("sources", [])}
    corpus = Path(corpus_path)
    if not corpus.is_file():
        raise LegalIndexError(f"Corpus file not found: {corpus}")
    connection = _connect(db_path)
    documents = 0
    chunks_added = 0
    try:
        with connection:
            for line_number, line in enumerate(corpus.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise LegalIndexError(f"Invalid JSONL record at line {line_number}.") from exc
                source_id = record.get("source_id")
                require_source_permission(source_id, "index_and_embed", register=active_register)
                source = source_map.get(source_id)
                if source is None:
                    raise SourcePermissionError(f"Source is missing from register: {source_id}")
                document_id = record.get("document_id")
                text = record.get("text")
                if not isinstance(document_id, str) or not isinstance(text, str) or not text.strip():
                    raise LegalIndexError(f"Missing document_id or text at line {line_number}.")
                pieces = split_legal_text(text)
                connection.execute(
                    "DELETE FROM legal_chunks_fts WHERE rowid IN "
                    "(SELECT rowid FROM legal_chunks WHERE document_id = ?)",
                    (document_id,),
                )
                connection.execute("DELETE FROM legal_chunks WHERE document_id = ?", (document_id,))
                for chunk_number, piece in enumerate(pieces):
                    cursor = connection.execute(
                        """INSERT INTO legal_chunks (
                            document_id, chunk_number, title, branch, document_type,
                            source_id, source_reference, source_url, publication_date,
                            effective_from, effective_to, chunk_text
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            document_id, chunk_number, record.get("title", ""),
                            record.get("branch", ""), record.get("document_type", ""),
                            source_id, record.get("source_reference", ""),
                            record.get("source_url"), record.get("publication_date"),
                            record.get("effective_from"), record.get("effective_to"), piece,
                        ),
                    )
                    rowid = cursor.lastrowid
                    connection.execute(
                        "INSERT INTO legal_chunks_fts(rowid, chunk_text, title, branch, source_reference) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (rowid, piece, record.get("title", ""), record.get("branch", ""),
                         record.get("source_reference", "")),
                    )
                    chunks_added += 1
                documents += 1
    finally:
        connection.close()
    return {"documents_indexed": documents, "chunks_indexed": chunks_added}


def search_legal_index(
    db_path: str | Path,
    query: str,
    *,
    limit: int = 5,
    register: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not query.strip():
        return []
    if not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20.")
    active_register = register if register is not None else load_source_register()
    # Quote each token so user input cannot inject FTS operators or syntax.
    terms = re.findall(r"[\w]+", query, flags=re.UNICODE)
    if not terms:
        return []
    match_query = " AND ".join('"' + term.replace('"', '""') + '"' for term in terms)
    connection = _connect(db_path)
    try:
        rows = connection.execute(
            """SELECT c.document_id, c.chunk_number, c.title, c.branch,
                      c.document_type, c.source_id, c.source_reference, c.source_url,
                      c.publication_date, c.effective_from, c.effective_to, c.chunk_text,
                      bm25(legal_chunks_fts) AS score
               FROM legal_chunks_fts f
               JOIN legal_chunks c ON c.rowid = f.rowid
               WHERE legal_chunks_fts MATCH ?
               ORDER BY score
               LIMIT ?""",
            (match_query, limit * 3),
        ).fetchall()
    except sqlite3.OperationalError as exc:
        raise LegalIndexError(f"Search query failed: {exc}") from exc
    finally:
        connection.close()

    results: list[dict[str, Any]] = []
    for row in rows:
        try:
            require_source_permission(row["source_id"], "ai_retrieval_and_analysis", register=active_register)
        except SourcePermissionError:
            continue
        results.append(dict(row))
        if len(results) >= limit:
            break
    return results
