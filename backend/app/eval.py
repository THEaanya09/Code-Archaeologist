"""Evaluation harness for CodeArchaeologist: query classifier and retrieval precision."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.classifier import classify_query_scored
from app.config import DATA_DIR, GOLDEN_FILE, PROCESSED_DIR
from app.neo4j_client import Neo4jClient
from app.retrieval import Retriever

BENCHMARK_FILE = DATA_DIR / "benchmark_questions.json"


def evaluate_classifier() -> dict[str, Any]:
    """Run classifier on benchmark dataset and compute real confusion matrix and metrics."""
    if not BENCHMARK_FILE.exists():
        raise FileNotFoundError(f"Benchmark file not found: {BENCHMARK_FILE}")

    with BENCHMARK_FILE.open("r", encoding="utf-8") as f:
        cases = json.load(f)

    categories = ["historical", "repository", "general", "hybrid"]
    matrix: dict[str, dict[str, int]] = {
        expected: {pred: 0 for pred in categories} for expected in categories
    }

    multi_signal_cases: list[dict[str, Any]] = []
    correct = 0
    total = len(cases)

    for item in cases:
        q = item["question"]
        expected = item["expected_category"]
        result = classify_query_scored(q)
        pred = result.category

        if expected in matrix and pred in matrix[expected]:
            matrix[expected][pred] += 1

        is_match = (pred == expected)
        if is_match:
            correct += 1

        # Check if question triggered multiple signals
        active_signals = {cat: score for cat, score in result.scores.items() if score > 0}
        if len(active_signals) > 1 or result.tie_break_applied:
            multi_signal_cases.append({
                "id": item["id"],
                "question": q,
                "expected": expected,
                "predicted": pred,
                "scores": result.scores,
                "matched_signals": result.matched_signals,
                "tie_break_applied": result.tie_break_applied,
                "rationale": result.decision_rationale,
            })

    accuracy = (correct / total * 100.0) if total else 0.0

    print("=" * 68)
    print("QUERY CLASSIFIER EVALUATION REPORT")
    print("=" * 68)
    print(f"Total benchmark questions: {total}")
    print(f"Correctly classified:     {correct}/{total} ({accuracy:.1f}%)")
    print()
    print("CONFUSION MATRIX (Rows: Expected, Columns: Predicted)")
    header = f"{'Expected \\ Pred':<16} | " + " | ".join(f"{c:>11}" for c in categories) + " | Total"
    print(header)
    print("-" * len(header))
    for expected in categories:
        row_counts = [matrix[expected][pred] for pred in categories]
        row_sum = sum(row_counts)
        row_str = f"{expected:<16} | " + " | ".join(f"{cnt:>11}" for cnt in row_counts) + f" | {row_sum:>5}"
        print(row_str)
    print()

    print(f"MULTI-SIGNAL / OVERLAPPING CASES IDENTIFIED: {len(multi_signal_cases)}")
    for case in multi_signal_cases:
        status = "MATCH" if case["expected"] == case["predicted"] else "MISMATCH"
        print(f"- [{status}] ID {case['id']}: expected '{case['expected']}', got '{case['predicted']}'")
        print(f"  Scores: {case['scores']} | Tie-break: {case['tie_break_applied']}")
        print(f"  Resolution: {case['rationale']}")
    print("=" * 68)

    return {
        "total": total,
        "correct": correct,
        "accuracy_pct": round(accuracy, 2),
        "confusion_matrix": matrix,
        "multi_signal_cases": multi_signal_cases,
    }


def evaluate_retrieval() -> dict[str, Any]:
    """Run retrieval-only evaluation against golden questions."""
    with GOLDEN_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    neo4j = Neo4jClient.from_env()
    if neo4j is None:
        raise RuntimeError("Neo4j is not configured.")

    retriever = Retriever(neo4j)
    total = len(data)
    matched = 0
    results = []

    for item in data:
        question = item["question"]
        expected_urls = set(item.get("urls") or [])
        evidence = retriever.search(question, top_k=5)
        retrieved_urls = {e.source_url for e in evidence if e.source_url}
        hit = bool(expected_urls & retrieved_urls)

        if hit:
            matched += 1

        results.append({
            "id": item["id"],
            "question": question,
            "hit": hit,
            "expected_urls": list(expected_urls),
            "retrieved_urls": list(retrieved_urls),
        })

    rate = (matched / total * 100.0) if total else 0.0

    print("RETRIEVAL EVALUATION REPORT")
    print(f"Evaluated {total} golden questions.")
    print(f"Source match rate: {rate:.1f}% ({matched}/{total})")
    print()

    return {
        "total": total,
        "matched": matched,
        "match_rate_pct": round(rate, 2),
        "details": results,
    }


def run_eval() -> None:
    classifier_results = evaluate_classifier()

    retrieval_results = None
    try:
        retrieval_results = evaluate_retrieval()
    except Exception as exc:
        print(f"Retrieval evaluation skipped / error: {exc}")

    eval_summary = {
        "classifier": classifier_results,
        "retrieval": retrieval_results,
    }

    out_file = PROCESSED_DIR / "eval_results.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(eval_summary, f, indent=2)
    print(f"Full evaluation saved to: {out_file}")


if __name__ == "__main__":
    run_eval()