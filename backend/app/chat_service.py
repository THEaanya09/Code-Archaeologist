"""Conversational chat service with session management, routing, and rate limiting.

Provides two modes:
  - General AI: Direct LLM Q&A for programming/technology questions
  - Repository Analysis: GraphRAG-powered evidence-grounded answers
  - Auto: Lightweight heuristic routing using the existing classifier
"""
from __future__ import annotations

import hashlib
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from app.classifier import classify_query
from app.config import get_settings
from app.graphrag import GraphRAGEngine
from app.providers import LLMProvider

logger = logging.getLogger(__name__)

# ── Compact system prompts (token-efficient) ─────────────────────────────

GENERAL_SYSTEM_PROMPT = """You are Code Archaeologist, an expert AI programming assistant.
Answer questions about programming, software engineering, frameworks, and technology clearly and concisely.
Use markdown formatting with code blocks when showing code.
Keep responses focused and avoid unnecessary verbosity."""

REPO_SYSTEM_PROMPT = """You are Code Archaeologist, a repository analysis assistant for {repo}.
Answer questions using ONLY the provided evidence from the repository's commits, PRs, issues, and code.
If evidence is insufficient, say so clearly rather than guessing.
Cite specific commits, PRs, or files when available.
Use markdown formatting."""


@dataclass
class ChatMessage:
    role: str  # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)
    mode: str = "auto"
    usage: dict[str, int] | None = None


@dataclass
class ChatSession:
    session_id: str
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    request_count: int = 0
    total_tokens_used: int = 0


class RateLimiter:
    """In-memory per-session rate limiter (development mode).

    NOT production-grade. Suitable for single-instance development deployments.
    For production, use Redis or a database-backed solution.
    """

    def __init__(self, daily_limit: int = 20) -> None:
        self.daily_limit = daily_limit
        self._counters: dict[str, list[float]] = defaultdict(list)

    def check(self, session_id: str) -> tuple[bool, int]:
        """Check if session is within rate limit.

        Returns:
            (allowed, remaining_requests)
        """
        now = time.time()
        day_start = now - 86400  # 24h window

        # Prune old entries
        self._counters[session_id] = [
            ts for ts in self._counters[session_id] if ts > day_start
        ]

        count = len(self._counters[session_id])
        remaining = max(0, self.daily_limit - count)
        return count < self.daily_limit, remaining

    def record(self, session_id: str) -> None:
        self._counters[session_id].append(time.time())


class ChatService:
    """Manages conversational chat sessions with Sarvam AI integration."""

    def __init__(self, engine: GraphRAGEngine) -> None:
        self.engine = engine
        self.settings = get_settings()
        self.llm = engine.llm
        self._sessions: dict[str, ChatSession] = {}
        self._rate_limiter = RateLimiter(daily_limit=self.settings.daily_request_limit)
        self._response_cache: dict[str, dict[str, Any]] = {}

    def _get_or_create_session(self, session_id: str) -> ChatSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = ChatSession(session_id=session_id)
        return self._sessions[session_id]

    def _build_history(self, session: ChatSession) -> list[dict[str, str]]:
        """Build conversation history limited to max_history_messages."""
        max_msgs = self.settings.max_history_messages
        recent = session.messages[-(max_msgs):]
        return [{"role": m.role, "content": m.content} for m in recent]

    def _truncate_context(self, text: str, max_chars: int = 3000) -> str:
        """Intelligently truncate context to fit token budgets."""
        if len(text) <= max_chars:
            return text
        # Keep the first part and add a truncation notice
        return text[:max_chars] + "\n\n[Context truncated for token efficiency]"

    def _cache_key(self, question: str, mode: str) -> str:
        """Generate a cache key for repeated requests."""
        return hashlib.md5(f"{question.lower().strip()}:{mode}".encode()).hexdigest()

    def route_question(self, question: str, mode: str) -> str:
        """Route question to the appropriate handler.

        Args:
            question: The user's question.
            mode: One of "general", "repository", "auto".

        Returns:
            The resolved mode: "general" or "repository".
        """
        if mode == "general":
            return "general"
        if mode == "repository":
            return "repository"

        # Auto mode: use the existing deterministic classifier
        category = classify_query(question)
        if category in ("historical", "repository", "hybrid"):
            return "repository"
        return "general"

    def _handle_general(
        self, question: str, session: ChatSession
    ) -> dict[str, Any]:
        """Handle a general AI question with conversation context."""
        if self.llm is None:
            return {
                "answer": "LLM is not configured. Please set SARVAM_API_KEY in the backend environment.",
                "mode_used": "general",
                "category": "general",
                "confidence": "low",
                "sources": [],
                "evidence": [],
                "usage": None,
            }

        history = self._build_history(session)

        try:
            raw = self.llm.generate(
                system=GENERAL_SYSTEM_PROMPT,
                user=question,
                history=history,
            )
            usage = self.llm.get_last_usage()

            return {
                "answer": raw,
                "mode_used": "general",
                "category": "general",
                "confidence": "high",
                "sources": [],
                "evidence": [],
                "usage": usage,
            }
        except RuntimeError as exc:
            logger.error(f"General Q&A error: {exc}")
            raise

    def _handle_repository(
        self, question: str, session: ChatSession
    ) -> dict[str, Any]:
        """Handle a repository-specific question using GraphRAG + Sarvam AI."""
        # Use the existing GraphRAG engine for retrieval and answer generation
        try:
            ask_response = self.engine.ask(question, top_k=self.settings.max_retrieved_chunks)

            # If we have an LLM and conversation history, enhance the answer with context
            answer = ask_response.answer
            usage = None

            if self.llm is not None and len(session.messages) > 0:
                # Build a compact evidence package for conversational follow-up
                history = self._build_history(session)
                evidence_context = ""
                if ask_response.evidence:
                    snippets = []
                    for e in ask_response.evidence[:self.settings.max_retrieved_chunks]:
                        snippet = f"- [{e.decision_id}] {e.summary}: {e.rationale}"
                        if e.source_url:
                            snippet += f" (Source: {e.source_url})"
                        snippets.append(snippet)
                    evidence_context = "\n".join(snippets)

                repo = self.settings.github_repo
                system = REPO_SYSTEM_PROMPT.format(repo=repo)
                context_prompt = question
                if evidence_context:
                    context_prompt = f"""QUESTION: {question}

REPOSITORY EVIDENCE:
{self._truncate_context(evidence_context)}

Previous answer context: {self._truncate_context(answer, 500)}

Provide a clear, evidence-grounded answer. Cite specific evidence IDs when available."""

                try:
                    enhanced = self.llm.generate(
                        system=system,
                        user=context_prompt,
                        history=history,
                    )
                    usage = self.llm.get_last_usage()
                    answer = enhanced
                except Exception as exc:
                    logger.warning(f"Enhanced repo answer failed, using base: {exc}")

            return {
                "answer": answer,
                "mode_used": "repository",
                "category": ask_response.category,
                "confidence": ask_response.confidence,
                "overview": ask_response.overview,
                "sources": ask_response.sources,
                "evidence": [e.model_dump() for e in ask_response.evidence],
                "people": ask_response.people,
                "dates": ask_response.dates,
                "graph_path": [n.model_dump() for n in ask_response.graph_path],
                "relevant_files": ask_response.relevant_files,
                "architecture_flow": [s.model_dump() for s in ask_response.architecture_flow],
                "key_modules": [m.model_dump() for m in ask_response.key_modules],
                "mode": ask_response.mode,
                "usage": usage,
            }
        except Exception as exc:
            logger.error(f"Repository Q&A error: {exc}")
            raise

    def chat(
        self, question: str, mode: str = "auto", session_id: str = "default"
    ) -> dict[str, Any]:
        """Process a chat message and return a response.

        Args:
            question: User's question text.
            mode: "general", "repository", or "auto".
            session_id: Session identifier for conversation continuity.

        Returns:
            Response dict with answer, mode_used, evidence, usage, etc.
        """
        # Validate input
        question = question.strip()
        if not question:
            return {
                "answer": "",
                "mode_used": mode,
                "error": "Empty message. Please ask a question.",
                "usage": None,
            }

        if len(question) < 1:
            return {
                "answer": "",
                "mode_used": mode,
                "error": "Question too short. Please provide more detail.",
                "usage": None,
            }

        # Rate limit check
        allowed, remaining = self._rate_limiter.check(session_id)
        if not allowed:
            return {
                "answer": "",
                "mode_used": mode,
                "error": f"Daily request limit ({self.settings.daily_request_limit}) reached. Try again tomorrow.",
                "remaining_requests": 0,
                "usage": None,
            }

        # Check cache for identical recent questions
        cache_key = self._cache_key(question, mode)
        if cache_key in self._response_cache:
            cached = self._response_cache[cache_key]
            cached["cached"] = True
            return cached

        session = self._get_or_create_session(session_id)

        # Route question
        resolved_mode = self.route_question(question, mode)

        # Generate response
        try:
            if resolved_mode == "general":
                result = self._handle_general(question, session)
            else:
                result = self._handle_repository(question, session)

            # Store user and assistant messages in conversation history
            session.messages.append(
                ChatMessage(role="user", content=question, mode=resolved_mode)
            )
            session.messages.append(
                ChatMessage(
                    role="assistant",
                    content=result.get("answer", ""),
                    mode=resolved_mode,
                    usage=result.get("usage"),
                )
            )

            # Track usage
            session.request_count += 1
            self._rate_limiter.record(session_id)
            if result.get("usage") and result["usage"].get("total_tokens"):
                session.total_tokens_used += result["usage"]["total_tokens"]

            result["remaining_requests"] = remaining - 1
            result["session_id"] = session_id
            result["cached"] = False

            # Cache result (limited cache size)
            if len(self._response_cache) > 100:
                # Evict oldest entries
                oldest_keys = list(self._response_cache.keys())[:50]
                for k in oldest_keys:
                    del self._response_cache[k]
            self._response_cache[cache_key] = result

            return result

        except RuntimeError as exc:
            error_msg = str(exc)
            return {
                "answer": "",
                "mode_used": resolved_mode,
                "error": error_msg,
                "remaining_requests": remaining,
                "session_id": session_id,
                "usage": None,
            }

    def get_session_info(self, session_id: str) -> dict[str, Any]:
        """Return session statistics."""
        session = self._sessions.get(session_id)
        if not session:
            return {"exists": False}

        allowed, remaining = self._rate_limiter.check(session_id)
        return {
            "exists": True,
            "session_id": session_id,
            "message_count": len(session.messages),
            "request_count": session.request_count,
            "total_tokens_used": session.total_tokens_used,
            "remaining_requests": remaining,
            "created_at": session.created_at,
        }

    def clear_session(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
