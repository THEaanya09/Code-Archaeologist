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


class AskResponse(BaseModel):
    answer: str
    confidence: str
    sources: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    graph_path: list[GraphNode] = Field(default_factory=list)
    mode: str
