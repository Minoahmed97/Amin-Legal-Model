"""Environment-based model provider selection."""
from __future__ import annotations

import os
from collections.abc import Mapping

from amin_legal_model.providers.base import UnconfiguredProvider
from amin_legal_model.providers.openai_compatible import OpenAICompatibleProvider
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


def provider_from_environment(environ: Mapping[str, str] | None = None):
    env = environ if environ is not None else os.environ
    provider_type = env.get("AMIN_PROVIDER", "").strip().lower()
    model_server_url = env.get("AMIN_MODEL_SERVER_URL", "").strip()
    model_server_key = env.get("AMIN_MODEL_SERVER_KEY", "").strip()
    model_name = env.get("AMIN_MODEL_NAME", "").strip()

    if provider_type == "vllm" or model_server_url:
        if not model_server_url or not model_server_key or not model_name:
            raise ValueError(
                "vLLM provider requires AMIN_MODEL_SERVER_URL, "
                "AMIN_MODEL_SERVER_KEY and AMIN_MODEL_NAME."
            )
        return OpenAICompatibleProvider(
            model_server_url,
            model_name,
            model_server_key,
            timeout_seconds=float(env.get("AMIN_INFERENCE_TIMEOUT_SECONDS", "600")),
            max_tokens=int(env.get("AMIN_MAX_NEW_TOKENS", "4096")),
            temperature=float(env.get("AMIN_TEMPERATURE", "1.0")),
            top_p=float(env.get("AMIN_TOP_P", "0.95")),
            top_k=int(env.get("AMIN_TOP_K", "64")),
        )

    model_id = env.get("AMIN_MODEL_ID", "").strip()
    if not model_id:
        return UnconfiguredProvider()
    if provider_type not in {"", "transformers"}:
        raise ValueError(f"Unsupported AMIN_PROVIDER: {provider_type}")
    return TransformersProvider(
        model_id,
        local_files_only=_boolean(env.get("AMIN_MODEL_LOCAL_ONLY"), default=True),
        device_map=env.get("AMIN_DEVICE_MAP", "auto").strip() or "auto",
        max_new_tokens=int(env.get("AMIN_MAX_NEW_TOKENS", "2048")),
        max_input_tokens=int(env.get("AMIN_MAX_INPUT_TOKENS", "8192")),
        temperature=float(env.get("AMIN_TEMPERATURE", "0.2")),
    )
