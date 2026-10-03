# CodeArchaeologist

> **Understand any codebase — not just why, but what, how, where, and who. Now with conversational AI.**

CodeArchaeologist is a **repository intelligence platform** built on FastAPI, GraphRAG, Neo4j, and Sarvam AI. It ingests a GitHub repository's full history — commits, pull requests, issues, discussions, and architectural decisions — into a knowledge graph, and offers two ways to explore it:

- **Investigate Mode** — ask a single structured question; get a category-routed, evidence-grounded answer with a rich adaptive UI.
- **Chat Mode** — hold a multi-turn conversation with AI, switching between general programming Q&A and deep repository analysis.

Target repository: **`pallets/flask`** (configurable via `.env`).

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Backend Pipeline Commands](#backend-pipeline-commands)
- [API Reference](#api-reference)
- [Query Routing & Evaluation](#query-routing--evaluation)
- [Test Suite](#test-suite)
- [Limitations](#limitations)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)

---

## Features

### 🔍 Investigate Mode
Question routing across four answer categories with adaptive UI:

| Mode | Example Question |
|------|------------------|
| 📜 **Historical · Why** | *"Why was `request.json` deprecated?"* |
| 🏛 **Repository · Architecture** | *"What is the architecture of Flask?"* |
| 💡 **General · Concepts** | *"What is WSGI?"* |
| 🔀 **Hybrid** | *"Why does Flask use WSGI and how is it implemented here?"* |

Answers adapt their layout to the question type:
- **Historical** → Evidence trail · Contributors · Timeline · Related code
- **Repository** → Architecture overview · Execution flow stepper · Module grid · Key files
- **General** → Concept definition · How it works · *Inside pallets/flask* grounded section
- **Hybrid** → Architecture context combined with historical decision rationale

### 💬 Chat Mode
A full conversational interface backed by Sarvam AI:
- **Three routing modes**: `general` (direct LLM Q&A), `repository` (GraphRAG-grounded answers), `auto` (heuristic routing via the existing classifier)
- **Multi-turn session memory** — conversation history is preserved per session
- **Response caching** — identical questions return instantly (LRU cache, 100 entries)
- **Rate limiting** — 20 requests/session/24h (configurable)
- **Markdown rendering** with code blocks in the chat UI
- **Evidence drawer** — click any source to inspect raw evidence from the repository
- **Suggestion chips** — contextual follow-up prompts after every answer

### 🛡️ Anti-Hallucination Grounding
1. **Verbatim snippet verification** — every evidence snippet is verified against the underlying source text; unverifiable snippets are discarded.
2. **Mandatory claim citations** — the LLM is required to cite a specific `evidence_id` for every factual claim; uncited claims are stripped programmatically.
3. **Deterministic confidence** — confidence is computed algorithmically from evidence scores and citation ratios, never self-reported by the LLM.
4. **Zero-evidence guard** — if retrieval finds nothing, the system bypasses the LLM and returns a `"no_evidence"` refusal.

---

## How It Works

```
User question
      │
      ▼
┌─────────────────┐
│ Query Classifier │  ── deterministic heuristics ──▶  historical / repository / general / hybrid
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

---

## Architecture

### Backend (FastAPI · Python)

```
Request
  → api.py (FastAPI, CORS, v0.2.0)
      → /ask  → graphrag.py (GraphRAGEngine)
      │             → classifier.py   (classify: historical/repository/general/hybrid)
      │             → retrieval.py    (Retriever — differentiated Neo4j + vector search)
      │                 → neo4j_client.py  (Aura connection, READ routing, certifi TLS)
      │                 → repo_context.py  (Flask module catalogue & execution flow)
      │             → answer.py       (LLM synthesis — 4 specialised system prompts)
      │                 → providers.py    (SarvamLLM · OpenAICompatibleLLM + Gemini failover)
      │             → models.py       (Pydantic AskResponse — 16 fields)
      │
      → /chat → chat_service.py (ChatService)
                    → route_question()     (general | repository | auto)
                    → _handle_general()    (SarvamLLM + conversation history)
                    → _handle_repository() (GraphRAG + optional Sarvam enhancement)
                    → RateLimiter          (in-memory, per-session, 24h window)
                    → ChatSession          (message history, token tracking)
  ← AskResponse / ChatResponse JSON
```

### Frontend (Next.js 15 · TypeScript)

```
app/
  page.tsx            → Dashboard (stats, recent decisions)
  investigate/        → Investigation page (search + adaptive answer UI)
    page.tsx          → Mode toggle: Investigate ↔ Chat · query input · answer panel
  chat/               → Dedicated chat page
    page.tsx          → Full-page chat interface
  decisions/          → Decisions browser

components/
  chat/
    ChatInterface.tsx  → Conversational UI: message list, input, mode selector,
                         suggestion chips, evidence drawer, markdown rendering
  investigation/
    SearchBar          → Query input with golden-question suggestions
    AnswerPanel        → Adaptive renderer (4 modes)
    EvidenceCard       → Per-source evidence display
    GraphPath          → Neo4j graph traversal visualisation
  dashboard/
    StatsCards         → Live repository stats
  layout/
    Header · Sidebar
  ui/
    PullStringSwitch   → Tactile light/dark mode toggle
    Skeleton           → Loading states
    ThemeProvider      → Dark mode context
    SmoothScroll       → Locomotive-style smooth scrolling
                         (disabled on /chat to prevent scroll conflict)
    Badge · CommandPalette
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
│   │   ├── api.py               # FastAPI endpoints + CORS (v0.2.0)
│   │   ├── chat_service.py      # ChatService: sessions, routing, rate limiting
│   │   ├── classifier.py        # Query router: historical/repository/general/hybrid
│   │   ├── graphrag.py          # GraphRAGEngine — orchestrates retrieval & synthesis
│   │   ├── retrieval.py         # Differentiated Neo4j retrieval strategies
│   │   ├── answer.py            # LLM synthesis — 4 category-tailored prompts
│   │   ├── providers.py         # SarvamLLM · OpenAI-compatible LLM with Gemini failover
│   │   ├── grounding.py         # Evidence verification & anti-hallucination gates
│   │   ├── repo_context.py      # Flask module catalogue & 7-step execution flow
│   │   ├── models.py            # Pydantic: AskRequest, AskResponse, ChatRequest, ChatResponse
│   │   ├── config.py            # Settings & environment loader
│   │   ├── neo4j_client.py      # Neo4j Aura driver (READ routing, certifi TLS)
│   │   ├── neo4j_ingest.py      # Populates Neo4j from normalized data
│   │   ├── neo4j_schema.py      # Schema constraints & indexes
│   │   ├── github_client.py     # GitHub REST API wrapper
│   │   ├── github_ingest.py     # Ingests PRs, issues, discussions
│   │   ├── extract_decisions.py # LLM + rule-based decision extraction
│   │   ├── normalize.py         # Normalize raw ingested records
│   │   ├── enrich_golden.py     # Enrich golden evaluation set
│   │   ├── eval.py              # Automated evaluation pipeline
│   │   ├── smoke.py             # Smoke test checks
│   │   └── utils.py             # Shared helpers
│   ├── data/
│   │   ├── benchmark_questions.json   # 45-question evaluation benchmark
│   │   └── processed/                 # Normalized records & golden decisions
│   └── tests/                         # Pytest test suite (28 passing tests)
│       ├── test_sarvam_provider.py
│       ├── test_chat_service.py
│       ├── test_api_contract.py
│       ├── test_classifier.py
│       ├── test_grounding.py
│       ├── test_config.py
│       ├── test_utils.py
│       └── test_models.py
│
├── frontend/
│   ├── package.json
│   ├── .env.example
│   ├── app/
│   │   ├── page.tsx             # Dashboard
│   │   ├── layout.tsx           # Root layout + font loading
│   │   ├── globals.css          # Design system tokens
│   │   ├── investigate/
│   │   │   └── page.tsx         # Investigation + inline Chat page
│   │   ├── chat/
│   │   │   └── page.tsx         # Dedicated full-page chat interface
│   │   └── decisions/
│   │       └── page.tsx         # Decisions browser
│   ├── components/
│   │   ├── chat/
│   │   │   └── ChatInterface.tsx  # Full conversational UI component
│   │   ├── investigation/
│   │   │   ├── AnswerPanel.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── EvidenceCard.tsx
│   │   │   └── GraphPath.tsx
│   │   ├── dashboard/
│   │   │   └── StatsCards.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   └── ui/
│   │       ├── PullStringSwitch.tsx
│   │       ├── ThemeProvider.tsx
│   │       ├── SmoothScroll.tsx
│   │       ├── Skeleton.tsx
│   │       ├── Badge.tsx
│   │       └── CommandPalette.tsx
│   ├── lib/
│   │   └── api.ts               # Typed API client (ask + chat endpoints)
│   └── types/
│       └── api.ts               # TypeScript interfaces
│
└── docs/                        # Additional documentation
    ├── architecture.md
    └── evaluation.md
```

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Neo4j Aura** account (free tier works) — or a self-hosted Neo4j 5.x instance
- A **GitHub personal access token** (read-only scopes sufficient)
- A **Sarvam AI API key** — for the chat and general Q&A endpoints
- An **OpenAI-compatible LLM endpoint** — e.g. Google Generative Language API (`gemini-2.0-flash`) for the investigate pipeline

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
| `http://127.0.0.1:8000/health` | Health check (Neo4j · LLM · Sarvam status) |
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

# LLM — Investigate pipeline (OpenAI-compatible)
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_API_KEY=<your-gemini-key>
LLM_MODEL=gemini-2.0-flash

# Sarvam AI — Chat & general Q&A
SARVAM_API_KEY=<your-sarvam-key>
SARVAM_BASE_URL=https://api.sarvam.ai/v1
SARVAM_MODEL=sarvam-2

# Chat service tuning (optional)
DAILY_REQUEST_LIMIT=20
MAX_HISTORY_MESSAGES=10
MAX_RETRIEVED_CHUNKS=5

# Evaluation gate
EXPOSE_GOLDEN_QUESTIONS=false

# Optional: CORS origins (comma-separated)
# CORS_ORIGINS=http://localhost:3000
```

### `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

> **Security**: Never expose `LLM_API_KEY`, `SARVAM_API_KEY`, `NEO4J_PASSWORD`, or `GITHUB_TOKEN` via `NEXT_PUBLIC_*` variables or commit `.env` files to Git.

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

# Evaluation & test suite
python3 -m app.eval                # Run automated evaluation benchmark
python3 -m app.smoke               # Live smoke checks
pytest                             # Run backend test suite (28 passing tests)
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health — Neo4j, LLM, and Sarvam AI configuration status |
| `GET` | `/stats` | Decision counts, confidence distribution, contributor stats |
| `POST` | `/ask` | Single-question investigate endpoint; returns category-routed structured answer |
| `POST` | `/chat` | **Conversational AI** — multi-turn chat with `auto`/`general`/`repository` mode |
| `GET` | `/chat/session/{id}` | Session status, token usage, and remaining request quota |
| `DELETE` | `/chat/session/{id}` | Clear conversation session history |
| `GET` | `/decisions` | Paginated decision list (filter by confidence, source type) |
| `GET` | `/decision/{id}` | Full decision record by ID |
| `GET` | `/golden-questions` | Curated benchmark questions (gated behind `EXPOSE_GOLDEN_QUESTIONS`) |

---

### `POST /chat`

**Request**
```json
{
  "question": "Why did Flask separate ApplicationContext from RequestContext in 0.9?",
  "mode": "auto",
  "session_id": "session_abc123"
}
```

**Modes**

| Value | Behaviour |
|-------|-----------|
| `auto` | Heuristic routing via the classifier (no extra LLM call) |
| `general` | Direct Sarvam AI Q&A for programming/technology questions |
| `repository` | GraphRAG-powered evidence-grounded answer for repo-specific questions |

**Response**
```json
{
  "answer": "Flask separated ApplicationContext from RequestContext in version 0.9...",
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

---

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
  "relevant_files": ["flask/json/__init__.py"],
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

Query routing runs via deterministic pattern scoring in `app/classifier.py` — no additional LLM call required.

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
| | `where is ... (handled/defined/located/called)` | 2 |
| | `what happens when a request enters` | 3 |
| | `in flask`, `in this repo`, `in pallets/flask` | 1 |
| `general` | `^what is`, `^what are`, `^define`, `^meaning of` (definition prefix) | 3 |
| | `difference between`, `concept of`, `explain the concept` | 2 |

**Tie-Break Rules:**
- If historical and repository scores are positive and tied, **`hybrid`** wins.
- If both are strongly present (`>= 3` each), **`hybrid`** is selected to activate dual retrieval.

### Evaluation Benchmark Results

| Benchmark | Result |
|-----------|--------|
| **Query Classifier** | **97.8% accuracy** (44/45 correct on `benchmark_questions.json`) |
| **Retrieval Match Rate** | **100.0%** (25/25 verified hits on golden ground-truth URLs) |

#### Confusion Matrix (Rows: Expected, Columns: Predicted)

| Expected \ Predicted | `historical` | `repository` | `general` | `hybrid` | Total | Recall |
|---|---|---|---|---|---|---|
| **`historical`** | 25 | 0 | 0 | 0 | 25 | 100.0% |
| **`repository`** | 0 | 10 | 0 | 0 | 10 | 100.0% |
| **`general`** | 0 | 0 | 5 | 0 | 5 | 100.0% |
| **`hybrid`** | 0 | 1 | 0 | 4 | 5 | 80.0% |

---

## Test Suite

**28 passing tests** across 8 dedicated test modules:

| Module | Tests | Coverage |
|--------|-------|---------|
| `test_sarvam_provider.py` | 1 | Sarvam AI API client, `api-subscription-key` header, payload formatting, conversation history, token usage |
| `test_chat_service.py` | 5 | Mode routing (general/repository/auto), session isolation, rate limiting, session clearing |
| `test_api_contract.py` | 5 | REST endpoint registration, `/chat` + session routes, `AskResponse`/`ChatResponse` schema, session cleanup |
| `test_classifier.py` | 6 | Single-signal routing for all categories, multi-signal/ambiguous queries, deterministic tie-breaking |
| `test_grounding.py` | 5 | Fabricated evidence rejection, partial confidence downgrade, verbatim retention, uncited claim stripping, deterministic confidence |
| `test_config.py` | 2 | `Settings` dataclass properties, golden question dataset structure |
| `test_utils.py` | 3 | Deduplication utilities, robust JSON serialization |
| `test_models.py` | 1 | Pydantic model roundtrips, evidence serialization |

Run the suite:
```bash
cd backend && pytest
```

---

## Limitations

1. **Repository Scope**: Ingested and verified against `pallets/flask` (25 curated golden decisions + sample recent PRs and issues). Not a full 14-year commit crawl.
2. **In-Memory Sessions**: Chat sessions do not persist across server restarts. For production, replace `RateLimiter` and `ChatSession` stores with Redis.
3. **Rate Limiting**: Per-process and single-instance. Horizontal scaling requires a shared backing store.
4. **Model Dependency**: Decision extraction and answer generation depend on the configured LLM. Output wording is not bit-for-bit reproducible across model versions.
5. **Vector Search**: Dense vector embedding similarity search is implemented in `retrieval.py` but is optional — it requires a locally configured embeddings endpoint.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend framework** | FastAPI + Uvicorn |
| **Knowledge graph** | Neo4j Aura (bolt+TLS) |
| **Chat & General AI** | Sarvam AI (`sarvam-2`) via `api-subscription-key` auth |
| **Investigate LLM** | Google Gemini 2.0 Flash via OpenAI-compatible endpoint |
| **LLM failover** | `gemini-2.0-flash` → `gemini-2.5-flash` → `gemini-1.5-flash` (no unpinned `-latest` aliases) |
| **GitHub ingestion** | PyGithub + GitHub REST API |
| **Data validation** | Pydantic v2 |
| **Frontend framework** | Next.js 15 (App Router) + TypeScript |
| **UI presentation** | Framer Motion · Vanilla CSS design tokens (no Tailwind) |
| **Typography** | Merriweather (serif) · Inter (sans) · JetBrains Mono |
| **Smooth scrolling** | Lenis (disabled on `/chat` to prevent scroll conflicts) |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-improvement`
3. Run `pytest` in `backend/` (28 tests) and verify `npx tsc --noEmit` in `frontend/` before pushing
4. Open a pull request against `main`

---

*Built with ❤️ by [THEaanya09](https://github.com/THEaanya09) and [akshitsharma07](https://github.com/akshitsharma07)*
