"""Evidence-only answer synthesis with a robust local-model fallback."""
from __future__ import annotations

from app.models import Evidence
from app.providers import LLMProvider, parse_json_object
from app.utils import unique_keep_order


SYSTEM = """You answer WHY-code questions using ONLY the supplied evidence.
Never invent historical facts, people, dates, motivations, or sources.
Prefer the highest-scoring evidence. Ignore unrelated evidence.
Return concise JSON with keys: answer, confidence.
The answer should explain the decision and the main rationale/trade-off in 1-3 sentences."""


def _fallback(evidence: list[Evidence]) -> tuple[str, str, list[str], list[str]]:
    if not evidence:
        return (
            "I could not find enough evidence in the indexed repository history to answer this reliably.",
            "low",
            [],
            [],
        )
    top = evidence[0]
    return (
        top.rationale,
        top.confidence if top.score > 0 else "low",
        unique_keep_order([p for e in evidence[:2] for p in e.people]),
        unique_keep_order([d for e in evidence[:2] for d in e.dates]),
    )


def _clean_plain_text(raw: str) -> str:
    text = raw.strip()
    lowered = text.lower()
    if "answer:" in lowered:
        start = lowered.find("answer:") + len("answer:")
        end = lowered.find("confidence:", start)
        if end == -1:
            end = len(text)
        text = text[start:end].strip()
    return text


def generate_answer(question: str, evidence: list[Evidence], llm: LLMProvider | None):
    if not evidence:
        return (*_fallback(evidence), "fallback")
    if llm is None:
        return (*_fallback(evidence), "fallback")

    # Only pass the strongest relevant items to the LLM.
    evidence_text = "\n\n".join(
        f"SOURCE: {e.source_url}\nSUMMARY: {e.summary}\nRATIONALE: {e.rationale}\n"
        f"EVIDENCE: {e.evidence_snippet}\nSCORE: {e.score:.3f}"
        for e in evidence[:3]
    )
    try:
        raw = llm.generate(
            SYSTEM,
            f"QUESTION: {question}\n\nEVIDENCE:\n{evidence_text}",
        ).strip()

        try:
            parsed = parse_json_object(raw)
            answer = str(parsed.get("answer") or evidence[0].rationale).strip()
            confidence = str(parsed.get("confidence") or evidence[0].confidence)
        except Exception:
            answer = _clean_plain_text(raw) or evidence[0].rationale
            confidence = evidence[0].confidence

        people = unique_keep_order([p for e in evidence[:2] for p in e.people])
        dates = unique_keep_order([d for e in evidence[:2] for d in e.dates])
        return answer, confidence, people, dates, "llm"
    except Exception as exc:
        print(f"Answer generation fallback: {exc}")
        return (*_fallback(evidence), "fallback")
