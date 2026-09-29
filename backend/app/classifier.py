"""Fast deterministic query routing / classification."""
from __future__ import annotations

import re


def classify_query(question: str) -> str:
    """Classifies a user query into:
    - 'historical': decisions, why-code, motivations, deprecations, PR/commit rationale
    - 'repository': codebase architecture, modules, file structure, request lifecycle, implementation
    - 'general': pure concepts, definitions, general software engineering patterns
    - 'hybrid': combinations of concept/architecture with historical decisions/why rationale
    """
    q = question.strip().lower()

    # Signals for historical / decision questions
    has_why = bool(re.search(r"\b(why|reason|rationale|motivation|tradeoff|trade-off|decision|deprecat\w*|removed|dropped|migrated|origin|history|who merged|when did|when was)\b", q))
    has_pr_commit = bool(re.search(r"\b(pr|pull request|commit|issue|changelog)\b", q) or re.search(r"#\d+", q))

    # Signals for codebase / repository understanding
    has_repo_terms = bool(re.search(
        r"\b(architecture|structure|lifecycle|modules?|major modules|files?|directory|codebase|workflow|flow|pipeline|entry point|wsgi_app|blueprint|dispatch|routing|internals|how does .+ work here|how is .+ implemented|where is .+ (handled|defined|located|called)|what happens when (a )?request enters|request enters the application)\b",
        q
    ))
    has_repo_context = bool(re.search(r"\b(in flask|in this repo|in this codebase|in pallets/flask|here)\b", q))

    # Pure conceptual / definition questions without historical or structural inquiry
    is_what_is = bool(re.search(r"^(what is|what are|explain|define|meaning of)\s+(a |an |the )?([a-z0-9_\-\s]+)\??$", q))
    short_words = q.split()
    if is_what_is and len(short_words) <= 6 and not has_repo_context and not has_why and not re.search(r"\b(architecture|structure|major modules|where is)\b", q):
        return "general"

    # Hybrid check: Combines conceptual ("what is", "how") or architectural terms with historical rationale ("why", "moved", "deprecated")
    if has_why and (bool(re.search(r"\b(what is|how does|where is|explain the structure)\b", q)) or has_repo_terms or has_repo_context) and not bool(re.search(r"^why\s+(did|was|were|is)\s+([a-z0-9_\-\.\s]+)$", q)):
        return "hybrid"

    # Repository structural / lifecycle questions
    if has_repo_terms or has_repo_context or bool(re.search(r"\b(how does|where is|explain the|how is)\b", q)):
        return "repository"

    # Historical questions
    if has_why or has_pr_commit:
        return "historical"

    if is_what_is:
        return "general"

    return "historical"
