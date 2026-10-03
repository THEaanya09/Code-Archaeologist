"""Deterministic scoring-based query routing and category classification.

Scores candidate queries across categories by matching signal patterns with weights:
- 'historical': decisions, why-code, motivations, trade-offs, deprecations, PR/commit rationale
- 'repository': codebase architecture, modules, file structure, request lifecycle, internals
- 'general': pure concepts, definitions, general software engineering patterns
- 'hybrid': queries containing both strong historical rationale and repository architecture signals

Tie-Break & Conflict Resolution Rule:
- When both historical and repository scores are positive and tied (score_hist == score_repo),
  'hybrid' wins the tie-break deterministically.
- When both historical and repository scores are strongly present (score_hist >= 3 and score_repo >= 3),
  'hybrid' is selected to activate combined architectural and historical retrieval.
- Otherwise, the strictly highest category score wins.
- If no signals match, defaults safely to 'historical' for backward compatibility.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClassificationResult:
    category: str
    scores: dict[str, int]
    matched_signals: dict[str, list[str]]
    tie_break_applied: bool = False
    decision_rationale: str = ""


HISTORICAL_PATTERNS: list[tuple[str, int, str]] = [
    (r"\b(why|why did|why does|why was|why were)\b", 3, "why_prefix"),
    (r"\b(reason|rationale|motivation|tradeoff|trade-off|decision)\b", 2, "rationale_term"),
    (r"\b(deprecat\w*|removed|dropped|migrated|origin|history)\b", 2, "lifecycle_event"),
    (r"\b(who merged|when did|when was|merged at|maintainers?)\b", 2, "attribution"),
    (r"\b(pull request|pr|commit|issue|changelog|fix)\b", 2, "git_artifact"),
    (r"#\d+", 2, "issue_pr_number"),
    (r"\b(instead of|rather than|reverted|revert)\b", 1, "contrastive_choice"),
]

REPOSITORY_PATTERNS: list[tuple[str, int, str]] = [
    (r"\b(architecture|structure|lifecycle|request lifecycle)\b", 3, "architecture_core"),
    (r"\b(modules?|major modules|file structure|directory structure|codebase)\b", 2, "module_structure"),
    (r"\b(workflow|pipeline|entry point|wsgi|wsgi_app|blueprint|dispatch|routing)\b", 2, "routing_flow"),
    (r"\b(how does .+ work|how is .+ implemented)\b", 2, "mechanism"),
    (r"\b(where is .+ (handled|defined|located|called))\b", 2, "code_location"),
    (r"\b(what happens when (a )?request enters|request enters the application)\b", 3, "request_flow"),
    (r"\b(how do .+ communicate|internals)\b", 2, "component_interaction"),
    (r"\b(in flask|in this repo|in this codebase|in pallets/flask)\b", 1, "repo_scope"),
]

GENERAL_PATTERNS: list[tuple[str, int, str]] = [
    (r"^(what is|what are|define|meaning of)\s+", 3, "definition_prefix"),
    (r"\b(difference between|concept of|explain the concept)\b", 2, "conceptual_phrase"),
]


def classify_query_scored(question: str) -> ClassificationResult:
    """Deterministically score query signals across categories."""
    q = question.strip().lower()

    hist_signals = [tag for p, _, tag in HISTORICAL_PATTERNS if re.search(p, q)]
    repo_signals = [tag for p, _, tag in REPOSITORY_PATTERNS if re.search(p, q)]
    gen_signals = [tag for p, _, tag in GENERAL_PATTERNS if re.search(p, q)]

    score_hist = sum(w for p, w, _ in HISTORICAL_PATTERNS if re.search(p, q))
    score_repo = sum(w for p, w, _ in REPOSITORY_PATTERNS if re.search(p, q))
    score_gen = sum(w for p, w, _ in GENERAL_PATTERNS if re.search(p, q))

    scores = {
        "historical": score_hist,
        "repository": score_repo,
        "general": score_gen,
    }
    matched = {
        "historical": hist_signals,
        "repository": repo_signals,
        "general": gen_signals,
    }

    # 1. Pure conceptual definition with no historical and no repo tokens
    if score_gen > 0 and score_hist == 0 and score_repo == 0:
        return ClassificationResult(
            category="general",
            scores=scores,
            matched_signals=matched,
            tie_break_applied=False,
            decision_rationale="Pure definition pattern with zero historical or repository signals",
        )

    # 2. Multi-signal conflict / overlap resolution
    if score_hist > 0 and score_repo > 0:
        if score_hist == score_repo:
            return ClassificationResult(
                category="hybrid",
                scores=scores,
                matched_signals=matched,
                tie_break_applied=True,
                decision_rationale=f"Tied historical ({score_hist}) and repository ({score_repo}) signals: hybrid wins tie-break rule",
            )
        if score_hist >= 3 and score_repo >= 3:
            return ClassificationResult(
                category="hybrid",
                scores=scores,
                matched_signals=matched,
                tie_break_applied=True,
                decision_rationale=f"Both historical ({score_hist}>=3) and repository ({score_repo}>=3) are strongly present: hybrid selected",
            )
        if score_hist > score_repo:
            return ClassificationResult(
                category="historical",
                scores=scores,
                matched_signals=matched,
                tie_break_applied=False,
                decision_rationale=f"Historical score ({score_hist}) dominates repository score ({score_repo})",
            )
        return ClassificationResult(
            category="repository",
            scores=scores,
            matched_signals=matched,
            tie_break_applied=False,
            decision_rationale=f"Repository score ({score_repo}) dominates historical score ({score_hist})",
        )

    # 3. Single-category dominance
    if score_hist > 0 and score_hist >= score_gen:
        return ClassificationResult(
            category="historical",
            scores=scores,
            matched_signals=matched,
            tie_break_applied=False,
            decision_rationale=f"Historical score ({score_hist}) dominates",
        )
    if score_repo > 0 and score_repo >= score_gen:
        return ClassificationResult(
            category="repository",
            scores=scores,
            matched_signals=matched,
            tie_break_applied=False,
            decision_rationale=f"Repository score ({score_repo}) dominates",
        )
    if score_gen > 0:
        return ClassificationResult(
            category="general",
            scores=scores,
            matched_signals=matched,
            tie_break_applied=False,
            decision_rationale=f"General definition score ({score_gen}) dominates",
        )

    # 4. Fallback when zero explicit keywords match
    return ClassificationResult(
        category="historical",
        scores=scores,
        matched_signals=matched,
        tie_break_applied=False,
        decision_rationale="No explicit keywords matched; safe default to historical",
    )


def classify_query(question: str) -> str:
    """Classifies a user query into 'historical', 'repository', 'general', or 'hybrid'."""
    return classify_query_scored(question).category
