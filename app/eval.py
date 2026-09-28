"""Fast retrieval-only evaluation for the golden dataset."""
from __future__ import annotations

import json

from app.config import GOLDEN_FILE
from app.neo4j_client import Neo4jClient
from app.retrieval import Retriever


def run_eval() -> None:
    with GOLDEN_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    neo4j = Neo4jClient.from_env()

    if neo4j is None:
        raise RuntimeError("Neo4j is not configured.")

    retriever = Retriever(neo4j)

    total = len(data)
    matched = 0

    for item in data:
        question = item["question"]
        expected_urls = set(item.get("urls") or [])

        evidence = retriever.search(question, top_k=5)
        retrieved_urls = {
            e.source_url for e in evidence if e.source_url
        }

        hit = bool(expected_urls & retrieved_urls)

        if hit:
            matched += 1

        print(
            f"[{'PASS' if hit else 'FAIL'}] "
            f"ID {item['id']} | "
            f"retrieved={len(evidence)}"
        )

    rate = (matched / total * 100) if total else 0.0

    print()
    print(f"Evaluated {total} questions.")
    print(f"Source match rate: {rate:.1f}%")


if __name__ == "__main__":
    run_eval()