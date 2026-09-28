"""Normalize cached GitHub payloads into simple graph-ready records."""
from __future__ import annotations

from app.config import NORMALIZED_DIR, RAW_DIR, ensure_data_dirs
from app.utils import read_json, unique_keep_order, write_json


def normalize() -> None:
    ensure_data_dirs()

    issues = read_json(RAW_DIR / "issues.json")
    prs = read_json(RAW_DIR / "prs.json")
    commits = read_json(RAW_DIR / "commits.json")

    people: list[str] = []
    files: list[dict] = []

    for issue in issues:
        if issue.get("author_login"):
            people.append(issue["author_login"])
        people.extend(c.get("author_login") for c in issue.get("comments", []))

    for pr in prs:
        if pr.get("author_login"):
            people.append(pr["author_login"])
        people.extend(c.get("author_login") for c in pr.get("comments", []))

    for commit in commits:
        if commit.get("author_login"):
            people.append(commit["author_login"])
        files.extend(commit.get("files", []))

    normalized_people = [{"login": p} for p in unique_keep_order([x for x in people if x])]
    unique_files = {}
    for item in files:
        unique_files[item["path"]] = item

    write_json(NORMALIZED_DIR / "issues.json", issues)
    write_json(NORMALIZED_DIR / "prs.json", prs)
    write_json(NORMALIZED_DIR / "commits.json", commits)
    write_json(NORMALIZED_DIR / "people.json", normalized_people)
    write_json(NORMALIZED_DIR / "files.json", list(unique_files.values()))

    print(
        f"Normalized: {len(unique_files)} files, {len(normalized_people)} people, "
        f"{len(issues)} issues, {len(prs)} PRs, {len(commits)} commits"
    )


if __name__ == "__main__":
    normalize()
