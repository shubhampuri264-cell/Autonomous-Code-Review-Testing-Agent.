"""Run model."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Run(BaseModel):
    id: str
    repository_id: str
    status: str = "pending"
    trigger: str = "manual"
    coverage_before: Optional[float] = None
    coverage_after: Optional[float] = None
    iterations: int = 0
    pr_url: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
