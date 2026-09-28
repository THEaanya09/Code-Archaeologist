"""Evidence-first retrieval with deterministic lexical scoring and optional vectors."""
from __future__ import annotations

from app.models import Evidence, GraphNode
from app.providers import EmbeddingProvider
from app.utils import lexical_score, read_json


class Retriever:
    def __init__(self, neo4j=None, embeddings: EmbeddingProvider | None = None) -> None:
        self.neo4j = neo4j
        self.embeddings = embeddings

    def _local_decisions(self, question: str) -> list[Evidence]:
        from app.config import PROCESSED_DIR

        path = PROCESSED_DIR / "extracted_decisions.json"
        if not path.exists():
            return []
        scored = []
        for row in read_json(path):
            text = " ".join([
                row.get("summary", ""),
                row.get("rationale", ""),
                row.get("tradeoffs") or "",
            ])
            score = lexical_score(question, text)
            scored.append((score, row))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            Evidence(
                decision_id=row["id"],
                summary=row["summary"],
                rationale=row["rationale"],
                confidence=row.get("confidence", "low"),
                source_type=row.get("source_type", "unknown"),
                source_id=row.get("source_id"),
                source_url=row.get("source_url"),
                evidence_snippet=row.get("evidence_snippet"),
                score=score,
                people=row.get("people", []),
                dates=row.get("dates", []),
            )
            for score, row in scored[:10]
            if score > 0
        ]

    def _neo4j_decisions(self, question: str, top_k: int) -> list[Evidence]:
        if self.neo4j is None:
            return []
        rows = self.neo4j.run(
            """
            MATCH (d:Decision)
            RETURN d.id AS decision_id,
                   d.summary AS summary,
                   d.rationale AS rationale,
                   d.confidence AS confidence,
                   d.source_type AS source_type,
                   d.source_id AS source_id,
                   d.source_url AS source_url,
                   d.evidence_snippet AS evidence_snippet,
                   d.person_login AS person_login,
                   d.decision_date AS decision_date
            LIMIT 200
            """
        )
        candidates = []
        for row in rows:
            text = " ".join([row.get("summary") or "", row.get("rationale") or ""])
            score = lexical_score(question, text)
            if score > 0:
                people = [row["person_login"]] if row.get("person_login") else []
                dates = [row["decision_date"]] if row.get("decision_date") else []
                candidates.append((score, Evidence(
                    decision_id=row["decision_id"],
                    summary=row["summary"],
                    rationale=row["rationale"],
                    confidence=row.get("confidence", "low"),
                    source_type=row.get("source_type", "unknown"),
                    source_id=row.get("source_id"),
                    source_url=row.get("source_url"),
                    evidence_snippet=row.get("evidence_snippet"),
                    score=score,
                    people=people,
                    dates=dates,
                )))
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in candidates[:top_k]]

    def _neo4j_vector(self, question: str, top_k: int) -> list[Evidence]:
        if self.neo4j is None or self.embeddings is None:
            return []
        try:
            vector = self.embeddings.embed(question)
            rows = self.neo4j.run(
                """
                CALL db.index.vector.queryNodes('decision_embedding', $k, $vector)
                YIELD node, score
                RETURN node.id AS decision_id,
                       node.summary AS summary,
                       node.rationale AS rationale,
                       node.confidence AS confidence,
                       node.source_type AS source_type,
                       node.source_id AS source_id,
                       node.source_url AS source_url,
                       node.evidence_snippet AS evidence_snippet,
                       node.person_login AS person_login,
                       node.decision_date AS decision_date,
                       score
                """,
                k=top_k,
                vector=vector,
            )
            return [Evidence(
                decision_id=row["decision_id"],
                summary=row["summary"],
                rationale=row["rationale"],
                confidence=row.get("confidence", "low"),
                source_type=row.get("source_type", "unknown"),
                source_id=row.get("source_id"),
                source_url=row.get("source_url"),
                evidence_snippet=row.get("evidence_snippet"),
                score=float(row.get("score", 0.0)),
                people=[row["person_login"]] if row.get("person_login") else [],
                dates=[row["decision_date"]] if row.get("decision_date") else [],
            ) for row in rows]
        except Exception as exc:
            print(f"Vector retrieval skipped: {exc}")
            return []

    def search(self, question: str, top_k: int = 5) -> list[Evidence]:
        combined: dict[str, Evidence] = {}

        for item in self._local_decisions(question):
            combined[item.decision_id] = item
        for item in self._neo4j_vector(question, top_k):
            existing = combined.get(item.decision_id)
            if existing is None or item.score > existing.score:
                combined[item.decision_id] = item
        for item in self._neo4j_decisions(question, top_k):
            existing = combined.get(item.decision_id)
            if existing is None or item.score > existing.score:
                combined[item.decision_id] = item

        ranked = sorted(combined.values(), key=lambda x: x.score, reverse=True)
        if not ranked:
            return []

        # Hard gate against generic/common-word matches.
        if ranked[0].score < 0.5:
            return []

        best_score = ranked[0].score
        threshold = best_score * 0.75
        return [item for item in ranked[:top_k] if item.score >= threshold]

    def graph_path(self, decision_id: str) -> list[GraphNode]:
        if self.neo4j is None:
            return []

        rows = self.neo4j.run(
            """
            MATCH (d:Decision {id:$id})
            OPTIONAL MATCH (d)-[:JUSTIFIES]->(pr:PR)
            OPTIONAL MATCH (d)-[:JUSTIFIES]->(issue:Issue)
            OPTIONAL MATCH (d)-[:JUSTIFIES]->(commit:Commit)
            OPTIONAL MATCH (pr)-[:AUTHORED]->(pr_person:Person)
            OPTIONAL MATCH (issue)-[:AUTHORED]->(issue_person:Person)
            OPTIONAL MATCH (commit)-[:AUTHORED]->(commit_person:Person)
            WITH d,
                 coalesce(pr_person, issue_person, commit_person) AS person,
                 pr, issue, commit
            RETURN [x IN [
                CASE WHEN d IS NOT NULL THEN {label:'Decision', key:d.id} END,
                CASE WHEN pr IS NOT NULL THEN {label:'PR', key:toString(pr.number)} END,
                CASE WHEN issue IS NOT NULL THEN {label:'Issue', key:toString(issue.number)} END,
                CASE WHEN commit IS NOT NULL THEN {label:'Commit', key:commit.sha} END,
                CASE WHEN person IS NOT NULL THEN {label:'Person', key:person.login} END
            ] WHERE x IS NOT NULL] AS path
            LIMIT 1
            """,
            id=decision_id,
        )
        if not rows:
            return []
        return [GraphNode(**node) for node in rows[0]["path"]]
