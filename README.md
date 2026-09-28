# CodeArchaeologist

**Answer the question code cannot answer: why is it like this?**

CodeArchaeologist reconstructs historical software decisions from GitHub discussions using an evidence-first retrieval pipeline, GraphRAG, and Neo4j knowledge graphs.

Target repository: `pallets/flask`

---

## Architecture & Project Structure

The project is cleanly decoupled into two top-level components:

```text
Code-Archaeologist/
├── frontend/               # Next.js 16 (App Router) + TypeScript + Tailwind CSS
│   ├── app/                # App router pages (Dashboard, Investigate, Decisions)
│   ├── components/         # UI & domain components (AnswerPanel, EvidenceCard, GraphPath, etc.)
│   ├── lib/                # Typed API client (apiFetch, askQuestion, getDecisions, etc.)
│   ├── types/              # TypeScript interfaces matching backend models
│   ├── .env.example        # NEXT_PUBLIC_API_URL template
│   └── package.json
│
├── backend/                # FastAPI + AI + GraphRAG + Neo4j
│   ├── app/                # Core Python application
│   │   ├── api.py          # FastAPI endpoints with CORS middleware
│   │   ├── config.py       # Dataclass settings & environment loader
│   │   ├── graphrag.py     # GraphRAG query engine
│   │   ├── retrieval.py    # Evidence-first retrieval
│   │   ├── extract_decisions.py # LLM & rule-based decision extraction
│   │   ├── github_ingest.py     # GitHub discussion ingestion
│   │   ├── neo4j_ingest.py      # Neo4j graph population
│   │   ├── neo4j_schema.py      # Neo4j constraints & schema setup
│   │   └── models.py       # Pydantic schemas
│   ├── data/               # Normalized records & golden decisions
│   ├── tests/              # Pytest test suite
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Backend secrets template
│   └── verify_build.py     # Syntax verification script
│
├── README.md
└── .gitignore
```

---

## Quick Start

### 1. Backend Setup

From the project root:

```bash
cd backend

# Create and activate virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to add your GITHUB_TOKEN, NEO4J_*, and LLM credentials (if available)
```

#### Run the FastAPI Backend

```bash
# Option A: Direct Python module execution
python3 -m app.api

# Option B: Uvicorn with auto-reload
python3 -m uvicorn app.api:app --reload --port 8000
```

FastAPI will be available at:
- **API Root**: `http://127.0.0.1:8000/`
- **Health Check**: `http://127.0.0.1:8000/health`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

---

### 2. Frontend Setup

In a separate terminal:

```bash
cd frontend

# Install Node dependencies
npm install

# Configure environment
cp .env.example .env.local
# NEXT_PUBLIC_API_URL defaults to http://127.0.0.1:8000

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Backend Pipeline Commands

All backend data operations are run from the `backend/` directory:

```bash
cd backend

# 1. Ingest GitHub discussions & normalize data
python3 -m app.github_ingest
python3 -m app.normalize

# 2. Extract architectural decisions
python3 -m app.extract_decisions

# 3. Setup Neo4j schema & ingest nodes/relationships (requires Neo4j running)
python3 -m app.neo4j_schema
python3 -m app.neo4j_ingest

# 4. Run automated evaluation
python3 -m app.eval

# 5. Run smoke checks
python3 -m app.smoke

# 6. Run test suite
pytest tests/
```

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health, Neo4j connection, LLM status |
| `GET` | `/stats` | Decision counts, confidence distribution, contributor stats |
| `POST` | `/ask` | Ask architectural questions; returns answer, evidence, and graph traversal |
| `GET` | `/decisions` | Filterable list of decisions (by confidence, source type, pagination) |
| `GET` | `/decision/{id}` | Detailed decision record by ID |
| `GET` | `/golden-questions` | Curated golden evaluation questions for quick investigation |

---

## Environment Separation & Security

- **Backend (`backend/.env`)**: Contains sensitive server secrets including `GITHUB_TOKEN`, `NEO4J_PASSWORD`, `LLM_API_KEY`, and `CORS_ORIGINS`. Never committed to Git.
- **Frontend (`frontend/.env.local`)**: Contains client-safe configuration (`NEXT_PUBLIC_API_URL`). Never expose backend tokens or credentials through `NEXT_PUBLIC_*`.
