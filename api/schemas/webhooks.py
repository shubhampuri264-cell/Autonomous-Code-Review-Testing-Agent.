"""Pydantic schemas for GitHub webhook payloads."""

from pydantic import BaseModel
from typing import Optional


class GitHubWebhookPayload(BaseModel):
    action: Optional[str] = None
    ref: Optional[str] = None
    repository: Optional[dict] = None
    sender: Optional[dict] = None
