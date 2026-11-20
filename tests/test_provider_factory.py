import pytest

from amin_legal_model.providers.base import UnconfiguredProvider
from amin_legal_model.providers.factory import provider_from_environment
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
