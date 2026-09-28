"""Question -> retrieval -> evidence-only answer orchestration."""
from __future__ import annotations

from app.answer import generate_answer
from app.config import get_settings
from app.models import AskResponse
from app.neo4j_client import Neo4jClient
from app.providers import make_embeddings, make_llm
from app.retrieval import Retriever
from app.utils import unique_keep_order


class GraphRAGEngine:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.neo4j = Neo4jClient.from_env()
        if self.neo4j is not None:
            try:
                self.neo4j.verify()
            except Exception as exc:
                print(f"Neo4j unavailable; using local retrieval: {exc}")
                self.neo4j.close()
                self.neo4j = None
        self.llm = make_llm(self.settings)
        self.embeddings = make_embeddings(self.settings)
        self.retriever = Retriever(self.neo4j, self.embeddings)

    def ask(self, question: str, top_k: int = 5) -> AskResponse:
        evidence = self.retriever.search(question, top_k=top_k)
        answer, confidence, people, dates, mode = generate_answer(question, evidence, self.llm)
        sources = unique_keep_order([e.source_url for e in evidence if e.source_url])
        people = unique_keep_order(people + [p for e in evidence for p in e.people])
        dates = unique_keep_order(dates + [d for e in evidence for d in e.dates])
        path = self.retriever.graph_path(evidence[0].decision_id) if evidence else []
        return AskResponse(
            answer=answer,
            confidence=confidence,
            sources=sources,
            evidence=evidence,
            people=people,
            dates=dates,
            graph_path=path,
            mode=mode if evidence else "fallback",
        )

    def close(self) -> None:
        if self.neo4j is not None:
            self.neo4j.close()
