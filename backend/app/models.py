"""Typed API and graph models."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)


class Evidence(BaseModel):
    decision_id: str
    summary: str
    rationale: str
    confidence: str = "low"
    source_type: str = "unknown"
    source_id: int | str | None = None
    source_url: str | None = None
    evidence_snippet: str | None = None
    score: float = 0.0
    people: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)


class GraphNode(BaseModel):
    label: str
    key: str


class ArchitectureStep(BaseModel):
    title: str
    description: str
    file_path: str | None = None
    component: str | None = None


class KeyModule(BaseModel):
    name: str
    file: str
    role: str
    description: str


class AskResponse(BaseModel):
    answer: str
    confidence: str
    category: str = "historical"  # "historical" | "repository" | "general" | "hybrid"
    overview: str | None = None
    concept: str | None = None
    how_it_works: str | None = None
    in_repository: str | None = None
    architecture_flow: list[ArchitectureStep] = Field(default_factory=list)
    key_modules: list[KeyModule] = Field(default_factory=list)
    relevant_files: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    graph_path: list[GraphNode] = Field(default_factory=list)
    mode: str


# ── Chat models for conversational endpoint ──────────────────────────

class ChatRequest(BaseModel):
    """Request model for the /chat conversational endpoint."""
    question: str = Field(min_length=1, max_length=2000)
    mode: str = Field(default="auto", pattern="^(general|repository|auto)$")
    session_id: str = Field(default="default", min_length=1, max_length=100)


class ChatResponse(BaseModel):
    """Response model for the /chat conversational endpoint."""
    answer: str = ""
    mode_used: str = "auto"
    category: str | None = None
    confidence: str | None = None
    overview: str | None = None
    sources: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    graph_path: list[GraphNode] = Field(default_factory=list)
    relevant_files: list[str] = Field(default_factory=list)
    architecture_flow: list[ArchitectureStep] = Field(default_factory=list)
    key_modules: list[KeyModule] = Field(default_factory=list)
    usage: dict[str, int] | None = None
    remaining_requests: int | None = None
    session_id: str = "default"
    cached: bool = False
    error: str | None = None

