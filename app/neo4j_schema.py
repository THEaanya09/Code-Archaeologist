"""Create the stable Neo4j constraints needed by the MVP."""
from __future__ import annotations

from app.neo4j_client import Neo4jClient

CONSTRAINTS = [
    "CREATE CONSTRAINT file_key IF NOT EXISTS FOR (n:File) REQUIRE n.key IS UNIQUE",
    "CREATE CONSTRAINT commit_sha IF NOT EXISTS FOR (n:Commit) REQUIRE n.sha IS UNIQUE",
    "CREATE CONSTRAINT pr_number IF NOT EXISTS FOR (n:PR) REQUIRE n.number IS UNIQUE",
    "CREATE CONSTRAINT issue_number IF NOT EXISTS FOR (n:Issue) REQUIRE n.number IS UNIQUE",
    "CREATE CONSTRAINT person_login IF NOT EXISTS FOR (n:Person) REQUIRE n.login IS UNIQUE",
    "CREATE CONSTRAINT decision_id IF NOT EXISTS FOR (n:Decision) REQUIRE n.id IS UNIQUE",
]


def setup_schema() -> None:
    client = Neo4jClient.from_env()
    if client is None:
        raise RuntimeError("Neo4j configuration missing in .env")
    try:
        client.verify()
        for query in CONSTRAINTS:
            client.run(query)
        print("Neo4j schema ready")
    finally:
        client.close()


if __name__ == "__main__":
    setup_schema()
