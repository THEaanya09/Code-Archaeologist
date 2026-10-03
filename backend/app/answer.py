"""Evidence-grounded answer synthesis tailored to query category."""
from __future__ import annotations

from typing import Any

from app.grounding import compute_deterministic_confidence, filter_and_ground_claims
from app.models import ArchitectureStep, Evidence, KeyModule
from app.providers import LLMProvider, parse_json_object
from app.utils import unique_keep_order

SYSTEM_HISTORICAL = """You answer WHY-code and historical software questions using ONLY the supplied repository evidence.
Never invent historical facts, people, dates, motivations, or sources.
Every factual sentence or claim in your response MUST cite its supporting evidence using an exact 'evidence_id' (e.g. 'golden-1').
Do NOT state any fact without citing a provided evidence ID.
Return JSON with key 'claims':
{
  "claims": [
    {"statement": "Sentence explaining the historical decision or reason.", "evidence_id": "golden-X"}
  ]
}"""

SYSTEM_REPOSITORY = """You are a repository architecture expert analyzing pallets/flask.
Explain the architecture, module relationships, or request execution flow using ONLY the supplied code entities and verified modules.
Never hallucinate non-existent files or functions.
Return JSON with keys:
- overview: A high-level technical summary of the subsystem or architectural design (2-3 sentences).
- answer: A detailed explanation of how these modules communicate, where routing/execution occurs, and what happens at each stage."""

SYSTEM_GENERAL = """You are an expert technical educator explaining software engineering concepts with direct grounding in pallets/flask.
Return JSON with keys:
- concept: Clear conceptual definition of the technology or pattern (1-2 sentences).
- how_it_works: General architectural mechanics of how this concept works in software systems.
- in_repository: How pallets/flask specifically implements or integrates this concept, citing actual files.
- answer: Combined comprehensive answer for the user."""

SYSTEM_HYBRID = """You are an expert software historian and systems architect.
Synthesize both the technical architecture/concept and the historical evolution/decision rationale using the supplied evidence.
Every historical claim MUST cite an 'evidence_id' from the provided evidence.
Return JSON with keys:
- claims: List of {"statement": "...", "evidence_id": "golden-X"}
- overview: High-level architectural context in pallets/flask."""


def _fallback_historical(evidence: list[Evidence]) -> tuple[str, str, list[str], list[str]]:
    if not evidence:
        return (
            "I could not find enough evidence in the indexed repository history to answer this reliably.",
            "low",
            [],
            [],
        )
    top = evidence[0]
    conf = compute_deterministic_confidence(evidence, channels_count=1, verified_ratio=1.0)
    return (
        top.rationale,
        conf,
        unique_keep_order([p for e in evidence[:2] for p in e.people]),
        unique_keep_order([d for e in evidence[:2] for d in e.dates]),
    )


def generate_historical_answer(
    question: str, evidence: list[Evidence], llm: LLMProvider | None
) -> tuple[str, str, list[str], list[str], str]:
    if not evidence:
        # Skip LLM call entirely when zero evidence is retrieved
        return (
            "I could not find enough evidence in the indexed repository history to answer this reliably.",
            "low",
            [],
            [],
            "no_evidence",
        )

    if llm is None:
        return (*_fallback_historical(evidence), "fallback")

    valid_ids = {e.decision_id for e in evidence if e.decision_id}

    evidence_text = "\n\n".join(
        f"EVIDENCE ID: {e.decision_id}\nSOURCE: {e.source_url}\nSUMMARY: {e.summary}\nRATIONALE: {e.rationale}\n"
        f"SNIPPET: {e.evidence_snippet}\nSCORE: {e.score:.3f}"
        for e in evidence[:3]
    )

    try:
        raw = llm.generate(
            SYSTEM_HISTORICAL,
            f"QUESTION: {question}\n\nEVIDENCE:\n{evidence_text}",
        ).strip()
        parsed = parse_json_object(raw)

        raw_claims = parsed.get("claims")
        if not isinstance(raw_claims, list) and parsed.get("answer"):
            raw_claims = [{"statement": parsed["answer"], "evidence_id": parsed.get("evidence_id", "")}]

        accepted, rejected = filter_and_ground_claims(raw_claims or [], valid_ids)

        if accepted:
            answer = " ".join(c.statement for c in accepted)
            ratio = len(accepted) / max(len(raw_claims or []), 1)
            confidence = compute_deterministic_confidence(evidence, channels_count=1, verified_ratio=ratio)
        else:
            # Drop uncited or wrongly cited claims; fallback to verified ground-truth rationale
            answer = evidence[0].rationale
            confidence = "low"

        people = unique_keep_order([p for e in evidence[:2] for p in e.people])
        dates = unique_keep_order([d for e in evidence[:2] for d in e.dates])
        return answer, confidence, people, dates, "llm"
    except Exception as exc:
        print(f"Historical answer generation fallback: {exc}")
        return (*_fallback_historical(evidence), "fallback")


def generate_repository_answer(
    question: str,
    modules: list[KeyModule],
    flow: list[ArchitectureStep],
    relevant_files: list[str],
    evidence: list[Evidence],
    llm: LLMProvider | None,
) -> dict[str, Any]:
    # Construct context from verified modules and flow
    module_text = "\n".join([f"- {m.name} ({m.file}): {m.role} — {m.description}" for m in modules[:6]])
    flow_text = "\n".join([f"{idx+1}. {s.title} [{s.component} in {s.file_path}]: {s.description}" for idx, s in enumerate(flow)])
    evidence_text = "\n".join([f"- PR/Decision: {e.summary} ({e.rationale})" for e in evidence[:2]]) if evidence else "None"

    user_prompt = f"""QUESTION: {question}

VERIFIED REPOSITORY MODULES:
{module_text}

REQUEST / EXECUTION FLOW:
{flow_text}

INDEXED REPOSITORY FILES:
{', '.join(relevant_files[:10])}

RELATED HISTORICAL DECISIONS:
{evidence_text}"""

    if llm is None:
        return {
            "overview": "Flask is structured as a compact WSGI kernel (flask/app.py) surrounded by modular subsystems for context management, routing, and extensions.",
            "answer": "Incoming HTTP requests enter through Flask.wsgi_app in flask/app.py, bind RequestContext in flask/ctx.py, and are matched against the URL map before calling the resolved view function.",
            "confidence": "medium",
            "mode": "fallback",
        }

    try:
        raw = llm.generate(SYSTEM_REPOSITORY, user_prompt).strip()
        parsed = parse_json_object(raw)
        return {
            "overview": str(parsed.get("overview", "")).strip(),
            "answer": str(parsed.get("answer", "")).strip(),
            "confidence": str(parsed.get("confidence", "high")),
            "mode": "llm",
        }
    except Exception as exc:
        print(f"Repository answer generation fallback: {exc}")
        return {
            "overview": "Flask is organized around a central WSGI application class with specialized modules for context isolation, blueprints, and request dispatching.",
            "answer": "Requests enter through `Flask.wsgi_app(environ, start_response)` in `flask/app.py`, activate thread-local proxies in `flask/ctx.py`, and resolve endpoints through Werkzeug's routing map.",
            "confidence": "medium",
            "mode": "fallback",
        }


def generate_general_answer(
    question: str,
    concept_data: dict[str, Any] | None,
    relevant_files: list[str],
    llm: LLMProvider | None,
) -> dict[str, Any]:
    context_hint = ""
    if concept_data:
        context_hint = f"""VERIFIED PALLETS/FLASK CONTEXT:
- Concept: {concept_data.get('concept')}
- How it works: {concept_data.get('how_it_works')}
- In this repository: {concept_data.get('in_repository')}
- Relevant repository files: {', '.join(concept_data.get('relevant_files', []))}"""

    user_prompt = f"""QUESTION: {question}

{context_hint}

RELEVANT REPOSITORY FILES: {', '.join(relevant_files[:6])}"""

    if llm is None:
        if concept_data:
            return {
                "concept": concept_data.get("concept", ""),
                "how_it_works": concept_data.get("how_it_works", ""),
                "in_repository": concept_data.get("in_repository", ""),
                "answer": f"{concept_data.get('concept')} {concept_data.get('in_repository')}",
                "confidence": "high",
                "mode": "fallback",
            }
        return {
            "concept": "General technical concept.",
            "how_it_works": "",
            "in_repository": "",
            "answer": "This is a general software engineering concept.",
            "confidence": "medium",
            "mode": "fallback",
        }

    try:
        raw = llm.generate(SYSTEM_GENERAL, user_prompt).strip()
        parsed = parse_json_object(raw)
        return {
            "concept": str(parsed.get("concept", "")).strip(),
            "how_it_works": str(parsed.get("how_it_works", "")).strip(),
            "in_repository": str(parsed.get("in_repository", "")).strip(),
            "answer": str(parsed.get("answer", "")).strip(),
            "confidence": "high",
            "mode": "llm",
        }
    except Exception as exc:
        print(f"General answer generation fallback: {exc}")
        if concept_data:
            return {
                "concept": concept_data.get("concept", ""),
                "how_it_works": concept_data.get("how_it_works", ""),
                "in_repository": concept_data.get("in_repository", ""),
                "answer": f"{concept_data.get('concept')} {concept_data.get('in_repository')}",
                "confidence": "medium",
                "mode": "fallback",
            }
        return {
            "concept": "",
            "how_it_works": "",
            "in_repository": "",
            "answer": "Technical concept explanation.",
            "confidence": "low",
            "mode": "fallback",
        }


def generate_hybrid_answer(
    question: str,
    evidence: list[Evidence],
    modules: list[KeyModule],
    concept_data: dict[str, Any] | None,
    llm: LLMProvider | None,
) -> dict[str, Any]:
    if not evidence:
        return {
            "answer": "No historical decision evidence found in the indexed repository history for this question.",
            "overview": "Flask integrates WSGI and context management across its core architecture.",
            "confidence": "low",
            "people": [],
            "dates": [],
            "mode": "no_evidence",
        }

    valid_ids = {e.decision_id for e in evidence if e.decision_id}

    if llm is None:
        ans, conf, people, dates = _fallback_historical(evidence)
        return {
            "answer": ans,
            "overview": "Flask integrates WSGI and context management across its core architecture.",
            "confidence": conf,
            "people": people,
            "dates": dates,
            "mode": "fallback",
        }

    evidence_text = "\n\n".join(
        f"EVIDENCE ID: {e.decision_id}\nSOURCE: {e.source_url}\nSUMMARY: {e.summary}\nRATIONALE: {e.rationale}\nSNIPPET: {e.evidence_snippet}"
        for e in evidence[:2]
    )

    module_text = ", ".join([f"{m.name} ({m.file})" for m in modules[:4]])

    user_prompt = f"""QUESTION: {question}

CODEBASE ARCHITECTURE:
Modules: {module_text}
Concept Context: {concept_data.get('in_repository', '') if concept_data else 'Standard Flask architecture'}

HISTORICAL EVIDENCE / DECISION RATIONALE:
{evidence_text}"""

    try:
        raw = llm.generate(SYSTEM_HYBRID, user_prompt).strip()
        parsed = parse_json_object(raw)
        raw_claims = parsed.get("claims")
        if not isinstance(raw_claims, list) and parsed.get("answer"):
            raw_claims = [{"statement": parsed["answer"], "evidence_id": parsed.get("evidence_id", "")}]

        accepted, rejected = filter_and_ground_claims(raw_claims or [], valid_ids)

        if accepted:
            answer = " ".join(c.statement for c in accepted)
            ratio = len(accepted) / max(len(raw_claims or []), 1)
            confidence = compute_deterministic_confidence(evidence, channels_count=1, verified_ratio=ratio)
        else:
            answer = evidence[0].rationale
            confidence = "low"

        people = unique_keep_order([p for e in evidence[:2] for p in e.people])
        dates = unique_keep_order([d for e in evidence[:2] for d in e.dates])
        return {
            "answer": answer,
            "overview": str(parsed.get("overview", "")).strip(),
            "confidence": confidence,
            "people": people,
            "dates": dates,
            "mode": "llm",
        }
    except Exception as exc:
        print(f"Hybrid answer generation fallback: {exc}")
        ans, conf, people, dates = _fallback_historical(evidence)
        return {
            "answer": ans,
            "overview": "Architectural integration and historical rationale in pallets/flask.",
            "confidence": conf,
            "people": people,
            "dates": dates,
            "mode": "fallback",
        }
