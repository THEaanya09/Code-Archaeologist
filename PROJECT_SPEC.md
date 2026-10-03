# CodeArchaeologist - Project Specification

## Problem
New engineers, contributors, and maintainers can read what code does, but the reasoning behind historical design choices is often scattered across commits, pull requests, issues, comments, people, and dates. CodeArchaeologist reconstructs that reasoning as evidence-backed answers.

## Core Flow
User question -> deterministic query classification -> graph traversal + lexical retrieval -> evidence package assembly -> grounded answer synthesis with mandatory claim citations -> sources + people/date + graph path.

## MVP Scope
One public repository: `pallets/flask`.

The MVP focuses on Files, Commits, PRs, Issues, People, and Decisions. It prioritizes evidence verification and ground truth reliability over autonomous agent execution or cross-repository indexing.

## Evidence Verification & Grounding Mechanism (Anti-Hallucination)
The LLM serves strictly as an answer synthesis layer, not an ungrounded generator of facts. Grounding is enforced through programmatic verification gates:

1. **Verbatim Snippet Verification in Decision Extraction**:
   - Every candidate evidence snippet must match verbatim (case/whitespace-insensitive) in the source PR, issue, or commit text.
   - Any decision with zero verifiable snippets is discarded.
   - Decisions with partial snippet matches have their confidence downgraded (`high` -> `medium`, `medium` -> `low`).
2. **Mandatory Claim Citations in Answer Generation**:
   - The LLM is instructed to structure responses as individual factual claims, each citing a specific `evidence_id` from the retrieved evidence package.
   - Any claim that lacks a citation or references an invalid `evidence_id` is programmatically stripped from the output before delivery to the user.
3. **Deterministic Confidence Metric**:
   - Confidence is computed algorithmically via `compute_deterministic_confidence()` from evidence retrieval scores and snippet verification ratios.
   - The LLM is prohibited from self-reporting confidence.
4. **Zero-Evidence Guard**:
   - If retrieval finds no relevant evidence, the system bypasses the LLM entirely, returning an immediate low-confidence refusal rather than prompting the model with an empty evidence package.

## Ground Truth & Benchmarks
- `data/golden_questions.json`: 25 curated WHY questions with verified source URLs and historical rationale. Missing commit SHAs are treated as legitimate when the decision originated in issue-only discussions.
- `data/benchmark_questions.json`: 45-question multi-category benchmark for query classification and tie-break validation.

## Architecture
GitHub API / PyGithub -> cached raw data -> normalized JSON -> Neo4j AuraDB -> verbatim decision extraction -> multi-channel retrieval -> grounded GraphRAG answer layer -> FastAPI `/ask` -> web investigation UI.

## Limitations
- **Single repository scope**: Ingested dataset covers `pallets/flask` (25 golden decisions + recent PR/issue samples), not a full 14-year commit tree crawl.
- **Model dependency**: Generation phrasing depends on the configured LLM; exact wording is not bit-for-bit reproducible across model versions. Pinned model identifiers (`gemini-2.0-flash`) prevent unannounced drift.
- **Heuristic confidence**: Confidence represents a rule-based heuristic derived from evidence presence and verification ratios, not a calibrated statistical probability.
