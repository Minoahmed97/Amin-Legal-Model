from pathlib import Path

import pytest

from amin_legal_model.source_policy import (
    SourcePermissionError,
    load_source_register,
    require_source_permission,
)


def test_project_register_loads_and_defaults_to_deny() -> None:
    register = load_source_register()
    assert len(register["sources"]) >= 5
    with pytest.raises(SourcePermissionError):
        require_source_permission(
            "egyptian_court_of_cassation",
            "automated_access",
            register=register,
        )


def test_unknown_source_is_rejected() -> None:
    with pytest.raises(SourcePermissionError, match="missing or ambiguous"):
        require_source_permission("not_registered", "store", register={"sources": []})


def test_approved_permission_is_operation_specific() -> None:
    register = {
        "sources": [{
            "source_id": "licensed_test_source",
            "license_status": "approved",
            "permissions": {"store": True, "train_or_finetune": False},
        }]
    }
    require_source_permission("licensed_test_source", "store", register=register)
    with pytest.raises(SourcePermissionError):
        require_source_permission("licensed_test_source", "train_or_finetune", register=register)


def test_non_approved_status_is_rejected_even_if_flag_true() -> None:
    register = {
        "sources": [{
            "source_id": "research_source",
            "license_status": "research_only",
            "permissions": {"manual_access": True},
        }]
    }
    with pytest.raises(SourcePermissionError):
        require_source_permission("research_source", "manual_access", register=register)
