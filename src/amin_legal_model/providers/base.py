from abc import ABC, abstractmethod


class ModelNotConfiguredError(RuntimeError):
    """Raised when no inference model has been configured."""


class ModelProvider(ABC):
    @abstractmethod
    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        """Generate a response using the configured model."""
        raise NotImplementedError


class UnconfiguredProvider(ModelProvider):
    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        raise ModelNotConfiguredError(
            "No model provider is configured. Select and deploy a licensed model first."
        )
