"""Resolve recorded legal-instrument dates and amendment/repeal relationships.

This is a metadata resolver, not a consolidation engine. Partial amendments do
not erase the original instrument text. Missing metadata remains explicitly
unknown, and no result is certified as the law currently in force.
"""
from __future__ import annotations

from datetime import date
from typing import Any


class LegalTimelineError(ValueError):
    """Raised for invalid dates or malformed legal timeline metadata."""


def _as_date(value: Any, field: str) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise LegalTimelineError(f"{field} must use YYYY-MM-DD.") from exc
    raise LegalTimelineError(f"{field} must be a date string or date object.")


def assess_legal_timeline(
    records: list[dict[str, Any]], as_of_date: date | str
) -> list[dict[str, Any]]:
    """Classify instruments and attach active amendment/repeal references."""
    target_date = _as_date(as_of_date, "as_of_date")
    if target_date is None:
        raise LegalTimelineError("as_of_date is required.")

    repeal_events: dict[str, list[dict[str, Any]]] = {}
    amendments: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise LegalTimelineError("Every timeline record must be an object.")
        start = _as_date(record.get("effective_from"), "effective_from")
        if start is not None and start > target_date:
            continue
        legal_id = record.get("legal_identifier")
        if not isinstance(legal_id, str) or not legal_id.strip():
            continue
        repeals = record.get("repeals", [])
        amends = record.get("amends", [])
        if not isinstance(repeals, list) or not isinstance(amends, list):
            raise LegalTimelineError("amends and repeals must be lists.")
        for target in repeals:
            if isinstance(target, str) and target.strip():
                repeal_events.setdefault(target, []).append(record)
        for target in amends:
            if isinstance(target, str) and target.strip():
                amendments.setdefault(target, []).append(record)

    resolved: list[dict[str, Any]] = []
    for record in records:
        start = _as_date(record.get("effective_from"), "effective_from")
        end = _as_date(record.get("effective_to"), "effective_to")
        legal_id = record.get("legal_identifier")
        repealed_by = repeal_events.get(legal_id, []) if legal_id else []
        active_amendments = amendments.get(legal_id, []) if legal_id else []

        if start is not None and start > target_date:
            state = "not_yet_effective"
        elif end is not None and end < target_date:
            state = "expired_or_ended"
        elif repealed_by:
            state = "repealed_by_recorded_instrument"
        elif start is None:
            state = "unknown_effective_date"
        else:
            state = "within_recorded_effective_window"

        resolved.append({
            "document_id": record.get("document_id"),
            "legal_identifier": legal_id,
            "status": state,
            "active_amendments": [
                {
                    "legal_identifier": item.get("legal_identifier"),
                    "title": item.get("title"),
                    "instrument_number": item.get("instrument_number"),
                    "effective_from": item.get("effective_from"),
                    "amended_articles": item.get("amended_articles", []),
                }
                for item in active_amendments
            ],
            "repealed_by": [
                {
                    "legal_identifier": item.get("legal_identifier"),
                    "title": item.get("title"),
                    "effective_from": item.get("effective_from"),
                }
                for item in repealed_by
            ],
        })
    return resolved
