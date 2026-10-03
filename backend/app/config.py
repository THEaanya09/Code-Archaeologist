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
    expose_golden_questions: bool = False
    cors_origins: tuple[str, ...] = ("http://localhost:3000", "http://127.0.0.1:3000")

    # ── Sarvam AI Configuration ──────────────────────────────────────
    sarvam_api_key: str | None = None
    sarvam_model: str = "sarvam-105b"
    sarvam_base_url: str = "https://api.sarvam.ai"

    # ── Token Optimization & Rate Limiting ───────────────────────────
    max_input_tokens: int = 4000
    max_output_tokens: int = 1000
    max_history_messages: int = 6
    max_retrieved_chunks: int = 5
    daily_request_limit: int = 20

    @property
    def neo4j_enabled(self) -> bool:
        return bool(self.neo4j_uri and self.neo4j_username and self.neo4j_password)

    @property
    def llm_enabled(self) -> bool:
        if self.llm_provider == "sarvam":
            return bool(self.sarvam_api_key and self.sarvam_model)
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
        llm_provider=_env("LLM_PROVIDER", "sarvam") or "sarvam",
        llm_base_url=_env("LLM_BASE_URL", "http://127.0.0.1:11434/v1") or "http://127.0.0.1:11434/v1",
        llm_api_key=_env("LLM_API_KEY"),
        llm_model=_env("LLM_MODEL", "sarvam-105b"),
        embedding_provider=_env("EMBEDDING_PROVIDER", "openai_compatible") or "openai_compatible",
        embedding_base_url=_env("EMBEDDING_BASE_URL"),
        embedding_api_key=_env("EMBEDDING_API_KEY"),
        embedding_model=_env("EMBEDDING_MODEL"),
        embedding_dimensions=int(_env("EMBEDDING_DIMENSIONS", "1536") or "1536"),
        extraction_mode=_env("EXTRACTION_MODE", "curated") or "curated",
        expose_golden_questions=(_env("EXPOSE_GOLDEN_QUESTIONS", "false") or "false").lower() in ("true", "1", "yes"),
        cors_origins=cors_origins,
        # Sarvam AI
        sarvam_api_key=_env("SARVAM_API_KEY"),
        sarvam_model=_env("SARVAM_MODEL", "sarvam-105b") or "sarvam-105b",
        sarvam_base_url=_env("SARVAM_BASE_URL", "https://api.sarvam.ai") or "https://api.sarvam.ai",
        # Token optimization
        max_input_tokens=int(_env("MAX_INPUT_TOKENS", "4000") or "4000"),
        max_output_tokens=int(_env("MAX_OUTPUT_TOKENS", "1000") or "1000"),
        max_history_messages=int(_env("MAX_HISTORY_MESSAGES", "6") or "6"),
        max_retrieved_chunks=int(_env("MAX_RETRIEVED_CHUNKS", "5") or "5"),
        daily_request_limit=int(_env("DAILY_REQUEST_LIMIT", "20") or "20"),
    )


def ensure_data_dirs() -> None:
    for path in (RAW_DIR, NORMALIZED_DIR, PROCESSED_DIR):
        path.mkdir(parents=True, exist_ok=True)
