import json
from pathlib import Path

import pytest

from amin_legal_model.legal_index import (
    LegalIndexError,
    build_legal_index,
    search_legal_index,
    split_legal_text,
)
from amin_legal_model.source_policy import SourcePermissionError


def _register():
    return {"sources": [{
        "source_id": "licensed_source",
        "license_status": "approved",
        "permissions": {
            "index_and_embed": True,
            "ai_retrieval_and_analysis": True,
        },
    }]}


def _corpus(tmp_path: Path, *, extra: dict | None = None) -> Path:
    record = {
        "document_id": "doc-1",
        "source_id": "licensed_source",
        "title": "قانون مدني افتراضي",
        "branch": "civil",
        "document_type": "law",
        "source_reference": "الجريدة الرسمية، عدد تجريبي",
        "effective_from": "2020-02-01",
        "effective_to": None,
        "legal_identifier": "LAW-1",
        "amends": [],
        "repeals": [],
        "amended_articles": [],
        "text": "المادة 1 الالتزامات المدنية تنشأ عن العقد وبحسن نية.",
    }
    if extra:
        record.update(extra)
    path = tmp_path / "legal.jsonl"
    path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def test_split_text_keeps_content_and_respects_limit():
    text = "أ" * 2300
    chunks = split_legal_text(text, max_chars=500, overlap_chars=50)
    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_build_and_search_index_returns_source_citation(tmp_path: Path):
    corpus = _corpus(tmp_path)
    db = tmp_path / "index" / "legal.sqlite"
    result = build_legal_index(corpus, db, register=_register())
    assert result["documents_indexed"] == 1
    found = search_legal_index(db, "الالتزامات المدنية", register=_register())
    assert found
    assert found[0]["source_reference"] == "الجريدة الرسمية، عدد تجريبي"
    assert found[0]["effective_from"] == "2020-02-01"


def test_indexing_denied_without_permission(tmp_path: Path):
    with pytest.raises(SourcePermissionError):
        build_legal_index(
            _corpus(tmp_path),
            tmp_path / "index.sqlite",
            register={"sources": [{
                "source_id": "licensed_source",
                "license_status": "unknown",
                "permissions": {"index_and_embed": True},
            }]},
        )


def test_retrieval_rechecks_permission(tmp_path: Path):
    corpus = _corpus(tmp_path)
    db = tmp_path / "index.sqlite"
    build_legal_index(corpus, db, register=_register())
    denied = {"sources": [{
        "source_id": "licensed_source",
        "license_status": "approved",
        "permissions": {"index_and_embed": True, "ai_retrieval_and_analysis": False},
    }]}
    assert search_legal_index(db, "الالتزامات المدنية", register=denied) == []


def test_missing_corpus_is_reported(tmp_path: Path):
    with pytest.raises(LegalIndexError, match="Corpus file not found"):
        build_legal_index(tmp_path / "missing.jsonl", tmp_path / "index.sqlite", register=_register())


def test_date_aware_search_returns_active_amendments(tmp_path: Path):
    corpus = _corpus(tmp_path)
    amendment = {
        "document_id": "amend-1",
        "source_id": "licensed_source",
        "title": "قانون معدل",
        "branch": "civil",
        "document_type": "amendment",
        "source_reference": "عدد لاحق",
        "effective_from": "2025-01-01",
        "legal_identifier": "AMEND-1",
        "amends": ["LAW-1"],
        "amended_articles": ["1"],
        "repeals": [],
        "text": "المادة 1 تعديل الالتزامات المدنية وشروط العقد.",
    }
    with corpus.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(amendment, ensure_ascii=False) + "\n")
    db = tmp_path / "index.sqlite"
    build_legal_index(corpus, db, register=_register())
    found = search_legal_index(
        db, "الالتزامات المدنية", as_of_date="2026-11-20", register=_register()
    )
    base = next(item for item in found if item["document_id"] == "doc-1")
    assert base["temporal_status"] == "within_recorded_effective_window"
    assert base["active_amendments"][0]["legal_identifier"] == "AMEND-1"
    assert "ليست شهادة" in base["temporal_warning"]


def test_date_aware_search_excludes_recorded_repeal(tmp_path: Path):
    corpus = _corpus(tmp_path)
    repeal = {
        "document_id": "repeal-1",
        "source_id": "licensed_source",
        "title": "قانون إلغاء",
        "branch": "civil",
        "document_type": "law",
        "source_reference": "عدد لاحق",
        "effective_from": "2025-01-01",
        "legal_identifier": "REPEAL-1",
        "amends": [],
        "repeals": ["LAW-1"],
        "amended_articles": [],
        "text": "المادة 1 الالتزامات المدنية ألغيت صراحة بنص افتراضي.",
    }
    with corpus.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(repeal, ensure_ascii=False) + "\n")
    db = tmp_path / "index.sqlite"
    build_legal_index(corpus, db, register=_register())
    old = search_legal_index(db, "الالتزامات المدنية", as_of_date="2024-12-31", register=_register())
    new = search_legal_index(db, "الالتزامات المدنية", as_of_date="2026-11-20", register=_register())
    assert any(item["document_id"] == "doc-1" for item in old)
    assert not any(item["document_id"] == "doc-1" for item in new)


def test_old_index_schema_is_migrated(tmp_path: Path):
    import sqlite3
    db = tmp_path / "old.sqlite"
    connection = sqlite3.connect(db)
    connection.execute(
        """CREATE TABLE legal_chunks (
            rowid INTEGER PRIMARY KEY, document_id TEXT NOT NULL, chunk_number INTEGER NOT NULL,
            title TEXT NOT NULL, branch TEXT NOT NULL, document_type TEXT NOT NULL,
            source_id TEXT NOT NULL, source_reference TEXT NOT NULL, source_url TEXT,
            publication_date TEXT, effective_from TEXT, effective_to TEXT, chunk_text TEXT NOT NULL,
            UNIQUE(document_id, chunk_number)
        )"""
    )
    connection.commit()
    connection.close()
    from amin_legal_model.legal_index import _connect
    migrated = _connect(db)
    columns = {row["name"] for row in migrated.execute("PRAGMA table_info(legal_chunks)")}
    migrated.close()
    assert {"legal_identifier", "amends_json", "repeals_json"} <= columns
