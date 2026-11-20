import json
from pathlib import Path

import pytest

from amin_legal_model.ingestion import IngestionError, ingest_document
from amin_legal_model.source_policy import SourcePermissionError


def _approved_register():
    return {
        "sources": [{
            "source_id": "licensed_official_source",
            "name": "Licensed official source",
            "source_url": "https://example.test",
            "license_status": "approved",
            "permissions": {"store": True},
        }]
    }


def _metadata():
    return {
        "title": "قانون افتراضي للاختبار",
        "document_type": "law",
        "branch": "civil",
        "source_reference": "ملف اختبار مقدم بصورة مشروعة",
        "publication_date": "2020-01-01",
        "effective_from": "2020-02-01",
    }


def test_ingest_text_with_provenance_and_review_flag(tmp_path: Path) -> None:
    source = tmp_path / "law.txt"
    source.write_text("نص قانوني تجريبي طويل بما يكفي لاختبار الاستيراد الآمن.", encoding="utf-8")
    result = ingest_document(
        source,
        source_id="licensed_official_source",
        metadata=_metadata(),
        output_dir=tmp_path / "corpus",
        register=_approved_register(),
    )
    assert result["status"] == "ingested"
    row = json.loads((tmp_path / "corpus" / "legal_documents.jsonl").read_text(encoding="utf-8"))
    assert row["branch"] == "civil"
    assert row["jurisdiction"] == "EG"
    assert row["text_review_status"] == "needs_human_verification"


def test_reject_unlicensed_source_before_writing(tmp_path: Path) -> None:
    source = tmp_path / "law.txt"
    source.write_text("نص قانوني تجريبي طويل بما يكفي لاختبار الاستيراد الآمن.", encoding="utf-8")
    with pytest.raises(SourcePermissionError):
        ingest_document(
            source,
            source_id="licensed_official_source",
            metadata=_metadata(),
            output_dir=tmp_path / "corpus",
            register={"sources": [{
                "source_id": "licensed_official_source",
                "license_status": "unknown",
                "permissions": {"store": True},
            }]},
        )
    assert not (tmp_path / "corpus").exists()


def test_duplicate_document_is_not_appended_twice(tmp_path: Path) -> None:
    source = tmp_path / "law.txt"
    source.write_text("نص قانوني تجريبي طويل بما يكفي لاختبار الاستيراد الآمن.", encoding="utf-8")
    kwargs = {
        "source_id": "licensed_official_source",
        "metadata": _metadata(),
        "output_dir": tmp_path / "corpus",
        "register": _approved_register(),
    }
    first = ingest_document(source, **kwargs)
    second = ingest_document(source, **kwargs)
    assert first["status"] == "ingested"
    assert second["status"] == "duplicate"


def test_reject_missing_required_metadata(tmp_path: Path) -> None:
    source = tmp_path / "law.txt"
    source.write_text("نص قانوني تجريبي طويل بما يكفي لاختبار الاستيراد الآمن.", encoding="utf-8")
    with pytest.raises(IngestionError, match="Missing required metadata"):
        ingest_document(
            source,
            source_id="licensed_official_source",
            metadata={"title": "عنوان فقط"},
            output_dir=tmp_path / "corpus",
            register=_approved_register(),
        )
