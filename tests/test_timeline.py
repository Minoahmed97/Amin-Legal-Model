from amin_legal_model.legal.timeline import assess_legal_timeline


def test_future_amendment_does_not_apply_before_its_effective_date():
    records = [
        {"document_id": "law", "legal_identifier": "LAW-1", "effective_from": "2020-01-01"},
        {
            "document_id": "amendment",
            "legal_identifier": "AMEND-1",
            "effective_from": "2027-01-01",
            "amends": ["LAW-1"],
            "amended_articles": ["5"],
        },
    ]
    result = assess_legal_timeline(records, "2026-11-20")
    assert result[0]["active_amendments"] == []
    assert result[1]["status"] == "not_yet_effective"


def test_active_amendment_is_linked_without_deactivating_original_law():
    records = [
        {"document_id": "law", "legal_identifier": "LAW-1", "effective_from": "2020-01-01"},
        {
            "document_id": "amendment",
            "legal_identifier": "AMEND-1",
            "effective_from": "2025-01-01",
            "amends": ["LAW-1"],
            "amended_articles": ["5", "7"],
            "title": "قانون معدل",
        },
    ]
    result = assess_legal_timeline(records, "2026-11-20")
    assert result[0]["status"] == "within_recorded_effective_window"
    assert result[0]["active_amendments"][0]["legal_identifier"] == "AMEND-1"


def test_full_repeal_only_takes_effect_from_recorded_date():
    records = [
        {"document_id": "law", "legal_identifier": "LAW-1", "effective_from": "2020-01-01"},
        {
            "document_id": "repeal",
            "legal_identifier": "REPEAL-1",
            "effective_from": "2026-01-01",
            "repeals": ["LAW-1"],
        },
    ]
    before = assess_legal_timeline(records, "2025-12-31")
    after = assess_legal_timeline(records, "2026-01-01")
    assert before[0]["status"] == "within_recorded_effective_window"
    assert after[0]["status"] == "repealed_by_recorded_instrument"


def test_unknown_effective_date_is_not_presented_as_current_law():
    result = assess_legal_timeline(
        [{"document_id": "unknown", "legal_identifier": "LAW-X"}],
        "2026-11-20",
    )
    assert result[0]["status"] == "unknown_effective_date"
