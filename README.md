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
- [Query Routing](#query-routing)
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

**Trust rule**: Every repository-specific claim is grounded in indexed evidence. If sufficient evidence cannot be retrieved from Neo4j, the system says so rather than hallucinating files, commits, PR numbers, or architecture details.

---

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

# Optional — Evaluation & smoke tests
python3 -m app.eval                # Run automated evaluation benchmark
python3 -m app.smoke               # Quick smoke checks
pytest tests/                      # Full test suite
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health, Neo4j connection status, LLM status |
| `GET` | `/stats` | Decision counts, confidence distribution, contributor stats |
| `POST` | `/ask` | Ask any question; returns category-routed answer + evidence |
| `GET` | `/decisions` | Paginated decision list (filter by confidence, source type) |
| `GET` | `/decision/{id}` | Full decision record by ID |
| `GET` | `/golden-questions` | Curated evaluation questions for quick testing |

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

## Query Routing

The classifier uses deterministic heuristics (no extra LLM call):

| Signal | Routed to |
|--------|-----------|
| Starts with *why*, contains *deprecated*, *introduced*, *merged*, *removed* | `historical` |
| Contains *architecture*, *structure*, *lifecycle*, *routing*, *module*, *how does* | `repository` |
| Generic concept questions (*what is X*) with no repo-specific context | `general` |
| Combines why + how / architecture + historical rationale | `hybrid` |

The classifier was validated against 22 benchmark cases with 100% accuracy before deployment.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend framework** | FastAPI + Uvicorn |
| **Knowledge graph** | Neo4j Aura (bolt+TLS) |
| **LLM** | OpenAI-compatible endpoint (Google Gemini 2.0 Flash) |
| **LLM resilience** | Failover cascade: `gemini-2.0-flash` → `gemini-2.5-flash` → `gemini-flash-latest` |
| **GitHub ingestion** | PyGithub + GitHub REST API |
| **Data validation** | Pydantic v2 |
| **Frontend framework** | Next.js 15 (App Router) + TypeScript |
| **UI animations** | Framer Motion |
| **Design** | Vanilla CSS design tokens (no Tailwind) |
| **Fonts** | Merriweather (serif) · Inter (sans) · JetBrains Mono |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-improvement`
3. Run `pytest tests/` and verify `npx tsc --noEmit` passes before pushing
4. Open a pull request against `main`

---

*Built with ❤️ by [THEaanya09](https://github.com/THEaanya09) and [akshitsharma07](https://github.com/akshitsharma07)*
