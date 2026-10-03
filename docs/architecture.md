# Architecture

```text
GitHub REST / PyGithub
         │
         ▼
raw cache ──▶ normalized JSON
         │
         ├──────────────────────┐
         ▼                      ▼
Decision Extraction       Neo4j AuraDB (Graph)
(verbatim snippet check)        │
         │                      │
         └──────────┬───────────┘
                    ▼
           Retriever Engine
      (BM25/Lexical + Cypher Graph + Optional Embeddings)
                    │
                    ▼
           Evidence Verification
                    │
                    ▼
           LLM Synthesis Layer
    (Pinned Gemini / OpenAI-compatible with Claim Grounding)
                    │
                    ▼
           FastAPI `/ask` Endpoint
                    │
                    ▼
           Web Investigation UI
```

---

## 1. Deterministic Query Routing & Classification

Queries are classified without an external LLM call using a deterministic scoring engine defined in [`app/classifier.py`](file:///Users/akshitsharma07/Developer/Code-Archaeologist/backend/app/classifier.py).

### Signal Weights and Patterns

| Category | Matched Signal Patterns | Weight |
|---|---|---|
| **`historical`** | `why`, `why did`, `why does`, `why was`, `why were` | 3 |
| | `reason`, `rationale`, `motivation`, `tradeoff`, `decision` | 2 |
| | `deprecat*`, `removed`, `dropped`, `migrated`, `origin`, `history` | 2 |
| | `who merged`, `when did`, `when was`, `merged at`, `maintainers` | 2 |
| | `pull request`, `pr`, `commit`, `issue`, `changelog`, `fix` | 2 |
| | `#<digits>` (PR/Issue reference) | 2 |
| | `instead of`, `rather than`, `revert` | 1 |
| **`repository`** | `architecture`, `structure`, `lifecycle`, `request lifecycle` | 3 |
| | `modules`, `major modules`, `file structure`, `directory structure`, `codebase` | 2 |
| | `workflow`, `pipeline`, `entry point`, `wsgi`, `blueprint`, `dispatch`, `routing` | 2 |
| | `how does ... work`, `how is ... implemented`, `how do ... communicate` | 2 |
| | `where is ... (handled\|defined\|located\|called)` | 2 |
| | `what happens when a request enters` | 3 |
| | `in flask`, `in this repo`, `in pallets/flask` | 1 |
| **`general`** | `^what is`, `^what are`, `^define`, `^meaning of` (definition prefix) | 3 |
| | `difference between`, `concept of`, `explain the concept` | 2 |

### Tie-Break & Multi-Signal Conflict Resolution Rules

1. **Pure Definitions**: If general definition score > 0 with zero historical and zero repository tokens, routes to `general`.
2. **Historical vs Repository Ties**: If both historical and repository scores are positive and equal (`score_hist == score_repo`), **`hybrid` wins the tie-break**.
3. **Dual Strong Signals**: If both `score_hist >= 3` and `score_repo >= 3` (e.g. asking both *why* and examining *architecture* or *routing*), the query is routed to **`hybrid`** to retrieve both architectural flow and historical PR rationale.
4. **Dominant Score**: When one category strictly dominates in score, that category is selected. Incidental code keywords (e.g. `wsgi_app` in a historical question) are outscored by multiple historical tokens (`why`, `instead of`, issue `#1538`).
5. **Fallback**: If no explicit patterns match, the classifier safely defaults to `historical`.

---

## 2. Evidence Grounding & Verification Boundary

CodeArchaeologist enforces a strict evidence boundary:
- **Decision Extraction Verification**: Every evidence snippet extracted from raw GitHub sources is verified verbatim (case and whitespace-insensitive) against the underlying PR/issue/commit body. Decisions with zero matching snippets are rejected; decisions with partial matches are downgraded in confidence.
- **Answer Claim Grounding**: In answer generation, every factual sentence must cite a specific valid `evidence_id` from the retrieved evidence package. Any claim lacking a citation or referencing a fabricated/invalid citation is stripped from the response.
- **Deterministic Confidence**: Confidence is computed programmatically by `compute_deterministic_confidence()` from evidence scores and citation verification ratios—the LLM is not allowed to self-report confidence.
- **Empty Retrieval Guard**: If retrieval yields zero evidence, the LLM call is bypassed entirely, immediately returning a low-confidence fallback response to prevent hallucinated speculation.
