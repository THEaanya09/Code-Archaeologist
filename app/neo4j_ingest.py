"""Load normalized repository entities and extracted decisions into Neo4j."""
from __future__ import annotations

from app.config import NORMALIZED_DIR, PROCESSED_DIR
from app.neo4j_client import Neo4jClient
from app.utils import read_json


def ingest() -> None:
    client = Neo4jClient.from_env()
    if client is None:
        raise RuntimeError("Neo4j configuration missing in .env")

    issues = read_json(NORMALIZED_DIR / "issues.json")
    prs = read_json(NORMALIZED_DIR / "prs.json")
    commits = read_json(NORMALIZED_DIR / "commits.json")
    people = read_json(NORMALIZED_DIR / "people.json")
    files = read_json(NORMALIZED_DIR / "files.json")
    decisions = read_json(PROCESSED_DIR / "extracted_decisions.json")

    try:
        client.verify()

        for person in people:
            client.run(
                "MERGE (p:Person {login:$login})",
                login=person["login"],
            )

        for file in files:
            client.run(
                "MERGE (f:File {key:$key}) SET f.repo=$repo, f.status=$status",
                key=file["path"], repo="pallets/flask", status=file.get("status"),
            )

        for issue in issues:
            client.run(
                """
                MERGE (i:Issue {number:$number})
                SET i.title=$title, i.body=$body, i.state=$state,
                    i.created_at=$created_at, i.url=$url, i.author_login=$author_login
                """,
                number=issue["number"], title=issue["title"], body=issue.get("body", ""),
                state=issue.get("state"), created_at=issue.get("created_at"), url=issue.get("url"),
                author_login=issue.get("author_login"),
            )
            if issue.get("author_login"):
                client.run(
                    "MATCH (i:Issue {number:$number}), (p:Person {login:$login}) MERGE (i)-[:AUTHORED]->(p)",
                    number=issue["number"], login=issue["author_login"],
                )

        for pr in prs:
            client.run(
                """
                MERGE (r:PR {number:$number})
                SET r.title=$title, r.body=$body, r.state=$state,
                    r.created_at=$created_at, r.merged_at=$merged_at,
                    r.url=$url, r.author_login=$author_login,
                    r.merge_commit_sha=$merge_commit_sha
                """,
                number=pr["number"], title=pr["title"], body=pr.get("body", ""),
                state=pr.get("state"), created_at=pr.get("created_at"), merged_at=pr.get("merged_at"),
                url=pr.get("url"), author_login=pr.get("author_login"),
                merge_commit_sha=pr.get("merge_commit_sha"),
            )
            if pr.get("author_login"):
                client.run(
                    "MATCH (r:PR {number:$number}), (p:Person {login:$login}) MERGE (r)-[:AUTHORED]->(p)",
                    number=pr["number"], login=pr["author_login"],
                )

        for commit in commits:
            client.run(
                """
                MERGE (c:Commit {sha:$sha})
                SET c.message=$message, c.date=$date, c.url=$url, c.author_login=$author_login
                """,
                sha=commit["sha"], message=commit.get("message", ""), date=commit.get("date"),
                url=commit.get("url"), author_login=commit.get("author_login"),
            )
            if commit.get("author_login"):
                client.run(
                    "MATCH (c:Commit {sha:$sha}), (p:Person {login:$login}) MERGE (c)-[:AUTHORED]->(p)",
                    sha=commit["sha"], login=commit["author_login"],
                )
            for file in commit.get("files", []):
                client.run(
                    "MATCH (c:Commit {sha:$sha}), (f:File {key:$path}) MERGE (c)-[:MODIFIES]->(f)",
                    sha=commit["sha"], path=file["path"],
                )

        for decision in decisions:
            client.run(
                """
                MERGE (d:Decision {id:$id})
                SET d.summary=$summary, d.rationale=$rationale, d.tradeoffs=$tradeoffs,
                    d.confidence=$confidence, d.source_type=$source_type,
                    d.source_id=$source_id, d.source_url=$source_url,
                    d.evidence_snippet=$evidence_snippet,
                    d.person_login=$person_login, d.decision_date=$decision_date
                """,
                id=decision["id"], summary=decision["summary"], rationale=decision["rationale"],
                tradeoffs=decision.get("tradeoffs", ""), confidence=decision["confidence"],
                source_type=decision["source_type"], source_id=decision.get("source_id"),
                source_url=decision.get("source_url"), evidence_snippet=decision.get("evidence_snippet"),
                person_login=(decision.get("people") or [None])[0],
                decision_date=(decision.get("dates") or [None])[0],
            )

            if decision.get("source_type") == "github_pr" and decision.get("source_id"):
                client.run(
                    "MATCH (d:Decision {id:$id}), (r:PR {number:$number}) MERGE (d)-[:JUSTIFIES]->(r)",
                    id=decision["id"], number=int(decision["source_id"]),
                )
            elif decision.get("source_type") == "github_issue" and decision.get("source_id"):
                client.run(
                    "MATCH (d:Decision {id:$id}), (i:Issue {number:$number}) MERGE (d)-[:JUSTIFIES]->(i)",
                    id=decision["id"], number=int(decision["source_id"]),
                )
            elif decision.get("source_type") == "github_commit" and decision.get("source_id"):
                client.run(
                    "MATCH (d:Decision {id:$id}), (c:Commit {sha:$sha}) MERGE (d)-[:JUSTIFIES]->(c)",
                    id=decision["id"], sha=str(decision["source_id"]),
                )

        # Backfill decision person/date from the linked GitHub source.
        client.run(
            """
            MATCH (d:Decision)-[:JUSTIFIES]->(source)
            SET d.person_login = coalesce(d.person_login, source.author_login),
                d.decision_date = coalesce(
                    d.decision_date,
                    source.merged_at,
                    source.created_at,
                    source.date
                )
            """
        )
        # Connect PRs and issues when the golden dataset provides both numbers.
        for decision in decisions:
            gid = decision.get("golden_id")
            if not gid:
                continue
            # The source_of_truth relation is enough for MVP query paths; extra links can be added later.

        print(
            f"Neo4j ingest complete: {len(files)} files, {len(people)} people, "
            f"{len(issues)} issues, {len(prs)} PRs, {len(commits)} commits, {len(decisions)} decisions"
        )
    finally:
        client.close()


if __name__ == "__main__":
    ingest()

