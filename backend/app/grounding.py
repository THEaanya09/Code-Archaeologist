"""Grounding and evidence-verification engine.

Enforces strict verification rules:
1. Decision Extraction: Verifies evidence snippets verbatim against original source text.
   - Discards decisions with zero verifiable snippets.
   - Downgrades confidence if only some snippets verify.
2. Answer Generation: Requires every factual claim to cite a valid retrieved evidence ID.
   - Strips claims that cite no evidence or invalid evidence IDs.
3. Deterministic Confidence: Computes confidence from evidence properties and verification ratios,
   never relying on self-reported LLM confidence values.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.models import Evidence


@dataclass(frozen=True)
class GroundedClaim:
    statement: str
    evidence_id: str
    is_valid: bool
    rejection_reason: str | None = None


def normalize_text(text: str) -> str:
    """Normalize text for case and whitespace-insensitive matching."""
    if not text:
        return ""
    # Collapse all whitespace sequences into single spaces and lower
    return " ".join(text.lower().split())


def verify_evidence_snippets(
    snippets: list[str],
    source_text: str,
    initial_confidence: str = "high",
) -> tuple[list[str], str, float]:
    """
    Verifies that every evidence snippet appears verbatim (case/whitespace-insensitive)
    in the actual source text.

    Returns:
    - verified_snippets: list of snippets verified in source text
    - final_confidence: 'high', 'medium', 'low', or 'rejected'
    - match_ratio: fraction of snippets verified (0.0 to 1.0)
    """
    if not snippets or not source_text:
        return [], "rejected", 0.0

    normalized_source = normalize_text(source_text)
    verified: list[str] = []

    for snippet in snippets:
        norm_snippet = normalize_text(snippet)
        if norm_snippet and norm_snippet in normalized_source:
            verified.append(snippet)

    total = len(snippets)
    verified_count = len(verified)
    ratio = (verified_count / total) if total else 0.0

    if verified_count == 0:
        # Zero verifiable snippets -> discard / reject
        return [], "rejected", 0.0

    if verified_count < total:
        # Partial match -> downgrade confidence
        downgrade_map = {
            "high": "medium",
            "medium": "low",
            "low": "low",
        }
        final_conf = downgrade_map.get(initial_confidence.lower(), "low")
        return verified, final_conf, ratio

    # Full match -> keep initial confidence
    return verified, initial_confidence, 1.0


def filter_and_ground_claims(
    claims: list[dict[str, Any]],
    valid_evidence_ids: set[str],
) -> tuple[list[GroundedClaim], list[GroundedClaim]]:
    """
    Strictly verifies each claim against retrieved evidence IDs.
    Drops any claim with missing or invalid citation.

    Returns:
    - accepted_claims: Claims citing a valid retrieved evidence ID
    - rejected_claims: Claims with no citation or invalid citation
    """
    accepted: list[GroundedClaim] = []
    rejected: list[GroundedClaim] = []

    for raw in claims:
        stmt = str(raw.get("statement") or raw.get("text") or raw.get("claim") or "").strip()
        ev_id = str(raw.get("evidence_id") or raw.get("citation") or raw.get("source_id") or "").strip()

        if not stmt:
            continue

        if not ev_id:
            rejected.append(GroundedClaim(
                statement=stmt,
                evidence_id="",
                is_valid=False,
                rejection_reason="Uncited claim: no evidence_id provided",
            ))
            continue

        if ev_id not in valid_evidence_ids:
            rejected.append(GroundedClaim(
                statement=stmt,
                evidence_id=ev_id,
                is_valid=False,
                rejection_reason=f"Invalid citation '{ev_id}': not in retrieved evidence package",
            ))
            continue

        accepted.append(GroundedClaim(
            statement=stmt,
            evidence_id=ev_id,
            is_valid=True,
            rejection_reason=None,
        ))

    return accepted, rejected


def compute_deterministic_confidence(
    evidence: list[Evidence],
    channels_count: int = 1,
    verified_ratio: float = 1.0,
) -> str:
    """
    Computes confidence deterministically from evidence properties:
    - top retrieval score
    - evidence snippet verification ratio
    - presence of verified URL
    - independent retrieval channels count
    """
    if not evidence or verified_ratio <= 0.0:
        return "low"

    top = evidence[0]
    if not top.source_url or top.score <= 0.0:
        return "low"

    if top.score >= 0.7 and verified_ratio >= 1.0 and channels_count >= 1 and top.confidence != "low":
        return "high"

    if top.score >= 0.3 and verified_ratio >= 0.5:
        return "medium"

    return "low"
