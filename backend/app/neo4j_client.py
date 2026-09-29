"""Small Neo4j driver wrapper."""
from __future__ import annotations

import certifi
import neo4j
from neo4j import GraphDatabase

from app.config import get_settings


class Neo4jClient:
    def __init__(self, uri: str, username: str, password: str) -> None:
        self.uri = uri
        self.username = username
        self.password = password

        # On macOS/Linux where default OpenSSL root store may miss Aura CAs,
        # use certifi bundle for neo4j+s:// and bolt+s://
        if uri.startswith("neo4j+s://"):
            norm_uri = "neo4j://" + uri[len("neo4j+s://"):]
            self.driver = GraphDatabase.driver(
                norm_uri,
                auth=(username, password),
                encrypted=True,
                trusted_certificates=neo4j.TrustCustomCAs(certifi.where()),
            )
        elif uri.startswith("bolt+s://"):
            norm_uri = "bolt://" + uri[len("bolt+s://"):]
            self.driver = GraphDatabase.driver(
                norm_uri,
                auth=(username, password),
                encrypted=True,
                trusted_certificates=neo4j.TrustCustomCAs(certifi.where()),
            )
        else:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))

    @classmethod
    def from_env(cls) -> "Neo4jClient | None":
        settings = get_settings()
        if not settings.neo4j_enabled:
            return None
        return cls(settings.neo4j_uri or "", settings.neo4j_username or "", settings.neo4j_password or "")

    def verify(self) -> bool:
        try:
            self.run("RETURN 1 as ok")
            return True
        except Exception:
            self.driver.verify_connectivity()
            return True

    def run(self, query: str, **params):
        q_upper = query.strip().upper()
        is_write = any(kw in q_upper for kw in ("CREATE", "MERGE", "DELETE", "SET", "DROP"))
        routing = neo4j.RoutingControl.WRITE if is_write else neo4j.RoutingControl.READ
        records, _, _ = self.driver.execute_query(query, routing_=routing, **params)
        return [record.data() for record in records]

    def close(self) -> None:
        self.driver.close()
