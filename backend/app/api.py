"""FastAPI HTTP API for CodeArchaeologist."""
from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import AskRequest, AskResponse
from app.graphrag import GraphRAGEngine

settings = get_settings()

app = FastAPI(title="CodeArchaeologist", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins) if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = GraphRAGEngine()


@app.get("/")
def root():
    return {"service": "CodeArchaeologist", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "neo4j": engine.neo4j is not None, "llm": engine.llm is not None}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        return engine.ask(request.question, request.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/ingest")
def ingest_endpoint():
    from app.github_ingest import ingest_golden
    ingest_golden()
    return {"status": "ok"}


@app.post("/extract")
def extract_endpoint():
    from app.extract_decisions import extract
    extract()
    return {"status": "ok"}


@app.get("/decision/{decision_id}")
def decision(decision_id: str):
    if engine.neo4j is not None:
        rows = engine.neo4j.run(
            "MATCH (d:Decision {id:$id}) RETURN d",
            id=decision_id,
        )
        if rows:
            return rows[0]["d"]

    from app.config import PROCESSED_DIR
    from app.utils import read_json
    path = PROCESSED_DIR / "extracted_decisions.json"
    if path.exists():
        for row in read_json(path):
            if row["id"] == decision_id:
                return row

    raise HTTPException(status_code=404, detail="Decision not found")


@app.get("/decisions")
def list_decisions(
    confidence: Optional[str] = Query(None, description="Filter by confidence: high, medium, low"),
    source_type: Optional[str] = Query(None, description="Filter by source_type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List all extracted decisions with optional filtering."""
    from app.config import PROCESSED_DIR
    from app.utils import read_json

    all_decisions = []

    # Try Neo4j first
    if engine.neo4j is not None:
        try:
            rows = engine.neo4j.run(
                """
                MATCH (d:Decision)
                RETURN d.id AS id, d.summary AS summary, d.rationale AS rationale,
                       d.tradeoffs AS tradeoffs, d.confidence AS confidence,
                       d.source_type AS source_type, d.source_id AS source_id,
                       d.source_url AS source_url, d.evidence_snippet AS evidence_snippet,
                       d.person_login AS person_login, d.decision_date AS decision_date
                ORDER BY d.id
                """
            )
            for row in rows:
                all_decisions.append({
                    "id": row["id"],
                    "summary": row["summary"],
                    "rationale": row["rationale"],
                    "tradeoffs": row.get("tradeoffs", ""),
                    "confidence": row.get("confidence", "low"),
                    "source_type": row.get("source_type", "unknown"),
                    "source_id": row.get("source_id"),
                    "source_url": row.get("source_url"),
                    "evidence_snippet": row.get("evidence_snippet"),
                    "people": [row["person_login"]] if row.get("person_login") else [],
                    "dates": [row["decision_date"]] if row.get("decision_date") else [],
                })
        except Exception:
            all_decisions = []

    # Fallback to local JSON
    if not all_decisions:
        path = PROCESSED_DIR / "extracted_decisions.json"
        if path.exists():
            all_decisions = read_json(path)

    # Apply filters
    if confidence:
        all_decisions = [d for d in all_decisions if d.get("confidence") == confidence]
    if source_type:
        all_decisions = [d for d in all_decisions if d.get("source_type") == source_type]

    total = len(all_decisions)
    paginated = all_decisions[offset : offset + limit]

    return {"total": total, "offset": offset, "limit": limit, "decisions": paginated}


@app.get("/stats")
def stats():
    """Return system-level stats for the dashboard."""
    from app.config import PROCESSED_DIR, GOLDEN_FILE
    from app.utils import read_json

    decision_count = 0
    confidence_counts = {"high": 0, "medium": 0, "low": 0}
    source_type_counts = {}
    people_set = set()

    path = PROCESSED_DIR / "extracted_decisions.json"
    if path.exists():
        decisions = read_json(path)
        decision_count = len(decisions)
        for d in decisions:
            conf = d.get("confidence", "low")
            confidence_counts[conf] = confidence_counts.get(conf, 0) + 1
            st = d.get("source_type", "unknown")
            source_type_counts[st] = source_type_counts.get(st, 0) + 1
            for p in d.get("people", []):
                people_set.add(p)

    golden_count = 0
    if GOLDEN_FILE.exists():
        golden_count = len(read_json(GOLDEN_FILE))

    return {
        "decision_count": decision_count,
        "golden_question_count": golden_count,
        "contributor_count": len(people_set),
        "confidence_distribution": confidence_counts,
        "source_type_distribution": source_type_counts,
        "neo4j_connected": engine.neo4j is not None,
        "llm_connected": engine.llm is not None,
        "repo": "pallets/flask",
    }


@app.get("/golden-questions")
def golden_questions():
    """Return sample golden questions for the UI."""
    from app.config import GOLDEN_FILE
    from app.utils import read_json

    if not GOLDEN_FILE.exists():
        return {"questions": []}

    data = read_json(GOLDEN_FILE)
    return {
        "questions": [
            {
                "id": item["id"],
                "question": item["question"],
                "confidence": item.get("confidence", "low"),
                "source_type": "github_pr" if item.get("pr") else ("github_issue" if item.get("issue") else "github_commit"),
            }
            for item in data
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)

