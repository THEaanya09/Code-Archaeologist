"""Tests for configuration validation and golden dataset integrity."""
from __future__ import annotations

import json
from pathlib import Path

from app.config import GOLDEN_FILE, Settings, get_settings


def test_settings_properties():
    s = Settings(
        github_token="tok",
        github_repo="pallets/flask",
        neo4j_uri="neo4j+s://test.databases.neo4j.io",
        neo4j_username="neo4j",
        neo4j_password="pwd",
        llm_provider="openai_compatible",
        llm_base_url="https://example.com/v1",
        llm_api_key="key",
        llm_model="gemini-2.0-flash",
        embedding_provider="openai_compatible",
        embedding_base_url=None,
        embedding_api_key=None,
        embedding_model=None,
        embedding_dimensions=1536,
        extraction_mode="curated",
        expose_golden_questions=False,
    )
    assert s.neo4j_enabled is True
    assert s.llm_enabled is True
    assert s.embeddings_enabled is False
    assert s.expose_golden_questions is False


def test_golden_dataset_structure():
    """Verify that golden_questions.json exists and all entries contain required evaluation keys."""
    assert GOLDEN_FILE.exists(), f"Golden file not found at {GOLDEN_FILE}"
    with GOLDEN_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 25, f"Expected 25 curated golden questions, found {len(data)}"
    for item in data:
        assert "id" in item
        assert "question" in item
        assert "reason" in item
        assert "urls" in item
        assert isinstance(item["urls"], list)
        assert len(item["urls"]) > 0
