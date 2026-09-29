"""Evidence-first retrieval with differentiated strategies for Historical, Repository, and General queries."""
from __future__ import annotations

from typing import Any

from app.models import ArchitectureStep, Evidence, GraphNode, KeyModule
from app.providers import EmbeddingProvider
from app.repo_context import FLASK_MODULES, FLASK_REQUEST_FLOW, find_matching_concept
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
        try:
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
        except Exception as exc:
            print(f"Neo4j decision query skipped: {exc}")
            return []

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

    def search_historical_decisions(self, question: str, top_k: int = 5) -> list[Evidence]:
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

        # Gate against irrelevant noise
        if ranked[0].score < 0.35:
            return []

        best_score = ranked[0].score
        threshold = best_score * 0.65
        return [item for item in ranked[:top_k] if item.score >= threshold]

    def search_files(self, query: str, top_k: int = 6) -> list[str]:
        q_lower = query.lower()
        scored_files: list[tuple[float, str]] = []

        # Check Neo4j File nodes
        if self.neo4j is not None:
            try:
                rows = self.neo4j.run("MATCH (f:File) RETURN f.path as path")
                for r in rows:
                    path = r["path"]
                    score = lexical_score(q_lower, path)
                    # Boost exact module names
                    for part in path.replace(".py", "").split("/"):
                        if part in q_lower and len(part) > 2:
                            score += 1.0
                    if score > 0:
                        scored_files.append((score, path))
            except Exception:
                pass

        # Also search normalized files.json
        from app.config import NORMALIZED_DIR
        files_json = NORMALIZED_DIR / "files.json"
        if files_json.exists():
            for f in read_json(files_json):
                path = f.get("path", "")
                score = lexical_score(q_lower, path)
                for part in path.replace(".py", "").split("/"):
                    if part in q_lower and len(part) > 2:
                        score += 1.0
                if score > 0 and path not in [p for _, p in scored_files]:
                    scored_files.append((score, path))

        scored_files.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored_files[:top_k]]

    def search_architecture(self, question: str) -> tuple[list[KeyModule], list[ArchitectureStep], list[str]]:
        q_lower = question.lower()

        # Find matching or core modules
        matched_modules: list[KeyModule] = []
        is_general_arch = any(term in q_lower for term in ("architecture", "structure of flask", "major modules", "how do these modules", "codebase"))

        for mod in FLASK_MODULES:
            # If broad architecture, include core kernel modules
            if is_general_arch:
                matched_modules.append(KeyModule(
                    name=mod["module"],
                    file=mod["file"],
                    role=mod["component"],
                    description=mod["description"],
                ))
            else:
                # Check keyword relevance
                score = lexical_score(q_lower, f"{mod['module']} {mod['component']} {mod['description']}")
                if score > 0.15 or any(term in q_lower for term in (mod["file"].replace("flask/", "").replace(".py", ""), mod["module"])):
                    matched_modules.append(KeyModule(
                        name=mod["module"],
                        file=mod["file"],
                        role=mod["component"],
                        description=mod["description"],
                    ))

        if not matched_modules:
            # Default to primary core modules
            for mod in FLASK_MODULES[:5]:
                matched_modules.append(KeyModule(
                    name=mod["module"],
                    file=mod["file"],
                    role=mod["component"],
                    description=mod["description"],
                ))

        # Architecture request flow stages
        flow_steps: list[ArchitectureStep] = []
        for step in FLASK_REQUEST_FLOW:
            flow_steps.append(ArchitectureStep(
                title=step["title"],
                component=step["component"],
                file_path=step["file_path"],
                description=step["description"],
            ))

        # Relevant files
        relevant_files = self.search_files(question)
        for m in matched_modules:
            if m.file not in relevant_files:
                relevant_files.append(m.file)

        return matched_modules, flow_steps, relevant_files

    def search_concept(self, question: str) -> dict[str, Any] | None:
        return find_matching_concept(question)

    def search(self, question: str, category: str = "historical", top_k: int = 5) -> list[Evidence]:
        if category == "historical":
            return self.search_historical_decisions(question, top_k=top_k)
        elif category == "hybrid":
            return self.search_historical_decisions(question, top_k=top_k)
        elif category == "repository":
            # For repository questions, decisions are secondary historical evidence if directly matching
            return self.search_historical_decisions(question, top_k=2)
        else:
            # For general questions, evidence is optional
            return []

    def graph_path(self, decision_id: str) -> list[GraphNode]:
        if self.neo4j is None:
            return []

        try:
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
        except Exception:
            return []

    def graph_path_for_architecture(self, topic: str = "architecture") -> list[GraphNode]:
        """Provides structural graph relationships for repository architecture."""
        t = topic.lower()
        if "routing" in t:
            return [
                GraphNode(label="Kernel", key="flask/app.py:Flask"),
                GraphNode(label="Map", key="werkzeug.routing.Map"),
                GraphNode(label="Blueprint", key="flask/blueprints.py:Blueprint"),
                GraphNode(label="Dispatcher", key="Flask.dispatch_request"),
            ]
        elif "wsgi" in t or "request" in t or "lifecycle" in t or "enter" in t:
            return [
                GraphNode(label="Server", key="WSGI Server (Gunicorn/Werkzeug)"),
                GraphNode(label="Gateway", key="Flask.wsgi_app"),
                GraphNode(label="Context", key="RequestContext (ctx.push)"),
                GraphNode(label="Dispatcher", key="Flask.dispatch_request"),
                GraphNode(label="Response", key="Flask.make_response"),
            ]
        else:
            return [
                GraphNode(label="Entry", key="flask/app.py:Flask"),
                GraphNode(label="Context", key="flask/ctx.py:RequestContext"),
                GraphNode(label="Modules", key="flask/blueprints.py"),
                GraphNode(label="Session", key="flask/sessions.py"),
            ]
