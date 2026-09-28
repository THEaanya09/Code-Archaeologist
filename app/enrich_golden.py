import json
import os

from dotenv import load_dotenv
from github import Github, Auth

load_dotenv(".env")

TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN missing in .env")

REPO_NAME = "pallets/flask"
INPUT_FILE = "data/golden_questions.json"

g = Github(auth=Auth.Token(TOKEN))
repo = g.get_repo(REPO_NAME)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    pr_number = item.get("pr")
    issue_number = item.get("issue")

    # PR available -> get merge commit + merged date
    if pr_number:
        try:
            pr = repo.get_pull(pr_number)

            if pr.merged:
                item["commit"] = pr.merge_commit_sha
                item["date"] = pr.merged_at.date().isoformat()
            elif not item.get("date") and pr.created_at:
                item["date"] = pr.created_at.date().isoformat()

        except Exception as e:
            print(f"PR {pr_number} failed: {e}")

    # Issue-only entries -> use issue creation date
    elif issue_number:
        try:
            issue = repo.get_issue(issue_number)

            if not item.get("date") and issue.created_at:
                item["date"] = issue.created_at.date().isoformat()

        except Exception as e:
            print(f"Issue {issue_number} failed: {e}")

with open(INPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Enrichment complete.")
print("Questions:", len(data))
print("Missing commit:", sum(x.get("commit") is None for x in data))
print("Missing date:", sum(x.get("date") is None for x in data))