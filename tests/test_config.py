from pathlib import Path

import pytest

from amin_legal_model.config import ConfigError, load_config


def test_load_project_config() -> None:
    config_path = Path(__file__).parents[1] / "configs" / "model.yaml"
    config = load_config(config_path)
    assert config["project"]["name"] == "AMIN Legal Model"
    assert config["runtime"]["provider"] == "not_configured"


def test_reject_non_mapping_config(tmp_path: Path) -> None:
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text("- not a mapping", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(config_file)


def test_reject_missing_project_name(tmp_path: Path) -> None:
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text("project: {}\nruntime: {}", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(config_file)
