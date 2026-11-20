from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when the project configuration is missing or invalid."""


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.is_file():
        raise ConfigError(f"Configuration file not found: {config_path}")

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML configuration: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Configuration root must be a YAML mapping.")

    project = data.get("project")
    if not isinstance(project, dict) or not project.get("name"):
        raise ConfigError("Configuration must define project.name.")

    runtime = data.get("runtime")
    if not isinstance(runtime, dict):
        raise ConfigError("Configuration must define a runtime mapping.")

    return data
