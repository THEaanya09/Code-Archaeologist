"""Unit tests for ChatService, session management, routing, and rate limiting."""
from __future__ import annotations

import pytest
from app.chat_service import ChatService, RateLimiter
from app.providers import LLMProvider


class MockLLM(LLMProvider):
    def __init__(self, response_text: str = "Mock answer"):
        self.response_text = response_text
        self.call_history = []

    def generate(self, system: str, user: str, history: list[dict[str, str]] | None = None) -> str:
        self.call_history.append({"system": system, "user": user, "history": history or []})
        return self.response_text

    def get_last_usage(self) -> dict[str, int] | None:
        return {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}


class MockEngine:
    def __init__(self, llm: LLMProvider | None = None):
        self.llm = llm
        self.neo4j = None

    def ask(self, question: str, top_k: int = 5):
        from app.models import AskResponse
        return AskResponse(
            answer=f"Repo analysis for {question}",
            confidence="high",
            category="repository",
            sources=["https://github.com/pallets/flask/commit/abc"],
            evidence=[],
            people=["mitsuhiko"],
            dates=["2010-04-16"],
            graph_path=[],
            relevant_files=["flask/app.py"],
            mode="rag",
        )


def test_general_mode_flow():
    mock_llm = MockLLM("Python is versatile.")
    engine = MockEngine(mock_llm)
    service = ChatService(engine)

    result = service.chat("Explain Python", mode="general", session_id="sess_1")
    assert result["answer"] == "Python is versatile."
    assert result["mode_used"] == "general"
    assert result["session_id"] == "sess_1"
    assert result["usage"]["total_tokens"] == 30

    # Verify session recorded the conversation
    info = service.get_session_info("sess_1")
    assert info["message_count"] == 2  # user + assistant


def test_repository_mode_flow():
    mock_llm = MockLLM("ignored")
    engine = MockEngine(mock_llm)
    service = ChatService(engine)

    result = service.chat("Why was RequestContext added?", mode="repository", session_id="sess_2")
    assert "Repo analysis" in result["answer"]
    assert result["mode_used"] == "repository"
    assert len(result["sources"]) == 1
    assert result["sources"][0] == "https://github.com/pallets/flask/commit/abc"


def test_auto_mode_routing():
    mock_llm = MockLLM("A decorator is a function.")
    engine = MockEngine(mock_llm)
    service = ChatService(engine)

    # General question -> routed to general
    res_gen = service.chat("What is a decorator?", mode="auto", session_id="sess_3")
    assert res_gen["mode_used"] == "general"

    # Repo question with git terminology -> routed to repository
    res_repo = service.chat("Why was commit 123 merged in PR 456?", mode="auto", session_id="sess_3")
    assert res_repo["mode_used"] == "repository"


def test_rate_limiter():
    limiter = RateLimiter(daily_limit=2)
    assert limiter.check("user_a") == (True, 2)
    limiter.record("user_a")
    assert limiter.check("user_a") == (True, 1)
    limiter.record("user_a")
    assert limiter.check("user_a") == (False, 0)


def test_session_clearing():
    mock_llm = MockLLM("Hello")
    engine = MockEngine(mock_llm)
    service = ChatService(engine)

    service.chat("Hi", mode="general", session_id="sess_clear")
    assert service.get_session_info("sess_clear")["exists"] is True

    service.clear_session("sess_clear")
    assert service.get_session_info("sess_clear")["exists"] is False
