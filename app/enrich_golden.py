"""Backfill missing dates and available PR merge SHAs from GitHub."""
from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from github import Auth, Github

from app.config import ROOT_DIR

load_dotenv(ROOT_DIR / ".env")

REPO_NAME = os.getenv("GITHUB_REPO", "pallets/flask")
INPUT_FILE = ROOT_DIR / "data" / "golden_questions.json"


def enrich() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN missing in .env")

    client = Github(auth=Auth.Token(token), per_page=100)
    repo = client.get_repo(REPO_NAME)

    with INPUT_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    for item in data:
        pr_number = item.get("pr")
        issue_number = item.get("issue")

        if pr_number:
            try:
                pr = repo.get_pull(int(pr_number))
                if pr.merged:
                    item["commit"] = pr.merge_commit_sha
                    if pr.merged_at:
                        item["date"] = pr.merged_at.date().isoformat()
                elif not item.get("date") and pr.created_at:
                    item["date"] = pr.created_at.date().isoformat()
            except Exception as exc:
                print(f"PR {pr_number} failed: {exc}")
        elif issue_number:
            try:
                issue = repo.get_issue(int(issue_number))
                if not item.get("date") and issue.created_at:
                    item["date"] = issue.created_at.date().isoformat()
            except Exception as exc:
                print(f"Issue {issue_number} failed: {exc}")

    with INPUT_FILE.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)

    print("Enrichment complete.")
    print("Questions:", len(data))
    print("Missing commit:", sum(x.get("commit") is None for x in data))
    print("Missing date:", sum(x.get("date") is None for x in data))


if __name__ == "__main__":
    enrich()
