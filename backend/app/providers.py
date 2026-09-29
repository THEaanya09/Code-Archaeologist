"""Replaceable LLM and embedding providers using an OpenAI-compatible API."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import requests

from app.config import Settings, get_settings


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system: str, user: str) -> str:
        raise NotImplementedError


class OpenAICompatibleLLM(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def generate(self, system: str, user: str) -> str:
        models_to_try = [self.model]
        # If model is a Gemini variant, configure resilient fallback sequence
        # gemini-2.0-flash is most stable; others follow in order of reliability
        if "gemini" in self.model.lower():
            for alt in [
                "gemini-2.0-flash",
                "gemini-2.5-flash",
                "gemini-flash-latest",
                "gemini-3.8-flash",
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
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
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
    if s.llm_provider != "openai_compatible":
        raise ValueError(f"Unsupported LLM provider: {s.llm_provider}")
    return OpenAICompatibleLLM(s.llm_base_url, s.llm_api_key or "", s.llm_model or "")


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
