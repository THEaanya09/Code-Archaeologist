"""Tests for API contract, routing endpoints, and gated access."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.api import app
from app.models import AskRequest, AskResponse


def test_api_routes_exist():
    """Verify all expected REST API endpoints are registered on the FastAPI app."""
    routes = {route.path for route in app.routes}  # type: ignore[attr-defined]
    assert "/health" in routes
    assert "/stats" in routes
    assert "/ask" in routes
    assert "/decisions" in routes
    assert "/golden-questions" in routes


def test_golden_questions_gated_by_default(monkeypatch):
    """Verify that GET /golden-questions returns gated response without data leakage when gated."""
    import dataclasses
    from app.config import get_settings
    
    current_settings = get_settings()
    mock_settings = dataclasses.replace(current_settings, expose_golden_questions=False)
    monkeypatch.setattr("app.config.get_settings", lambda: mock_settings)

    client = TestClient(app)
    resp = client.get("/golden-questions")
    assert resp.status_code == 200
    payload = resp.json()
    assert "gated" in payload
    # When gated, questions list is empty to prevent evaluation contamination
    assert payload["questions"] == []
    assert "gated" in payload["message"].lower() or payload["gated"] is True


def test_ask_response_schema_fields():
    """Verify AskResponse model contract has all expected fields."""
    response = AskResponse(
        answer="Grounding verified.",
        confidence="high",
        category="historical",
        sources=["https://github.com/pallets/flask/pull/1"],
        evidence=[],
        people=["davidism"],
        dates=["2018-05-01"],
        graph_path=[],
        relevant_files=["flask/app.py"],
        mode="llm",
    )
    dumped = response.model_dump()
    for field_name in [
        "answer",
        "confidence",
        "category",
        "sources",
        "evidence",
        "people",
        "dates",
        "graph_path",
        "relevant_files",
        "mode",
    ]:
        assert field_name in dumped


def test_chat_routes_exist():
    """Verify chat endpoints are registered on FastAPI app."""
    routes = {route.path for route in app.routes}  # type: ignore[attr-defined]
    assert "/chat" in routes
    assert "/chat/session/{session_id}" in routes


def test_chat_endpoint_contract(monkeypatch):
    """Verify POST /chat responds with ChatResponse structure."""
    from app.api import chat_service
    
    if chat_service.llm:
        monkeypatch.setattr(
            chat_service.llm,
            "generate",
            lambda system, user, history=None: "Python is a programming language."
        )

    client = TestClient(app)
    resp = client.post(
        "/chat",
        json={"question": "What is Python?", "mode": "general", "session_id": "test-session-1"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "mode_used" in data
    assert "session_id" in data
    assert "usage" in data
    assert data["session_id"] == "test-session-1"

    # Test session inspection
    session_resp = client.get("/chat/session/test-session-1")
    assert session_resp.status_code == 200
    sdata = session_resp.json()
    assert sdata["message_count"] >= 2  # user + assistant

    # Test session clear
    del_resp = client.delete("/chat/session/test-session-1")
    assert del_resp.status_code == 200
    assert del_resp.json()["cleared"] is True
