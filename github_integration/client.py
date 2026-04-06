"""PyGitHub wrapper for repository operations."""

from github import Github
from core.config import settings


def get_github_client() -> Github:
    """Get authenticated GitHub client."""
    return Github(settings.github_token)


def get_repo(repo_url: str):
    """Get a GitHub repository object from URL."""
    g = get_github_client()
    # Extract owner/repo from URL
    # Handles: https://github.com/owner/repo or owner/repo
    parts = repo_url.rstrip("/").split("/")
    repo_name = f"{parts[-2]}/{parts[-1]}"
    return g.get_repo(repo_name)
