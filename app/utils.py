"""Small deterministic utilities used by the pipeline."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "been", "before", "being",
    "but", "by", "can", "did", "does", "for", "from", "how", "in", "instead", "into",
    "is", "it", "its", "like", "make", "made", "of", "on", "or", "so", "that", "the",
    "their", "them", "there", "this", "to", "was", "were", "what", "when", "why", "with",
    "would", "flask", "repo", "repository", "version", "one", "two", "use", "using", "used",
}


def tokenize(text: str) -> list[str]:
    raw = re.findall(r"[A-Za-z0-9_.-]+", text.lower())
    tokens: list[str] = []
    for token in raw:
        if token in STOPWORDS:
            continue
        if token.isdigit():
            continue
        if len(token) < 2:
            continue
        tokens.append(token)
    return tokens


def lexical_score(query: str, text: str) -> float:
    """Return a [0,1] overlap score, ignoring generic question words."""
    q = set(tokenize(query))
    t = set(tokenize(text))
    if not q or not t:
        return 0.0

    overlap = q & t
    if not overlap:
        return 0.0

    # Recall over distinctive query terms is the primary relevance signal.
    recall = len(overlap) / len(q)
    phrase_bonus = 0.1 if query.lower().strip() in text.lower() else 0.0
    return min(1.0, round(recall + phrase_bonus, 6))


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)


def unique_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
