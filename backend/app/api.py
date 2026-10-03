"""FastAPI HTTP API for CodeArchaeologist."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import AskRequest, AskResponse, ChatRequest, ChatResponse, Evidence
from app.graphrag import GraphRAGEngine
from app.chat_service import ChatService

logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(title="CodeArchaeologist", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins) if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = GraphRAGEngine()
chat_service = ChatService(engine)


@app.get("/")
def root():
    return {"service": "CodeArchaeologist", "version": "0.2.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "neo4j": engine.neo4j is not None,
        "llm": engine.llm is not None,
        "llm_provider": settings.llm_provider,
        "sarvam_configured": bool(settings.sarvam_api_key),
    }


# ── Existing Ask Endpoint (preserved for backward compatibility) ─────

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        return engine.ask(request.question, request.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ── Conversational Chat Endpoint ─────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Conversational AI endpoint supporting general and repository-specific questions.

    Modes:
    - general: Direct AI Q&A for programming/technology questions
    - repository: GraphRAG-powered evidence-grounded answers
    - auto: Lightweight heuristic routing (no extra LLM call)
    """
    try:
        result = chat_service.chat(
            question=request.question,
            mode=request.mode,
            session_id=request.session_id,
        )

        # Check for service-level errors
        if result.get("error"):
            return ChatResponse(
                answer="",
                mode_used=result.get("mode_used", request.mode),
                error=result["error"],
                remaining_requests=result.get("remaining_requests"),
                session_id=request.session_id,
            )

        # Build evidence list from raw dicts
        evidence_list = []
        for e in result.get("evidence", []):
            if isinstance(e, dict):
                try:
                    evidence_list.append(Evidence(**e))
                except Exception:
                    pass

        return ChatResponse(
            answer=result.get("answer", ""),
            mode_used=result.get("mode_used", "auto"),
            category=result.get("category"),
            confidence=result.get("confidence"),
            overview=result.get("overview"),
            sources=result.get("sources", []),
            evidence=evidence_list,
            people=result.get("people", []),
            dates=result.get("dates", []),
            graph_path=result.get("graph_path", []),
            relevant_files=result.get("relevant_files", []),
            architecture_flow=result.get("architecture_flow", []),
            key_modules=result.get("key_modules", []),
            usage=result.get("usage"),
            remaining_requests=result.get("remaining_requests"),
            session_id=result.get("session_id", request.session_id),
            cached=result.get("cached", False),
        )

    except Exception as exc:
        logger.error(f"Chat endpoint error: {exc}")
        # Don't expose internal errors
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question. Please try again.",
        ) from exc


@app.get("/chat/session/{session_id}")
def get_session(session_id: str):
    """Get session info and usage statistics."""
    return chat_service.get_session_info(session_id)


@app.delete("/chat/session/{session_id}")
def clear_session(session_id: str):
    """Clear conversation history for a session."""
    chat_service.clear_session(session_id)
    return {"status": "ok", "session_id": session_id, "cleared": True}


# ── Existing Endpoints (all preserved) ───────────────────────────────

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
        "llm_provider": settings.llm_provider,
        "sarvam_configured": bool(settings.sarvam_api_key),
        "repo": settings.github_repo,
    }


@app.get("/golden-questions")
def golden_questions():
    """Return sample golden questions for the UI, gated behind EXPOSE_GOLDEN_QUESTIONS to prevent eval contamination."""
    from app.config import GOLDEN_FILE, get_settings
    from app.utils import read_json

    settings = get_settings()
    if not settings.expose_golden_questions:
        return {
            "questions": [],
            "gated": True,
            "message": "Golden evaluation questions endpoint is gated to prevent benchmark memorization and data leakage. Set EXPOSE_GOLDEN_QUESTIONS=true in your environment to expose live.",
        }

    if not GOLDEN_FILE.exists():
        return {"questions": [], "gated": False}

    data = read_json(GOLDEN_FILE)
    return {
        "gated": False,
        "questions": [
            {
                "id": item["id"],
                "question": item["question"],
                "confidence": item.get("confidence", "low"),
                "source_type": "github_pr" if item.get("pr") else ("github_issue" if item.get("issue") else "github_commit"),
            }
            for item in data
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)


