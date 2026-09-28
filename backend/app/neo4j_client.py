"""Small Neo4j driver wrapper."""
from __future__ import annotations

from neo4j import GraphDatabase

from app.config import get_settings


class Neo4jClient:
    def __init__(self, uri: str, username: str, password: str) -> None:
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    @classmethod
    def from_env(cls) -> "Neo4jClient | None":
        settings = get_settings()
        if not settings.neo4j_enabled:
            return None
        return cls(settings.neo4j_uri or "", settings.neo4j_username or "", settings.neo4j_password or "")

    def verify(self) -> bool:
        self.driver.verify_connectivity()
        return True

    def run(self, query: str, **params):
        records, _, _ = self.driver.execute_query(query, **params)
        return [record.data() for record in records]

    def close(self) -> None:
        self.driver.close()

