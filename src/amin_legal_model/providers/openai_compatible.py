"""OpenAI-compatible private inference server provider (e.g. vLLM)."""
from __future__ import annotations

import httpx

from amin_legal_model.providers.base import ModelNotConfiguredError, ModelProvider


class OpenAICompatibleProvider(ModelProvider):
    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str,
        *,
        timeout_seconds: float = 600.0,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        top_p: float = 0.95,
        top_k: int = 64,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("Model server URL must use http:// or https://.")
        if not model.strip() or not api_key.strip():
            raise ValueError("Model name and private model-server key are required.")
        if timeout_seconds <= 0 or max_tokens < 1 or temperature < 0:
            raise ValueError("Invalid inference timeout or generation settings.")
        if not 0 < top_p <= 1 or top_k < 0:
            raise ValueError("top_p must be in (0, 1] and top_k must be non-negative.")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k

    @property
    def model_loaded(self) -> bool:
        # The model runs in a separate process; readiness is verified over HTTP.
        return False

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(5.0),
                headers={"Authorization": f"Bearer {self.api_key}"},
            ) as client:
                response = await client.get(f"{self.base_url}/models")
                response.raise_for_status()
                payload = response.json()
            models = payload.get("data", [])
            return any(
                item.get("id") == self.model or item.get("root") == self.model
                for item in models
            )
        except (httpx.HTTPError, ValueError, TypeError):
            return False

    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_tokens": self.max_tokens,
        }
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout_seconds),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            ) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=body,
                )
                response.raise_for_status()
                payload = response.json()
            answer = payload["choices"][0]["message"]["content"]
            if isinstance(answer, list):
                answer = "".join(
                    part.get("text", "") for part in answer if isinstance(part, dict)
                )
            if not isinstance(answer, str) or not answer.strip():
                raise ModelNotConfiguredError("The private model server returned an empty response.")
            return answer.strip()
        except httpx.TimeoutException as exc:
            raise ModelNotConfiguredError(
                "The private model server exceeded the configured inference timeout."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ModelNotConfiguredError(
                f"The private model server rejected inference (HTTP {exc.response.status_code})."
            ) from exc
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ModelNotConfiguredError(
                f"The private model server could not complete inference: {exc}"
            ) from exc
