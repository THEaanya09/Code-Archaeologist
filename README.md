# CodeArchaeologist

> **Understand any codebase — not just why, but what, how, where, and who.**

CodeArchaeologist is a **repository intelligence assistant** built on FastAPI, GraphRAG, Neo4j, and an OpenAI-compatible LLM endpoint. It ingests a GitHub repository's full history — commits, pull requests, issues, discussions, and decisions — into a knowledge graph and answers questions across four distinct modes:

| Mode | Example Question |
|------|-----------------|
| 📜 **Historical · Why** | *"Why was `request.json` deprecated?"* |
| 🏛 **Repository · Architecture** | *"What is the architecture of Flask?"* |
| 💡 **General · Concepts** | *"What is WSGI?"* |
| 🔀 **Hybrid** | *"Why does Flask use WSGI and how is it implemented here?"* |

Target repository: **`pallets/flask`** (configurable via `.env`).

---

## Table of Contents

- [Demo](#demo)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Backend Pipeline Commands](#backend-pipeline-commands)
- [API Reference](#api-reference)
- [Query Routing & Evaluation](#query-routing--evaluation)
- [Limitations](#limitations)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)

---

## Demo

The investigation page opens with a three-column question showcase grouped by category. Click any question to immediately query the pipeline:

```
📜 Historical · Why           🏛 Repository · Architecture     💡 General · Concepts
────────────────────          ──────────────────────────────   ──────────────────────
Why was request.json          What is the architecture         What is WSGI?
  deprecated?                   of Flask?
Why was before_request        How does the request             What is middleware?
  introduced?                   lifecycle work?
Why did Flask move to         Where is routing handled?        What is a request context?
  Blueprints?
Why was ApplicationContext    What are the major modules?      What is dependency injection?
  separated?
```

Answers adapt their layout to the question type:
- **Historical** → Evidence trail · Contributors · Timeline · Related code
- **Repository** → Architecture overview · Execution flow stepper · Module grid · Key files
- **General** → Concept definition · How it works · *Inside pallets/flask* grounded section
- **Hybrid** → Architecture context combined with historical decision rationale

---

## How It Works

```
User question
      │
      ▼
┌─────────────────┐
│  Query Classifier│  ── deterministic heuristics ──▶  historical / repository / general / hybrid
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Differentiated Retrieval        │
│  historical  → decisions, PRs, issues   │
│  repository  → code entities, modules,  │
│                files, graph paths       │
│  general     → concept anchors +        │
│                optional repo context    │
│  hybrid      → both streams merged      │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│      Category-tailored LLM Synthesis    │
│  SYSTEM_HISTORICAL / SYSTEM_REPOSITORY  │
│  SYSTEM_GENERAL   / SYSTEM_HYBRID       │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Structured AskResponse          │
│  answer · evidence · overview · flow    │
│  modules · files · people · dates       │
└─────────────────────────────────────────┘
         │
         ▼
    Frontend renders
    per-category UI
```

### Evidence Grounding & Anti-Hallucination Mechanism

CodeArchaeologist does not rely on prompt assertions alone to prevent hallucinations. It enforces concrete programmatic verification gates in code:

1. **Verbatim Snippet Verification in Extraction**:
   - Every candidate evidence snippet extracted from raw GitHub sources is verified verbatim (case and whitespace-insensitive) against the underlying PR, issue, or commit text.
   - Any decision with zero verifiable snippets is discarded.
   - Decisions with partial snippet matches have their confidence downgraded (`high` → `medium`, `medium` → `low`).
2. **Mandatory Claim Citations in Answer Generation**:
   - The LLM is instructed to structure answers as individual claims, where every factual sentence must cite a specific `evidence_id` from the retrieved evidence package.
   - Any claim that lacks a citation or references an invalid `evidence_id` is programmatically stripped from the output before delivery.
3. **Deterministic Confidence Metric**:
   - Confidence is computed algorithmically via `compute_deterministic_confidence()` from evidence scores and citation verification ratios.
   - The LLM is prohibited from self-reporting confidence.
4. **Zero-Evidence Guard**:
   - If retrieval finds no relevant evidence, the system bypasses the LLM entirely, returning an immediate low-confidence refusal (`"no_evidence"`) rather than prompting the model with an empty evidence package.

## Architecture

### Backend (FastAPI · Python)

```
Request
  → api.py (FastAPI, CORS)
  → graphrag.py (GraphRAGEngine)
      → classifier.py  (classify query: historical / repository / general / hybrid)
      → retrieval.py   (Retriever — differentiated Neo4j + vector search)
          → neo4j_client.py (Aura connection, READ routing, certifi TLS)
          → repo_context.py (static Flask module catalogue & execution flow)
      → answer.py      (LLM synthesis — 4 specialised system prompts)
          → providers.py (OpenAICompatibleLLM with Gemini failover cascade)
      → models.py      (Pydantic AskResponse — 16 fields)
  ← AskResponse JSON
```

### Frontend (Next.js 15 · TypeScript)

```
app/
  page.tsx          → Dashboard (stats, recent decisions)
  investigate/      → Investigation page (search + adaptive answer UI)
  decisions/        → Decisions browser

components/
  investigation/
    SearchBar        → query input with golden-question suggestions
    AnswerPanel      → adaptive renderer (4 modes)
    EvidenceCard     → per-source evidence display
    GraphPath        → Neo4j graph traversal visualisation
  dashboard/
    StatsCards       → live repository stats
  layout/
    Header · Sidebar
  ui/
    PullStringSwitch → tactile light/dark mode toggle
    Skeleton         → loading states
    ThemeProvider    → dark mode context
    SmoothScroll     → locomotive-style smooth scrolling
```

---

## Project Structure

```text
Code-Archaeologist/
├── README.md
├── PROJECT_SPEC.md
├── .gitignore
│
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── api.py              # FastAPI endpoints + CORS
│   │   ├── classifier.py       # Query router: historical/repository/general/hybrid
│   │   ├── graphrag.py         # GraphRAGEngine — orchestrates retrieval & synthesis
│   │   ├── retrieval.py        # Differentiated Neo4j retrieval strategies
│   │   ├── answer.py           # LLM synthesis — 4 category-tailored prompts
│   │   ├── providers.py        # OpenAI-compatible LLM with Gemini failover
│   │   ├── repo_context.py     # Flask module catalogue & 7-step execution flow
│   │   ├── models.py           # Pydantic: AskRequest, AskResponse, Evidence, etc.
│   │   ├── config.py           # Settings & environment loader
│   │   ├── neo4j_client.py     # Neo4j Aura driver (READ routing, certifi TLS)
│   │   ├── neo4j_ingest.py     # Populates Neo4j from normalized data
│   │   ├── neo4j_schema.py     # Schema constraints & indexes
│   │   ├── github_client.py    # GitHub REST API wrapper
│   │   ├── github_ingest.py    # Ingests PRs, issues, discussions
│   │   ├── extract_decisions.py# LLM + rule-based decision extraction
│   │   ├── normalize.py        # Normalize raw ingested records
│   │   ├── enrich_golden.py    # Enrich golden evaluation set
│   │   ├── eval.py             # Automated evaluation pipeline
│   │   ├── smoke.py            # Smoke test checks
│   │   └── utils.py            # Shared helpers
│   ├── data/                   # Normalized records & golden decisions (gitignored)
│   └── tests/                  # Pytest test suite
│
├── frontend/
│   ├── package.json
│   ├── .env.example
│   ├── app/
│   │   ├── page.tsx            # Dashboard
│   │   ├── layout.tsx          # Root layout + font loading
│   │   ├── globals.css         # Design system tokens
│   │   ├── investigate/
│   │   │   └── page.tsx        # Investigation page
│   │   └── decisions/
│   │       └── page.tsx        # Decisions browser
│   ├── components/
│   │   ├── investigation/
│   │   │   ├── AnswerPanel.tsx  # Adaptive answer renderer (4 modes)
│   │   │   ├── SearchBar.tsx    # Query input + suggestions
│   │   │   ├── EvidenceCard.tsx # Evidence source display
│   │   │   └── GraphPath.tsx    # Neo4j graph path visualisation
│   │   ├── dashboard/
│   │   │   └── StatsCards.tsx   # Live repository stats
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   └── ui/
│   │       ├── PullStringSwitch.tsx  # Tactile light/dark toggle
│   │       ├── ThemeProvider.tsx     # Dark mode context
│   │       ├── SmoothScroll.tsx      # Smooth scrolling wrapper
│   │       ├── Skeleton.tsx          # Loading skeletons
│   │       ├── Badge.tsx
│   │       └── CommandPalette.tsx
│   ├── lib/
│   │   └── api.ts              # Typed API client
│   └── types/
│       └── api.ts              # TypeScript interfaces
│
└── docs/                       # Additional documentation
```

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Neo4j Aura** account (free tier works) — or a self-hosted Neo4j 5.x instance
- A **GitHub personal access token** (read-only scopes sufficient)
- An **OpenAI-compatible LLM endpoint** — e.g. Google Generative Language API (`gemini-2.0-flash`)

---

### 1. Clone & configure

```bash
git clone https://github.com/THEaanya09/Code-Archaeologist.git
cd Code-Archaeologist
```

---

### 2. Backend

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
# → Edit .env with your credentials (see Environment Variables below)
```

#### Run the API server

```bash
python3 -m uvicorn app.api:app --reload --port 8000
```

| URL | Purpose |
|-----|---------|
| `http://127.0.0.1:8000/` | API root |
| `http://127.0.0.1:8000/health` | Health check |
| `http://127.0.0.1:8000/docs` | Interactive Swagger UI |

---

### 3. Frontend

```bash
cd frontend

npm install

cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://127.0.0.1:8000  (default)

npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)**.

---

## Environment Variables

### `backend/.env`

```env
# GitHub
GITHUB_TOKEN=github_pat_...
GITHUB_REPO=pallets/flask

# Neo4j
NEO4J_URI=neo4j+s://<your-instance>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<your-password>

# LLM (OpenAI-compatible)
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_API_KEY=<your-key>
LLM_MODEL=gemini-2.0-flash

# Optional: CORS origins (comma-separated)
# CORS_ORIGINS=http://localhost:3000
```

### `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

> **Security**: Never expose `LLM_API_KEY`, `NEO4J_PASSWORD`, or `GITHUB_TOKEN` via `NEXT_PUBLIC_*` variables or commit `.env` files to Git.

---

## Backend Pipeline Commands

Run these from the `backend/` directory to populate the knowledge graph:

```bash
cd backend && source .venv/bin/activate

# Step 1 — Ingest GitHub data
python3 -m app.github_ingest       # Pull PRs, issues, discussions from GitHub
python3 -m app.normalize           # Normalize and deduplicate records

# Step 2 — Extract architectural decisions
python3 -m app.extract_decisions   # LLM + rule-based decision extraction

# Step 3 — Populate Neo4j knowledge graph
python3 -m app.neo4j_schema        # Create constraints & indexes
python3 -m app.neo4j_ingest        # Ingest nodes and relationships

# Optional — Evaluation & test suite
python3 -m app.eval                # Run automated evaluation benchmark (classifier + retrieval)
python3 -m app.smoke               # Live smoke checks (known decision vs unsupported DB switch)
pytest                             # Run backend test suite (28 passing tests)
```

The test suite consists of **28 passing tests** across 8 dedicated test modules:
- **`tests/test_sarvam_provider.py` (1 test)**: Sarvam AI API client, `api-subscription-key` header verification, payload formatting, conversation history handling, and token usage parsing.
- **`tests/test_chat_service.py` (5 tests)**: Dual-mode routing (General AI vs Repository Analysis vs Auto), session state isolation, rate limiting enforcement, and session clearing.
- **`tests/test_api_contract.py` (5 tests)**: REST endpoint registration including `/chat` and session routes, gated `/golden-questions` access, `AskResponse` and `ChatResponse` schema validation, and session cleanup contracts.
- **`tests/test_classifier.py` (6 tests)**: Single-signal routing for all categories, multi-signal / ambiguous queries, real overlapping examples, and deterministic tie-breaking.
- **`tests/test_grounding.py` (5 tests)**: Fabricated evidence rejection, partial evidence confidence downgrade, verbatim evidence retention, uncited/wrongly-cited claim stripping, and deterministic confidence computation.
- **`tests/test_config.py` (2 tests)**: `Settings` dataclass properties and golden question dataset structure validation.
- **`tests/test_utils.py` (3 tests)**: Deduplication utilities and robust JSON serialization.
- **`tests/test_models.py` (1 test)**: Pydantic model roundtrips and evidence serialization.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health, Neo4j connection status, LLM status, Sarvam config status |
| `GET` | `/stats` | Decision counts, confidence distribution, contributor stats |
| `POST` | `/chat` | **Conversational AI endpoint**: Multi-turn chat with mode selection (`auto`, `repository`, `general`), session memory, token tracking, and GraphRAG grounding |
| `GET` | `/chat/session/{id}` | Inspect conversation session status, token usage, and remaining request quota |
| `DELETE` | `/chat/session/{id}` | Clear conversation session history |
| `POST` | `/ask` | Ask any single question; returns category-routed answer + evidence (backward compatible) |
| `GET` | `/decisions` | Paginated decision list (filter by confidence, source type) |
| `GET` | `/decision/{id}` | Full decision record by ID |
| `GET` | `/golden-questions` | Curated benchmark questions (gated by default behind `EXPOSE_GOLDEN_QUESTIONS` to prevent evaluation data leakage) |

### `POST /chat` (Conversational AI)

**Request**
```json
{
  "question": "Why did Flask separate ApplicationContext from RequestContext in 0.9?",
  "mode": "auto",
  "session_id": "session_abc123"
}
```

**Response**
```json
{
  "answer": "Flask separated ApplicationContext from RequestContext in version 0.9 to decouple application-level configuration and teardown callbacks from HTTP request processing...",
  "mode_used": "repository",
  "category": "historical",
  "confidence": "high",
  "sources": ["https://github.com/pallets/flask/commit/..."],
  "evidence": [
    {
      "decision_id": "DEC-004",
      "summary": "Split ApplicationContext from RequestContext",
      "rationale": "Allows CLI scripts and tests to run within app context without mocking HTTP requests."
    }
  ],
  "usage": {
    "prompt_tokens": 128,
    "completion_tokens": 256,
    "total_tokens": 384
  },
  "remaining_requests": 19,
  "session_id": "session_abc123",
  "cached": false
}
```

### `POST /ask`

**Request**
```json
{
  "question": "Why was request.json deprecated?",
  "top_k": 5
}
```

**Response** (abbreviated)
```json
{
  "answer": "...",
  "confidence": "medium",
  "category": "historical",
  "overview": null,
  "concept": null,
  "how_it_works": null,
  "in_repository": null,
  "architecture_flow": [],
  "key_modules": [],
  "relevant_files": ["flask/json/__init__.py", "flask/json/tag.py"],
  "sources": ["https://github.com/pallets/flask/issues/..."],
  "evidence": [{ "decision_id": "...", "summary": "...", "rationale": "..." }],
  "people": ["Armin Ronacher"],
  "dates": ["2022-03-14"],
  "graph_path": [{ "label": "Decision", "key": "..." }],
  "mode": "llm"
}
```

The `category` field drives the frontend's adaptive rendering:
- `historical` → evidence-first investigation layout
- `repository` → architecture stepper + module grid
- `general` → concept card + *Inside pallets/flask* section
- `hybrid` → combined architecture + rationale

---

## Query Routing & Evaluation

Query routing runs via deterministic pattern scoring in [`app/classifier.py`](backend/app/classifier.py) without requiring an additional LLM call.

### Signal Scoring & Tie-Break Rules

| Category | Matched Signal Patterns | Weight |
|---|---|---|
| `historical` | `why`, `why did`, `why does`, `why was`, `why were` | 3 |
| | `reason`, `rationale`, `motivation`, `tradeoff`, `decision` | 2 |
| | `deprecat*`, `removed`, `dropped`, `migrated`, `origin`, `history` | 2 |
| | `who merged`, `when did`, `when was`, `merged at`, `maintainers` | 2 |
| | `pull request`, `pr`, `commit`, `issue`, `changelog`, `fix`, `#<digits>` | 2 |
| | `instead of`, `rather than`, `revert` | 1 |
| `repository` | `architecture`, `structure`, `lifecycle`, `request lifecycle` | 3 |
| | `modules`, `major modules`, `file structure`, `directory structure`, `codebase` | 2 |
| | `workflow`, `pipeline`, `entry point`, `wsgi`, `blueprint`, `dispatch`, `routing` | 2 |
| | `how does ... work`, `how is ... implemented`, `how do ... communicate` | 2 |
| | `where is ... (handled\|defined\|located\|called)` | 2 |
| | `what happens when a request enters` | 3 |
| | `in flask`, `in this repo`, `in pallets/flask` | 1 |
| `general` | `^what is`, `^what are`, `^define`, `^meaning of` (definition prefix) | 3 |
| | `difference between`, `concept of`, `explain the concept` | 2 |

**Tie-Break Rules:**
- If historical and repository scores are positive and tied (`score_hist == score_repo`), **`hybrid` wins the tie-break**.
- If both historical and repository are strongly present (`score_hist >= 3` and `score_repo >= 3`), **`hybrid`** is selected to activate dual retrieval.
- Incidental code tokens in historical questions (e.g. `wsgi_app` in *"Why did Flask move ctx.push() inside try block in wsgi_app?"*) are dominated by multiple historical tokens (score 8 vs 2).

### Real Evaluation Benchmark Results

Computed from the evaluation suite (`python3 -m app.eval`):

- **Query Classifier Benchmark:** **97.8% Accuracy** (44/45 correct across `data/benchmark_questions.json`)
- **Retrieval Match Rate:** **100.0%** (25/25 verified hits on curated ground-truth URLs in `data/golden_questions.json`)

#### Real Confusion Matrix (Rows: Expected, Columns: Predicted)

| Expected \ Predicted | `historical` | `repository` | `general` | `hybrid` | Total | Class Recall |
|---|---|---|---|---|---|---|
| **`historical`** | 25 | 0 | 0 | 0 | 25 | 100.0% |
| **`repository`** | 0 | 10 | 0 | 0 | 10 | 100.0% |
| **`general`** | 0 | 0 | 5 | 0 | 5 | 100.0% |
| **`hybrid`** | 0 | 1 | 0 | 4 | 5 | 80.0% |

*Multi-signal analysis:* Out of 45 benchmark queries, 14 contained signals spanning multiple categories simultaneously. In 13 of 14 cases, the scoring hierarchy and tie-break rules produced the intended routing. In 1 case (ID 44: *"Rationale for blueprint routing architecture"*), repository tokens (score 5) dominated the rationale token (score 2), routing to `repository`.

---

## Limitations

1. **Repository Scope**: Ingested and verified against `pallets/flask` (25 curated golden decisions + sample recent PRs and issues). It is not a full 14-year commit crawl of the entire repository history.
2. **Model Dependency**: Decision extraction and answer generation depend on the configured LLM. While ground-truth facts and citations are verified, output wording is not bit-for-bit reproducible across model versions. Pinned model identifiers prevent silent drift.
3. **Deterministic Heuristic Confidence**: Confidence is an algorithmic score derived from evidence presence, retrieval ranks, and citation verification ratios, not a calibrated Bayesian statistical probability.
4. **Active Verification Status**: The active, fully validated pipeline utilizes Cypher graph queries in Neo4j Aura + BM25/lexical retrieval + Gemini/OpenAI-compatible LLM synthesis. Dense vector embedding similarity search is implemented in `retrieval.py` but is optional and requires a locally configured embeddings endpoint.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend framework** | FastAPI + Uvicorn |
| **Knowledge graph** | Neo4j Aura (bolt+TLS) |
| **Active LLM** | Google Gemini 2.0 Flash (`gemini-2.0-flash`) via OpenAI-compatible endpoint |
| **Pinned LLM failover** | Explicit version cascade: `gemini-2.0-flash` → `gemini-2.5-flash` → `gemini-1.5-flash` → `gemini-3.5-flash` *(no unpinned `-latest` aliases)* |
| **GitHub ingestion** | PyGithub + GitHub REST API |
| **Data validation** | Pydantic v2 |
| **Frontend framework** | Next.js 15 (App Router) + TypeScript |
| **UI presentation** | Framer Motion · Vanilla CSS design tokens (no Tailwind) |
| **Typography** | Merriweather (serif) · Inter (sans) · JetBrains Mono |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-improvement`
3. Run `pytest` in `backend/` (20 tests) and verify `npx tsc --noEmit` in `frontend/` before pushing
4. Open a pull request against `main`

---

*Built with ❤️ by [THEaanya09](https://github.com/THEaanya09) and [akshitsharma07](https://github.com/akshitsharma07)*
