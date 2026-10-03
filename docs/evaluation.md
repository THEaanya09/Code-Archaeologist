# Evaluation & Benchmark Harness

The evaluation harness in [`backend/app/eval.py`](file:///Users/akshitsharma07/Developer/Code-Archaeologist/backend/app/eval.py) evaluates both the deterministic query classifier and the retrieval precision of the GraphRAG pipeline against curated benchmarks.

## 1. Running the Evaluation Suite

```bash
cd backend
python3 -m app.eval
```

This runs both benchmark evaluations and persists structured output to `data/processed/eval_results.json`.

---

## 2. Query Classifier Benchmark Results

The classifier was evaluated against the 45-question multi-category benchmark in `data/benchmark_questions.json` (25 historical, 10 repository architecture, 5 general concepts, and 5 hybrid multi-signal questions).

### Performance Summary

- **Total benchmark cases:** 45
- **Correct classifications:** 44 / 45
- **Accuracy:** **97.8%**

### Real Confusion Matrix (Rows: Expected, Columns: Predicted)

| Expected \ Predicted | `historical` | `repository` | `general` | `hybrid` | Total | Class Recall |
|---|---|---|---|---|---|---|
| **`historical`** | 25 | 0 | 0 | 0 | 25 | 100.0% |
| **`repository`** | 0 | 10 | 0 | 0 | 10 | 100.0% |
| **`general`** | 0 | 0 | 5 | 0 | 5 | 100.0% |
| **`hybrid`** | 0 | 1 | 0 | 4 | 5 | 80.0% |

### Analysis of Multi-Signal Questions & Tie-Break Resolutions

During evaluation, 14 questions triggered signals across multiple categories simultaneously:

| Question ID | Question Text | Expected | Predicted | Scores (H / R / G) | Tie-Break Applied | Resolution Rule |
|---|---|---|---|---|---|---|
| **4** | *Why did Flask 1.0 move ctx.push() inside try block in wsgi_app...* | `historical` | `historical` | 8 / 2 / 0 | No | Historical score (8) dominates code keyword `wsgi_app` (2) |
| **6** | *Why did flask run HTTPS support not include gen_cert...* | `historical` | `historical` | 3 / 1 / 0 | No | Historical score (3) dominates CLI term (1) |
| **11** | *Why was the deprecation of request.json reversed...* | `historical` | `historical` | 5 / 1 / 0 | No | Historical deprecation signals (5) dominate (1) |
| **14** | *Why did Flask 1.0 forbid dots in blueprint view function names?* | `historical` | `historical` | 3 / 2 / 0 | No | Historical score (3) dominates blueprint keyword (2) |
| **19** | *Why did maintainers want blueprint url_prefix double-slash fix...* | `historical` | `historical` | 8 / 2 / 0 | No | Historical tokens (`why`, `maintainers`, `fix`) dominate (8 vs 2) |
| **26** | *What is the architecture of this repository?* | `repository` | `repository` | 0 / 3 / 3 | No | Repository context wins over generic definition |
| **31** | *What are the major modules and how do they communicate?* | `repository` | `repository` | 0 / 4 / 3 | No | Repository module structure score (4) dominates definition (3) |
| **34** | *What is the file structure and directory layout of Flask codebase?* | `repository` | `repository` | 0 / 5 / 3 | No | Repository structural score (5) dominates definition (3) |
| **36** | *What is WSGI?* | `general` | `general` | 0 / 2 / 3 | No | Definition score (3) dominates standalone WSGI term (2) |
| **41** | *Why does the routing architecture work this way?* | `hybrid` | `hybrid` | 3 / 5 / 0 | Yes | Both historical (3) and repo (5) strongly present (both >= 3) |
| **42** | *Explain the structure of Flask and why blueprints were introduced* | `hybrid` | `hybrid` | 3 / 3 / 0 | Yes | Tied historical (3) and repo (3): hybrid wins tie-break rule |
| **43** | *How does WSGI integration work and why was it chosen?* | `hybrid` | `hybrid` | 3 / 4 / 0 | Yes | Both historical (3) and repo (4) strongly present (both >= 3) |
| **44** | *Rationale for blueprint routing architecture* | `hybrid` | `repository` | 2 / 5 / 0 | No | Repository tokens (5) dominate single rationale token (2) |
| **45** | *Why did Flask adopt Werkzeug for its routing engine and how does dispatch work?* | `hybrid` | `hybrid` | 3 / 4 / 0 | Yes | Both historical (3) and repo (4) strongly present (both >= 3) |

---

## 3. Retrieval Precision Benchmark

- **Dataset:** 25 curated golden questions in `data/golden_questions.json`
- **Metric:** Source URL match rate (fraction of questions where the retrieved evidence includes the ground-truth GitHub PR, issue, or commit URL within top 5 results)
- **Result:** **100.0%** (25/25 verified hits)

---

## 4. Benchmark API Gating (`/golden-questions`)

The `/golden-questions` API endpoint is **gated by default** (`EXPOSE_GOLDEN_QUESTIONS=false`).

**Why Gating is Required:**
Exposing the exact evaluation benchmark questions publicly over an unauthenticated API creates a high risk of benchmark memorization and data leakage. By defaulting to gated access, the evaluation suite remains isolated from test-time contamination. For local debugging or UI question suggestions, enable it explicitly:
```bash
EXPOSE_GOLDEN_QUESTIONS=true
```
