"""Local Hugging Face Transformers provider.

Weights are loaded lazily. Remote model downloads are disabled by default;
deployers must deliberately opt in or pre-stage a reviewed checkpoint.
"""
from __future__ import annotations

import asyncio
import threading
from typing import Any

from amin_legal_model.providers.base import ModelNotConfiguredError, ModelProvider


class TransformersProvider(ModelProvider):
    def __init__(
        self,
        model_id: str,
        *,
        local_files_only: bool = True,
        device_map: str = "auto",
        max_new_tokens: int = 2048,
        max_input_tokens: int = 8192,
        temperature: float = 0.2,
    ) -> None:
        if not model_id.strip():
            raise ValueError("model_id must not be empty.")
        if max_new_tokens < 1 or max_input_tokens < 256:
            raise ValueError("Token limits are outside safe bounds.")
        if temperature < 0:
            raise ValueError("temperature must be non-negative.")
        self.model_id = model_id
        self.local_files_only = local_files_only
        self.device_map = device_map
        self.max_new_tokens = max_new_tokens
        self.max_input_tokens = max_input_tokens
        self.temperature = temperature
        self._model: Any = None
        self._tokenizer: Any = None
        self._load_lock = threading.Lock()
        self._generation_lock = threading.Lock()

    @property
    def model_loaded(self) -> bool:
        return self._model is not None and self._tokenizer is not None

    def _load(self) -> None:
        if self.model_loaded:
            return
        with self._load_lock:
            if self.model_loaded:
                return
            try:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer
            except ImportError as exc:
                raise ModelNotConfiguredError(
                    "The configured model needs the optional inference dependencies. "
                    "Install with: pip install -e '.[inference]'."
                ) from exc
            try:
                common = {
                    "local_files_only": self.local_files_only,
                    "trust_remote_code": False,
                }
                tokenizer = AutoTokenizer.from_pretrained(self.model_id, **common)
                model_options: dict[str, Any] = {
                    **common,
                    "torch_dtype": "auto",
                    "low_cpu_mem_usage": True,
                }
                if self.device_map != "none":
                    model_options["device_map"] = self.device_map
                model = AutoModelForCausalLM.from_pretrained(self.model_id, **model_options)
                if self.device_map == "none":
                    model.to(torch.device("cpu"))
                model.eval()
                if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
                    tokenizer.pad_token_id = tokenizer.eos_token_id
                self._tokenizer = tokenizer
                self._model = model
            except Exception as exc:
                raise ModelNotConfiguredError(
                    f"Could not load model '{self.model_id}'. Verify the checkpoint, "
                    "license approval, local model files, tokenizer and available RAM/VRAM. "
                    f"Cause: {exc}"
                ) from exc

    def _format_prompt(self, system_prompt: str, user_prompt: str) -> str:
        assert self._tokenizer is not None
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        apply_template = getattr(self._tokenizer, "apply_chat_template", None)
        if callable(apply_template):
            try:
                return apply_template(messages, tokenize=False, add_generation_prompt=True)
            except (TypeError, ValueError, NotImplementedError):
                pass
        return f"System:\n{system_prompt}\n\nUser:\n{user_prompt}\n\nAssistant:\n"

    def _generate_sync(self, system_prompt: str, user_prompt: str) -> str:
        self._load()
        import torch

        with self._generation_lock:
            prompt = self._format_prompt(system_prompt, user_prompt)
            encoded = self._tokenizer(prompt, return_tensors="pt", truncation=False)
            input_ids = encoded["input_ids"]
            if input_ids.shape[-1] > self.max_input_tokens:
                raise ModelNotConfiguredError(
                    f"Input is {input_ids.shape[-1]} tokens; configured limit is "
                    f"{self.max_input_tokens}. Split the document or use retrieval."
                )
            try:
                device = next(self._model.parameters()).device
                encoded = {key: value.to(device) for key, value in encoded.items()}
            except (AttributeError, StopIteration, RuntimeError):
                pass
            generation: dict[str, Any] = {
                "max_new_tokens": self.max_new_tokens,
                "pad_token_id": self._tokenizer.pad_token_id,
                "eos_token_id": self._tokenizer.eos_token_id,
                "use_cache": True,
            }
            if self.temperature > 0:
                generation.update({"do_sample": True, "temperature": self.temperature, "top_p": 0.9})
            else:
                generation["do_sample"] = False
            try:
                with torch.inference_mode():
                    output = self._model.generate(**encoded, **generation)
                prompt_length = encoded["input_ids"].shape[-1]
                answer_tokens = output[0][prompt_length:]
                answer = self._tokenizer.decode(answer_tokens, skip_special_tokens=True).strip()
            except Exception as exc:
                raise ModelNotConfiguredError(f"Model generation failed: {exc}") from exc
            if not answer:
                raise ModelNotConfiguredError("The configured model returned an empty response.")
            return answer

    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        return await asyncio.to_thread(self._generate_sync, system_prompt, user_prompt)
