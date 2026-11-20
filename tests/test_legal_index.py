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
        "name": "Licensed source",
        "license_status": "approved",
        "permissions": {"index_and_embed": True, "ai_retrieval_and_analysis": True},
    }]}


def _corpus(tmp_path: Path):
    path = tmp_path / "legal_documents.jsonl"
    record = {
        "document_id": "doc-1",
        "title": "قانون مدني تجريبي",
        "document_type": "law",
        "branch": "civil",
        "source_id": "licensed_source",
        "source_reference": "الجريدة الرسمية، عدد تجريبي",
        "source_url": "https://example.test/law",
        "publication_date": "2020-01-01",
        "effective_from": "2020-02-01",
        "effective_to": None,
        "text": "المادة 1 ينظم هذا القانون الالتزامات المدنية والعقود والتعويض عن الضرر. "
                "المادة 2 يلتزم المدين بتنفيذ التزامه طبقاً لما اشتمل عليه العقد وبحسن نية.",
    }
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
