import asyncio
import httpx
import pytest

from amin_legal_model.providers.base import UnconfiguredProvider
from amin_legal_model.providers.factory import provider_from_environment
from amin_legal_model.providers.openai_compatible import OpenAICompatibleProvider
from amin_legal_model.providers.transformers_provider import TransformersProvider


def test_factory_defaults_to_no_model_and_no_download():
    provider = provider_from_environment({})
    assert isinstance(provider, UnconfiguredProvider)


def test_factory_configures_local_model_without_loading_weights():
    provider = provider_from_environment({
        "AMIN_MODEL_ID": "/models/egyptian-legal-model",
        "AMIN_MODEL_LOCAL_ONLY": "true",
        "AMIN_DEVICE_MAP": "auto",
        "AMIN_MAX_NEW_TOKENS": "512",
        "AMIN_MAX_INPUT_TOKENS": "4096",
    })
    assert isinstance(provider, TransformersProvider)
    assert provider.local_files_only is True
    assert provider.max_new_tokens == 512
    assert provider.model_loaded is False


def test_factory_allows_network_only_when_explicitly_requested():
    provider = provider_from_environment({
        "AMIN_MODEL_ID": "organization/reviewed-checkpoint",
        "AMIN_MODEL_LOCAL_ONLY": "false",
    })
    assert provider.local_files_only is False


def test_invalid_boolean_configuration_fails_closed():
    with pytest.raises(ValueError):
        provider_from_environment({
            "AMIN_MODEL_ID": "some/model",
            "AMIN_MODEL_LOCAL_ONLY": "sometimes",
        })


def test_factory_selects_private_vllm_server():
    provider = provider_from_environment({
        "AMIN_PROVIDER": "vllm",
        "AMIN_MODEL_SERVER_URL": "http://model:8001/v1",
        "AMIN_MODEL_SERVER_KEY": "internal-secret",
        "AMIN_MODEL_NAME": "google/gemma-4-31B-it",
    })
    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.model == "google/gemma-4-31B-it"
    assert provider.temperature == 1.0
    assert provider.top_p == 0.95
    assert provider.top_k == 64


def test_vllm_factory_requires_all_private_server_settings():
    with pytest.raises(ValueError, match="AMIN_MODEL_SERVER_URL"):
        provider_from_environment({"AMIN_PROVIDER": "vllm"})


def test_vllm_provider_sends_system_and_user_messages(monkeypatch):
    provider = OpenAICompatibleProvider(
        "http://model:8001/v1", "amin-gemma", "secret"
    )
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None
        def json(self):
            return {"choices": [{"message": {"content": "تحليل قانوني تجريبي"}}]}

    class FakeClient:
        def __init__(self, **kwargs):
            captured["headers"] = kwargs["headers"]
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return None
        async def post(self, url, json):
            captured["url"] = url
            captured["body"] = json
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
    answer = asyncio.run(provider.generate(system_prompt="تعليمات", user_prompt="وقائع"))
    assert answer == "تحليل قانوني تجريبي"
    assert captured["body"]["messages"][0]["role"] == "system"
    assert captured["body"]["messages"][1]["content"] == "وقائع"


def test_vllm_health_check_requires_configured_model(monkeypatch):
    provider = OpenAICompatibleProvider(
        "http://model:8001/v1", "amin-gemma", "secret"
    )

    class FakeResponse:
        def raise_for_status(self):
            return None
        def json(self):
            return {"data": [{"id": "amin-gemma"}]}

    class FakeClient:
        def __init__(self, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return None
        async def get(self, url):
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
    assert asyncio.run(provider.health_check()) is True
