"""Question classification -> differentiated retrieval -> category-tailored answer orchestration."""
from __future__ import annotations

from app.answer import (
    generate_general_answer,
    generate_historical_answer,
    generate_hybrid_answer,
    generate_repository_answer,
)
from app.classifier import classify_query
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
        # 1. Classify query into: historical, repository, general, hybrid
        category = classify_query(question)

        # 2. Differentiated Retrieval & Answer Synthesis
        if category == "historical":
            evidence = self.retriever.search_historical_decisions(question, top_k=top_k)
            answer, confidence, people, dates, mode = generate_historical_answer(
                question, evidence, self.llm
            )
            sources = unique_keep_order([e.source_url for e in evidence if e.source_url])
            people = unique_keep_order(people + [p for e in evidence for p in e.people])
            dates = unique_keep_order(dates + [d for e in evidence for d in e.dates])
            graph_path = self.retriever.graph_path(evidence[0].decision_id) if evidence else []
            relevant_files = self.retriever.search_files(question, top_k=4)

            return AskResponse(
                answer=answer,
                confidence=confidence,
                category=category,
                overview=None,
                sources=sources,
                evidence=evidence,
                people=people,
                dates=dates,
                graph_path=graph_path,
                relevant_files=relevant_files,
                mode=mode if evidence else "fallback",
            )

        elif category == "repository":
            modules, flow, relevant_files = self.retriever.search_architecture(question)
            evidence = self.retriever.search(question, category="repository", top_k=2)
            sources = unique_keep_order([e.source_url for e in evidence if e.source_url])
            res_data = generate_repository_answer(
                question, modules, flow, relevant_files, evidence, self.llm
            )
            graph_path = self.retriever.graph_path_for_architecture(question)

            return AskResponse(
                answer=res_data["answer"],
                confidence=res_data["confidence"],
                category=category,
                overview=res_data.get("overview"),
                architecture_flow=flow,
                key_modules=modules,
                relevant_files=relevant_files,
                sources=sources,
                evidence=evidence,
                people=unique_keep_order([p for e in evidence for p in e.people]),
                dates=unique_keep_order([d for e in evidence for d in e.dates]),
                graph_path=graph_path,
                mode=res_data.get("mode", "llm"),
            )

        elif category == "general":
            concept_data = self.retriever.search_concept(question)
            relevant_files = (
                concept_data.get("relevant_files", [])
                if concept_data
                else self.retriever.search_files(question, top_k=4)
            )
            res_data = generate_general_answer(
                question, concept_data, relevant_files, self.llm
            )
            graph_path = self.retriever.graph_path_for_architecture(question)

            return AskResponse(
                answer=res_data["answer"],
                confidence=res_data["confidence"],
                category=category,
                overview=None,
                concept=res_data.get("concept"),
                how_it_works=res_data.get("how_it_works"),
                in_repository=res_data.get("in_repository"),
                relevant_files=relevant_files,
                sources=[],
                evidence=[],
                people=[],
                dates=[],
                graph_path=graph_path,
                mode=res_data.get("mode", "llm"),
            )

        else:  # hybrid
            evidence = self.retriever.search_historical_decisions(question, top_k=top_k)
            modules, flow, relevant_files = self.retriever.search_architecture(question)
            concept_data = self.retriever.search_concept(question)
            res_data = generate_hybrid_answer(
                question, evidence, modules, concept_data, self.llm
            )
            sources = unique_keep_order([e.source_url for e in evidence if e.source_url])
            graph_path = (
                self.retriever.graph_path(evidence[0].decision_id)
                if evidence
                else self.retriever.graph_path_for_architecture(question)
            )

            return AskResponse(
                answer=res_data["answer"],
                confidence=res_data["confidence"],
                category=category,
                overview=res_data.get("overview"),
                architecture_flow=flow if ("how" in question.lower() or "structure" in question.lower()) else [],
                key_modules=modules[:4],
                relevant_files=relevant_files,
                sources=sources,
                evidence=evidence,
                people=res_data.get("people", []),
                dates=res_data.get("dates", []),
                graph_path=graph_path,
                mode=res_data.get("mode", "llm"),
            )

    def close(self) -> None:
        if self.neo4j is not None:
            self.neo4j.close()
