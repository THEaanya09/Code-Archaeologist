"""Lightweight local smoke checks for known and unsupported questions."""
from __future__ import annotations

import json

from app.graphrag import GraphRAGEngine


KNOWN = "Why did Flask 1.0 remove the deprecated flask.ext import namespace instead of keeping it as a compatibility shim?"
UNSUPPORTED = "Why did Flask 1.0 switch from PostgreSQL to MongoDB for its database layer?"


def main() -> None:
    engine = GraphRAGEngine()
    try:
        known = engine.ask(KNOWN, top_k=5)
        unsupported = engine.ask(UNSUPPORTED, top_k=5)
        print(json.dumps({"known": known.model_dump(), "unsupported": unsupported.model_dump()}, indent=2))
    finally:
        engine.close()


if __name__ == "__main__":
    main()
