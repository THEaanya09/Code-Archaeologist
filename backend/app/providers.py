"""Replaceable LLM and embedding providers using an OpenAI-compatible API."""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import requests

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system: str, user: str, history: list[dict[str, str]] | None = None) -> str:
        """Generate a response from the LLM.

        Args:
            system: System prompt.
            user: User message.
            history: Optional list of prior conversation messages [{"role": ..., "content": ...}].

        Returns:
            The generated text response.
        """
        raise NotImplementedError

    def get_last_usage(self) -> dict[str, int] | None:
        """Return token usage info from the last API call, if available."""
        return None


class SarvamLLM(LLMProvider):
    """Sarvam AI LLM provider using the OpenAI-compatible chat completions API."""

    def __init__(self, base_url: str, api_key: str, model: str, max_output_tokens: int = 1000) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.max_output_tokens = max_output_tokens
        self._last_usage: dict[str, int] | None = None
        # Reuse a single session for connection pooling
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "api-subscription-key": self.api_key,
        })

    def generate(self, system: str, user: str, history: list[dict[str, str]] | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": self.max_output_tokens,
        }

        try:
            response = self._session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=60,
            )

            if response.status_code == 429:
                raise RuntimeError("Sarvam AI rate limit exceeded. Please wait and try again.")
            if response.status_code == 401:
                raise RuntimeError("Sarvam AI authentication failed. Check your API key.")
            if response.status_code >= 500:
                raise RuntimeError(f"Sarvam AI server error (HTTP {response.status_code}). Try again later.")

            response.raise_for_status()
            data = response.json()

            # Track token usage
            usage = data.get("usage")
            if usage:
                self._last_usage = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }
            else:
                self._last_usage = None

            choices = data.get("choices", [])
            if not choices:
                raise RuntimeError("Sarvam AI returned empty response (no choices).")

            content = choices[0].get("message", {}).get("content", "")
            if not content:
                raise RuntimeError("Sarvam AI returned empty content in response.")

            return content.strip()

        except requests.exceptions.Timeout:
            raise RuntimeError("Sarvam AI request timed out. The server may be overloaded.")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Cannot connect to Sarvam AI. Check your network connection.")

    def get_last_usage(self) -> dict[str, int] | None:
        return self._last_usage


class OpenAICompatibleLLM(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def generate(self, system: str, user: str, history: list[dict[str, str]] | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user})

        models_to_try = [self.model]
        # Pinned failover cascade: explicit versioned model identifiers only (no -latest aliases)
        # Prevents silent drift and breaking changes from unpinned model aliases
        if "gemini" in self.model.lower():
            for alt in [
                "gemini-2.0-flash",
                "gemini-2.5-flash",
                "gemini-1.5-flash",
                "gemini-3.5-flash",
            ]:
                if alt not in models_to_try:
                    models_to_try.append(alt)

        last_error = None
        for m in models_to_try:
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": m,
                        "messages": messages,
                        "temperature": 0,
                    },
                    timeout=20,  # 20s per candidate
                )
                if response.status_code == 200:
                    payload = response.json()
                    return payload["choices"][0]["message"]["content"]
                elif response.status_code in (503, 429, 500):
                    last_error = f"HTTP {response.status_code} on {m}"
                    continue
                else:
                    response.raise_for_status()
            except Exception as exc:
                last_error = str(exc)
                continue

        if last_error:
            raise RuntimeError(f"All LLM candidate models failed. Last error: {last_error}")
        raise RuntimeError("LLM generation failed with empty response.")


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class OpenAICompatibleEmbeddings(EmbeddingProvider):
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def embed(self, text: str) -> list[float]:
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": self.model, "input": text},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


def make_llm(settings: Settings | None = None) -> LLMProvider | None:
    s = settings or get_settings()
    if not s.llm_enabled:
        return None
    if s.llm_provider == "sarvam":
        if not s.sarvam_api_key:
            logger.warning("Sarvam provider selected but SARVAM_API_KEY not set.")
            return None
        return SarvamLLM(
            base_url=s.sarvam_base_url,
            api_key=s.sarvam_api_key,
            model=s.sarvam_model,
            max_output_tokens=s.max_output_tokens,
        )
    if s.llm_provider == "openai_compatible":
        return OpenAICompatibleLLM(s.llm_base_url, s.llm_api_key or "", s.llm_model or "")
    raise ValueError(f"Unsupported LLM provider: {s.llm_provider}")


def make_embeddings(settings: Settings | None = None) -> EmbeddingProvider | None:
    s = settings or get_settings()
    if not s.embeddings_enabled:
        return None
    if s.embedding_provider != "openai_compatible":
        raise ValueError(f"Unsupported embedding provider: {s.embedding_provider}")
    return OpenAICompatibleEmbeddings(
        s.embedding_base_url or s.llm_base_url,
        s.embedding_api_key or s.llm_api_key or "",
        s.embedding_model or "",
    )


def parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise
        return json.loads(cleaned[start : end + 1])

