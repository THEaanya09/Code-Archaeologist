"""FastAPI HTTP API for CodeArchaeologist."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import AskRequest, AskResponse
from app.graphrag import GraphRAGEngine

app = FastAPI(title="CodeArchaeologist", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
