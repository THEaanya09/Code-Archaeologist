"""GitHub API wrapper with a small, stable surface for ingestion."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from github import Auth, Github


class GitHubClient:
    def __init__(self, token: str, repo_name: str) -> None:
        self.github = Github(auth=Auth.Token(token), per_page=100)
        self.repo = self.github.get_repo(repo_name)

    @staticmethod
    def _dt(value: datetime | None) -> str | None:
        return value.isoformat() if value else None

    def issue(self, number: int) -> dict[str, Any]:
        issue = self.repo.get_issue(number)
        comments = []
        for comment in issue.get_comments():
            comments.append({
                "author_login": getattr(comment.user, "login", None),
                "body": comment.body or "",
                "created_at": self._dt(comment.created_at),
                "url": comment.html_url,
            })
        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body or "",
            "state": issue.state,
            "created_at": self._dt(issue.created_at),
            "closed_at": self._dt(issue.closed_at),
            "author_login": getattr(issue.user, "login", None),
            "url": issue.html_url,
            "comments": comments,
        }

    def pull_request(self, number: int) -> dict[str, Any]:
        pr = self.repo.get_pull(number)
        comments = []
        for comment in pr.get_issue_comments():
            comments.append({
                "author_login": getattr(comment.user, "login", None),
                "body": comment.body or "",
                "created_at": self._dt(comment.created_at),
                "url": comment.html_url,
            })
        return {
            "number": pr.number,
            "title": pr.title,
            "body": pr.body or "",
            "state": pr.state,
            "created_at": self._dt(pr.created_at),
            "merged_at": self._dt(pr.merged_at),
            "author_login": getattr(pr.user, "login", None),
            "merge_commit_sha": pr.merge_commit_sha,
            "url": pr.html_url,
            "comments": comments,
        }

    def commit(self, sha: str) -> dict[str, Any]:
        commit = self.repo.get_commit(sha)
        files = []
        for file in commit.files:
            files.append({
                "path": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
            })
        return {
            "sha": commit.sha,
            "message": commit.commit.message,
            "date": self._dt(commit.commit.author.date if commit.commit.author else None),
            "author_login": getattr(commit.author, "login", None),
            "url": commit.html_url,
            "files": files,
        }

    def remaining_requests(self) -> int:
        return self.github.get_rate_limit().resources.core.remaining
