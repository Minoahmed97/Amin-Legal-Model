"""Fail-closed source permission checks for future corpus ingestion.

This module does not fetch or scrape source websites. It only decides whether
a planned operation is explicitly approved in the local source register.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ALLOWED_STATUSES = {"approved", "written_permission_required", "research_only", "blocked", "unknown"}
OPERATIONS = {
    "manual_access",
    "automated_access",
    "bulk_export",
    "store",
    "ocr_and_normalize",
    "index_and_embed",
    "ai_retrieval_and_analysis",
    "commercial_display",
    "redistribute",
    "train_or_finetune",
}


class SourcePermissionError(PermissionError):
    """Raised when a source is not approved for a requested operation."""


class SourceRegisterError(ValueError):
    """Raised when the source register is malformed or ambiguous."""


def load_source_register(path: str | Path | None = None) -> dict[str, Any]:
    register_path = Path(path) if path else Path(__file__).parents[3] / "configs" / "source_licenses.yaml"
    if not register_path.is_file():
        raise SourceRegisterError(f"Source license register not found: {register_path}")
    try:
        data = yaml.safe_load(register_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SourceRegisterError(f"Invalid source license YAML: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        raise SourceRegisterError("Source register must contain a sources list.")
    seen: set[str] = set()
    for source in data["sources"]:
        if not isinstance(source, dict) or not isinstance(source.get("source_id"), str):
            raise SourceRegisterError("Every source must define a source_id.")
        source_id = source["source_id"]
        if source_id in seen:
            raise SourceRegisterError(f"Duplicate source_id: {source_id}")
        seen.add(source_id)
        status = source.get("license_status", "unknown")
        if status not in ALLOWED_STATUSES:
            raise SourceRegisterError(f"Invalid license status for {source_id}: {status}")
        permissions = source.get("permissions", {})
        if not isinstance(permissions, dict):
            raise SourceRegisterError(f"Permissions must be a mapping for {source_id}.")
        for operation, permitted in permissions.items():
            if operation not in OPERATIONS:
                raise SourceRegisterError(f"Unknown operation for {source_id}: {operation}")
            if not isinstance(permitted, bool):
                raise SourceRegisterError(f"Permission {operation} for {source_id} must be boolean.")
    return data


def require_source_permission(
    source_id: str,
    operation: str,
    *,
    register: dict[str, Any] | None = None,
) -> None:
    """Allow only an explicitly true permission on a source marked approved."""
    if operation not in OPERATIONS:
        raise SourcePermissionError(f"Unsupported source operation: {operation}")
    data = register if register is not None else load_source_register()
    matches = [item for item in data.get("sources", []) if item.get("source_id") == source_id]
    if len(matches) != 1:
        raise SourcePermissionError(f"Source is missing or ambiguous: {source_id}")
    source = matches[0]
    status = source.get("license_status", "unknown")
    permitted = source.get("permissions", {}).get(operation) is True
    if status != "approved" or not permitted:
        raise SourcePermissionError(
            f"Source '{source_id}' is not approved for '{operation}' "
            f"(license_status={status}, permission={permitted})."
        )
