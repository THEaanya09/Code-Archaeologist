"""Environment-based application configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
NORMALIZED_DIR = DATA_DIR / "normalized"
PROCESSED_DIR = DATA_DIR / "processed"
GOLDEN_FILE = DATA_DIR / "golden_questions.json"


@dataclass(frozen=True)
class Settings:
    github_token: str | None
    github_repo: str
    neo4j_uri: str | None
    neo4j_username: str | None
    neo4j_password: str | None
    llm_provider: str
    llm_base_url: str
    llm_api_key: str | None
    llm_model: str | None
    embedding_provider: str
    embedding_base_url: str | None
    embedding_api_key: str | None
    embedding_model: str | None
    embedding_dimensions: int
    extraction_mode: str
    cors_origins: tuple[str, ...] = ("http://localhost:3000", "http://127.0.0.1:3000")

    @property
    def neo4j_enabled(self) -> bool:
        return bool(self.neo4j_uri and self.neo4j_username and self.neo4j_password)

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_api_key and self.llm_model)

    @property
    def embeddings_enabled(self) -> bool:
        return bool(self.embedding_api_key and self.embedding_model)


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if value is None:
        return None
    value = value.strip()
    return value or None


def get_settings() -> Settings:
    cors_raw = _env("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000") or "http://localhost:3000,http://127.0.0.1:3000"
    cors_origins = tuple(o.strip() for o in cors_raw.split(",") if o.strip())
    return Settings(
        github_token=_env("GITHUB_TOKEN"),
        github_repo=_env("GITHUB_REPO", "pallets/flask") or "pallets/flask",
        neo4j_uri=_env("NEO4J_URI"),
        neo4j_username=_env("NEO4J_USERNAME"),
        neo4j_password=_env("NEO4J_PASSWORD"),
        llm_provider=_env("LLM_PROVIDER", "openai_compatible") or "openai_compatible",
        llm_base_url=_env("LLM_BASE_URL", "http://127.0.0.1:11434/v1") or "http://127.0.0.1:11434/v1",
        llm_api_key=_env("LLM_API_KEY", "ollama"),
        llm_model=_env("LLM_MODEL", "qwen:latest"),
        embedding_provider=_env("EMBEDDING_PROVIDER", "openai_compatible") or "openai_compatible",
        embedding_base_url=_env("EMBEDDING_BASE_URL"),
        embedding_api_key=_env("EMBEDDING_API_KEY"),
        embedding_model=_env("EMBEDDING_MODEL"),
        embedding_dimensions=int(_env("EMBEDDING_DIMENSIONS", "1536") or "1536"),
        extraction_mode=_env("EXTRACTION_MODE", "curated") or "curated",
        cors_origins=cors_origins,
    )


def ensure_data_dirs() -> None:
    for path in (RAW_DIR, NORMALIZED_DIR, PROCESSED_DIR):
        path.mkdir(parents=True, exist_ok=True)
