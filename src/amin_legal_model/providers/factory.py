"""Environment-based model provider selection."""
from __future__ import annotations

import os
from collections.abc import Mapping

from amin_legal_model.providers.base import UnconfiguredProvider
from amin_legal_model.providers.transformers_provider import TransformersProvider


def _boolean(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("Boolean environment values must be true/false, 1/0, yes/no or on/off.")


def provider_from_environment(
    environ: Mapping[str, str] | None = None,
):
    env = environ if environ is not None else os.environ
    model_id = env.get("AMIN_MODEL_ID", "").strip()
    if not model_id:
        return UnconfiguredProvider()
    return TransformersProvider(
        model_id,
        local_files_only=_boolean(env.get("AMIN_MODEL_LOCAL_ONLY"), default=True),
        device_map=env.get("AMIN_DEVICE_MAP", "auto").strip() or "auto",
        max_new_tokens=int(env.get("AMIN_MAX_NEW_TOKENS", "2048")),
        max_input_tokens=int(env.get("AMIN_MAX_INPUT_TOKENS", "8192")),
        temperature=float(env.get("AMIN_TEMPERATURE", "0.2")),
    )
