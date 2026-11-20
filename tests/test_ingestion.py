import json
from pathlib import Path

import pytest

from amin_legal_model.ingestion import IngestionError, ingest_document
from amin_legal_model.source_policy import SourcePermissionError


def _approved_register(ocr: bool = False):
    permissions = {"store": True}
    if ocr:
        permissions["ocr_and_normalize"] = True
    return {
        "sources": [{
            "source_id": "licensed_official_source",
            "name": "Licensed official source",
            "source_url": "https://example.test",
            "license_status": "approved",
            "permissions": permissions,
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
    assert row["ocr_status"] == "not_required"


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


def test_scanned_image_requires_specific_ocr_permission(tmp_path: Path, monkeypatch):
    import amin_legal_model.ingestion as ingestion

    image = tmp_path / "scan.png"
    image.write_bytes(b"test image bytes")
    monkeypatch.setattr(
        ingestion, "_ocr_image",
        lambda _path: {"text": "نص قانوني مستخرج من صورة للاختبار والتحقق", "confidence": 78.5},
    )
    with pytest.raises(SourcePermissionError):
        ingest_document(
            image, source_id="licensed_official_source", metadata=_metadata(),
            output_dir=tmp_path / "corpus", register=_approved_register(ocr=False),
        )
    assert not (tmp_path / "corpus").exists()


def test_scanned_image_ocr_records_confidence_and_page_mapping(tmp_path: Path, monkeypatch):
    import amin_legal_model.ingestion as ingestion

    image = tmp_path / "scan.png"
    image.write_bytes(b"test image bytes")
    monkeypatch.setattr(
        ingestion, "_ocr_image",
        lambda _path: {"text": "نص قانوني مستخرج من صورة للاختبار والتحقق", "confidence": 78.5},
    )
    result = ingest_document(
        image, source_id="licensed_official_source", metadata=_metadata(),
        output_dir=tmp_path / "corpus", register=_approved_register(ocr=True),
    )
    row = json.loads((tmp_path / "corpus" / "legal_documents.jsonl").read_text(encoding="utf-8"))
    assert result["status"] == "ingested"
    assert row["ocr_status"] == "completed_needs_human_review"
    assert row["ocr_average_confidence"] == 78.5
    assert row["page_text_map"][0]["page"] == 1
    assert row["text_review_status"] == "needs_human_verification"


def test_validate_amendment_metadata_lists(tmp_path: Path):
    source = tmp_path / "law.txt"
    source.write_text("نص قانوني تجريبي طويل بما يكفي لاختبار الاستيراد الآمن.", encoding="utf-8")
    bad = {**_metadata(), "repeals": "not-a-list"}
    with pytest.raises(IngestionError, match="repeals must be a list"):
        ingest_document(
            source, source_id="licensed_official_source", metadata=bad,
            output_dir=tmp_path / "corpus", register=_approved_register(),
        )
