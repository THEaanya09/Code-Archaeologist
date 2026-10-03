"""Tests for evidence verification, claim grounding, and deterministic confidence."""
from __future__ import annotations

import pytest

from app.grounding import (
    compute_deterministic_confidence,
    filter_and_ground_claims,
    verify_evidence_snippets,
)
from app.models import Evidence


def test_decision_with_fabricated_evidence_is_rejected():
    """Requirement 3a: A decision with fabricated/non-matching evidence is rejected."""
    source_text = """
    We are deprecating flask.ext in Flask 0.12. Maintainers contacted extension authors
    to migrate to flask_foo imports.
    """
    fabricated_snippets = [
        "Flask switched its storage engine to PostgreSQL and SQLite.",
        "A migration script was automatically bundled with Flask CLI.",
    ]

    verified, final_conf, ratio = verify_evidence_snippets(
        snippets=fabricated_snippets,
        source_text=source_text,
        initial_confidence="high",
    )

    assert verified == []
    assert final_conf == "rejected"
    assert ratio == 0.0


def test_decision_with_partially_matching_evidence_is_downgraded():
    """Requirement 3b: A decision with partially-matching evidence has its confidence downgraded."""
    source_text = """
    We are deprecating flask.ext in Flask 0.12. Maintainers contacted extension authors
    to migrate to flask_foo imports.
    """
    # Snippet 1 is verbatim (ignoring case/whitespace), snippet 2 is fabricated
    mixed_snippets = [
        "Maintainers contacted extension authors to migrate to flask_foo imports",
        "This resulted in a 45% reduction in latency for microservices",
    ]

    verified, final_conf, ratio = verify_evidence_snippets(
        snippets=mixed_snippets,
        source_text=source_text,
        initial_confidence="high",
    )

    # 1 of 2 snippets matched -> downgraded from high to medium
    assert len(verified) == 1
    assert "Maintainers contacted extension authors" in verified[0]
    assert final_conf == "medium"
    assert ratio == 0.5


def test_decision_with_full_verbatim_evidence_retains_confidence():
    """Verbatim matching preserves confidence."""
    source_text = "Caching handlers for the exception MRO caused issues with some inheritance setups."
    snippets = ["Caching handlers for the exception MRO caused issues"]

    verified, final_conf, ratio = verify_evidence_snippets(
        snippets=snippets,
        source_text=source_text,
        initial_confidence="high",
    )
    assert len(verified) == 1
    assert final_conf == "high"
    assert ratio == 1.0


def test_answer_with_uncited_or_wrongly_cited_claim_is_stripped():
    """Requirement 3c: Claims with no citation or invalid citation are stripped from final output."""
    valid_evidence_ids = {"golden-1", "golden-2"}

    raw_claims = [
        {
            "statement": "flask.ext was deprecated in version 0.12.",
            "evidence_id": "golden-1",
        },
        {
            "statement": "Flask was initially designed exclusively for tornado web servers.",
            "evidence_id": "fabricated-999",  # Invalid citation
        },
        {
            "statement": "The maintainers held a vote in Zurich.",
            "evidence_id": "",  # Uncited claim
        },
        {
            "statement": "Extensions were advised to use direct package names.",
            "evidence_id": "golden-2",
        },
    ]

    accepted, rejected = filter_and_ground_claims(raw_claims, valid_evidence_ids)

    # Only the two properly cited claims should be accepted
    assert len(accepted) == 2
    assert accepted[0].statement == "flask.ext was deprecated in version 0.12."
    assert accepted[0].evidence_id == "golden-1"
    assert accepted[1].statement == "Extensions were advised to use direct package names."
    assert accepted[1].evidence_id == "golden-2"

    # Both invalid and uncited claims must be rejected
    assert len(rejected) == 2
    rejection_reasons = [r.rejection_reason for r in rejected]
    assert any("Invalid citation" in r for r in rejection_reasons)
    assert any("Uncited claim" in r for r in rejection_reasons)

    # When reconstructing final answer, stripped claims never appear
    final_answer = " ".join(c.statement for c in accepted)
    assert "tornado" not in final_answer
    assert "Zurich" not in final_answer


def test_confidence_computed_deterministically():
    """Confidence is derived from evidence properties, never self-reported by LLM."""
    evidence = [
        Evidence(
            decision_id="golden-1",
            summary="test",
            rationale="rationale",
            source_url="https://github.com/pallets/flask/pull/1",
            score=0.9,
            confidence="high",
        )
    ]
    # Strong score + full verification -> high
    assert compute_deterministic_confidence(evidence, channels_count=1, verified_ratio=1.0) == "high"

    # Degraded verification ratio -> medium
    assert compute_deterministic_confidence(evidence, channels_count=1, verified_ratio=0.5) == "medium"

    # Zero verification ratio -> low
    assert compute_deterministic_confidence(evidence, channels_count=1, verified_ratio=0.0) == "low"

    # Zero score -> low
    evidence_zero_score = [
        Evidence(
            decision_id="golden-1",
            summary="test",
            rationale="rationale",
            source_url="https://github.com/pallets/flask/pull/1",
            score=0.0,
        )
    ]
    assert compute_deterministic_confidence(evidence_zero_score, channels_count=1, verified_ratio=1.0) == "low"
