"""Tests for deterministic scoring-based query classification and tie-break rules."""
from __future__ import annotations

import pytest

from app.classifier import classify_query, classify_query_scored


def test_single_signal_historical():
    """Verify single-signal historical questions route to 'historical'."""
    assert classify_query("Why was flask.ext deprecated in Flask 1.0?") == "historical"
    assert classify_query("What was the motivation behind commit b80cf057?") == "historical"
    assert classify_query("Who merged pull request #2254?") == "historical"
    assert classify_query("Why did maintainers reject the config option?") == "historical"


def test_single_signal_repository():
    """Verify single-signal repository questions route to 'repository'."""
    assert classify_query("What is the architecture of this repository?") == "repository"
    assert classify_query("Explain the structure of Flask.") == "repository"
    assert classify_query("How does the request lifecycle work?") == "repository"
    assert classify_query("Where is routing handled in Flask?") == "repository"
    assert classify_query("What happens when a request enters the application?") == "repository"
    assert classify_query("How do the major modules communicate?") == "repository"


def test_single_signal_general():
    """Verify single-signal conceptual questions route to 'general'."""
    assert classify_query("What is WSGI?") == "general"
    assert classify_query("What are thread locals?") == "general"
    assert classify_query("Define reverse proxy") == "general"
    assert classify_query("Explain the concept of application context") == "general"


def test_overlapping_hybrid_real_examples():
    """Verify multi-signal questions with overlapping architectural + historical rationale."""
    # Example 1: explicitly requested in prompt
    q1 = "Why does the routing architecture work this way?"
    res1 = classify_query_scored(q1)
    assert res1.category == "hybrid"
    assert res1.scores["historical"] >= 3  # "why"
    assert res1.scores["repository"] >= 3  # "architecture" + "routing"
    assert res1.tie_break_applied is True

    # Example 2: structure + why rationale
    q2 = "Explain the structure of Flask and why blueprints were introduced"
    res2 = classify_query_scored(q2)
    assert res2.category == "hybrid"
    assert res2.scores["historical"] >= 3
    assert res2.scores["repository"] >= 3
    assert res2.tie_break_applied is True

    # Example 3: WSGI lifecycle mechanism + why choice
    q3 = "How does WSGI integration work and why was it chosen?"
    res3 = classify_query_scored(q3)
    assert res3.category == "hybrid"
    assert res3.scores["historical"] >= 3
    assert res3.scores["repository"] >= 3
    assert res3.tie_break_applied is True


def test_tied_signals_tie_break_rule():
    """Verify that when historical and repository scores are tied, 'hybrid' wins."""
    # "Why dispatch?" has historical=3 ('why') and repository=2 ('dispatch') -> historical dominates
    res_dom = classify_query_scored("Why dispatch?")
    assert res_dom.category == "historical"
    assert res_dom.scores["historical"] > res_dom.scores["repository"]

    # "Rationale for blueprint" has historical=2 ('rationale') and repository=2 ('blueprint') -> exact tie
    res_tied = classify_query_scored("Rationale for blueprint")
    assert res_tied.category == "hybrid"
    assert res_tied.scores["historical"] == 2
    assert res_tied.scores["repository"] == 2
    assert res_tied.tie_break_applied is True
    assert "hybrid wins tie-break rule" in res_tied.decision_rationale


def test_historical_dominates_when_incidental_code_terms_present():
    """Golden questions mentioning function names or code tokens still route to 'historical'."""
    q = "Why did Flask 1.0 move ctx.push() inside the try block in wsgi_app instead of adopting the more involved fix proposed in #1538?"
    res = classify_query_scored(q)
    assert res.category == "historical"
    # Historical signals (why, instead of, fix, #1538) outscore single token wsgi_app
    assert res.scores["historical"] > res.scores["repository"]
