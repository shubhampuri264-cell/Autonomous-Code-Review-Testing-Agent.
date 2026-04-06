"""Repository model."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Repository(BaseModel):
    id: str
    user_id: str
    github_url: str
    default_branch: str = "main"
    coverage_threshold: int = 80
    languages: list[str] = []
    created_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
