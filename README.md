# CodeArchaeologist

**Answer the question code cannot answer: why is it like this?**

CodeArchaeologist reconstructs historical software decisions from GitHub discussions using a decision graph and evidence-first retrieval.

## Target repository

`pallets/flask`

## Quick start

### 1. Environment

Use the existing `.venv` and existing `.env`. Do not overwrite your real `.env`.

Install dependencies:

```powershell
pip install -r requirements.txt
```

### 2. GitHub ingestion

```powershell
python -m app.github_ingest
python -m app.normalize
```

This uses the existing golden question set to fetch only high-value issues/PRs/commits and caches responses under `data/raw/`.

### 3. Extract decisions

Without an LLM key, the 25 curated golden decisions are used as a clearly marked fallback.

With an LLM configured in `.env`, the system attempts structured extraction from the fetched GitHub discussions and falls back when the extraction is incomplete.

```powershell
python -m app.extract_decisions
```

### 4. Neo4j

Add `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD` to `.env`.

```powershell
python -m app.neo4j_schema
python -m app.neo4j_ingest
```

### 5. API

```powershell
python -m app.api
```

Open:

- API health: `http://127.0.0.1:8000/health`
- UI: `http://127.0.0.1:8000/ui/`
- Swagger: `http://127.0.0.1:8000/docs`

### 6. Evaluate

```powershell
python -m app.eval
```

## API example

```http
POST /ask
Content-Type: application/json

{"question":"Why did Flask 1.0 remove the deprecated flask.ext import namespace?"}
```

## Security

Never commit `.env`, tokens, passwords, or API keys. Use `.env.example` as the template.

## Limitations

The MVP is intentionally scoped to one repository. Full semantic vector search requires an embedding provider and Neo4j vector index configuration. Historical coverage depends on which GitHub discussions are ingested.
