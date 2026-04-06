"""Pydantic schemas for repositories."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RepoCreate(BaseModel):
    github_url: str
    default_branch: Optional[str] = "main"
    coverage_threshold: Optional[int] = 80
    languages: Optional[list[str]] = None


class RepoResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    github_url: str
    default_branch: str
    coverage_threshold: int
    languages: Optional[list[str]] = None
    created_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
