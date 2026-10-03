"""Create provenance-rich Decision records from the golden WHY dataset.

Default mode is curated: the golden dataset is treated as verified ground truth.
Set EXTRACTION_MODE=llm only when you want Ollama to rewrite/structure additional
historical text; the original source and curated rationale remain preserved.
"""
from __future__ import annotations

from typing import Any

from app.config import GOLDEN_FILE, NORMALIZED_DIR, PROCESSED_DIR, ensure_data_dirs, get_settings
from app.grounding import verify_evidence_snippets
from app.providers import LLMProvider, make_llm, parse_json_object
from app.utils import read_json, unique_keep_order, write_json


def extract_decision_from_source(
    llm: LLMProvider,
    source_type: str,
    source_id: str | int,
    source_text: str,
    initial_confidence: str = "high",
) -> dict[str, Any] | None:
    """Extract a decision using LLM and strictly verify snippets verbatim against source text.

    - Rejects decisions with zero verifiable snippets.
    - Downgrades confidence if only some snippets verify.
    """
    prompt = (
        "Extract the technical decision and rationale from this source text.\n"
        "Return JSON with keys:\n"
        "- summary: short description of the decision\n"
        "- rationale: explanation of why the choice was made\n"
        "- evidence_snippets: list of exact verbatim quote strings copied directly from the text\n"
        f"SOURCE TEXT:\n{source_text[:3000]}"
    )
    raw = llm.generate("You are an evidence-grounded technical decision extractor.", prompt)
    parsed = parse_json_object(raw)
    snippets = parsed.get("evidence_snippets") or []
    if isinstance(snippets, str):
        snippets = [snippets]

    verified_snippets, final_conf, ratio = verify_evidence_snippets(snippets, source_text, initial_confidence)
    if not verified_snippets or final_conf == "rejected":
        # Discard any decision that has zero verifiable snippets
        return None

    return {
        "summary": str(parsed.get("summary", "")),
        "rationale": str(parsed.get("rationale", "")),
        "evidence_snippets": verified_snippets,
        "confidence": final_conf,
        "verification_ratio": ratio,
    }


def _source(item: dict) -> tuple[str, int | str | None, str | None]:
    if item.get("pr"):
        url = next((u for u in item.get("urls", []) if "/pull/" in u), None)
        return "github_pr", item["pr"], url
    if item.get("issue"):
        url = next((u for u in item.get("urls", []) if "/issues/" in u), None)
        return "github_issue", item["issue"], url
    if item.get("commit"):
        url = next((u for u in item.get("urls", []) if "/commit/" in u), None)
        return "github_commit", item["commit"], url
    return "unknown", None, None


def _source_meta(item: dict, prs: dict, issues: dict, commits: dict) -> tuple[list[str], list[str]]:
    people: list[str] = []
    dates: list[str] = []
    if item.get("pr") and item["pr"] in prs:
        row = prs[item["pr"]]
        if row.get("author_login"):
            people.append(row["author_login"])
        date = row.get("merged_at") or row.get("created_at")
        if date:
            dates.append(date[:10])
    if item.get("issue") and item["issue"] in issues:
        row = issues[item["issue"]]
        if row.get("author_login"):
            people.append(row["author_login"])
        if row.get("created_at"):
            dates.append(row["created_at"][:10])
    if item.get("commit") and item["commit"] in commits:
        row = commits[item["commit"]]
        if row.get("author_login"):
            people.append(row["author_login"])
        if row.get("date"):
            dates.append(row["date"][:10])
    if item.get("date"):
        dates.append(item["date"])
    return unique_keep_order(people), unique_keep_order(dates)


def _llm_refine(llm, question: str, rationale: str) -> tuple[str, str, str]:
    prompt = (
        "Return JSON with keys summary, rationale, tradeoffs. Use ONLY the supplied text. "
        "Do not add facts. Keep it concise.\n\n"
        f"QUESTION: {question}\nRATIONALE: {rationale}"
    )
    raw = llm.generate("You are a conservative historical code-decision extractor.", prompt)
    parsed = parse_json_object(raw)
    return (
        str(parsed.get("summary") or question),
        str(parsed.get("rationale") or rationale),
        str(parsed.get("tradeoffs") or ""),
    )


def extract() -> None:
    ensure_data_dirs()
    settings = get_settings()
    golden = read_json(GOLDEN_FILE)
    prs = {int(x["number"]): x for x in read_json(NORMALIZED_DIR / "prs.json")} if (NORMALIZED_DIR / "prs.json").exists() else {}
    issues = {int(x["number"]): x for x in read_json(NORMALIZED_DIR / "issues.json")} if (NORMALIZED_DIR / "issues.json").exists() else {}
    commits = {x["sha"]: x for x in read_json(NORMALIZED_DIR / "commits.json")} if (NORMALIZED_DIR / "commits.json").exists() else {}

    llm = None
    if settings.extraction_mode == "llm":
        llm = make_llm(settings)

    decisions = []
    for item in golden:
        source_type, source_id, source_url = _source(item)
        people, dates = _source_meta(item, prs, issues, commits)
        summary = item["question"]
        rationale = item.get("reason", "")
        tradeoffs = ""

        if llm is not None and rationale:
            try:
                summary, rationale, tradeoffs = _llm_refine(llm, summary, rationale)
            except Exception as exc:
                print(f"LLM extraction skipped for {item['id']}: {exc}")

        decisions.append({
            "id": f"golden-{item['id']}",
            "summary": summary,
            "rationale": rationale,
            "tradeoffs": tradeoffs,
            "confidence": item.get("confidence", "low"),
            "source_type": source_type,
            "source_id": source_id,
            "source_url": source_url,
            "evidence_snippet": rationale,
            "people": people,
            "dates": dates,
            "golden_id": item["id"],
        })

    write_json(PROCESSED_DIR / "extracted_decisions.json", decisions)
    print(f"Extracted decisions: {len(decisions)}")


if __name__ == "__main__":
    extract()
