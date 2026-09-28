"""Fetch the high-value GitHub history linked from the golden WHY dataset."""
from __future__ import annotations

from pathlib import Path

from app.config import GOLDEN_FILE, RAW_DIR, ensure_data_dirs, get_settings
from app.github_client import GitHubClient
from app.utils import read_json, write_json


def _cache(path: Path, producer):
    if path.exists():
        return read_json(path)
    value = producer()
    write_json(path, value)
    return value


def ingest_golden() -> None:
    settings = get_settings()
    if not settings.github_token:
        raise RuntimeError("GITHUB_TOKEN missing in .env")

    ensure_data_dirs()
    golden = read_json(GOLDEN_FILE)
    client = GitHubClient(settings.github_token, settings.github_repo)

    issue_numbers = sorted({int(x["issue"]) for x in golden if x.get("issue")})
    pr_numbers = sorted({int(x["pr"]) for x in golden if x.get("pr")})
    commits = sorted({x["commit"] for x in golden if x.get("commit")})

    issues = _cache(RAW_DIR / "issues.json", lambda: [client.issue(n) for n in issue_numbers])
    prs = _cache(RAW_DIR / "prs.json", lambda: [client.pull_request(n) for n in pr_numbers])
    commit_rows = _cache(RAW_DIR / "commits.json", lambda: [client.commit(sha) for sha in commits])

    write_json(RAW_DIR / "repo_meta.json", {
        "repo": settings.github_repo,
        "api_remaining": client.remaining_requests(),
    })

    print(f"Ingested/cached: {len(issues)} issues, {len(prs)} PRs, {len(commit_rows)} commits")


if __name__ == "__main__":
    ingest_golden()
