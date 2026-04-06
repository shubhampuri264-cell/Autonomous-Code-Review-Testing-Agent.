"""Pydantic schemas for runs."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RunTriggerRequest(BaseModel):
    repository_id: str
    branch: Optional[str] = None
    coverage_threshold: Optional[int] = None
    max_iterations: Optional[int] = None
    languages: Optional[list[str]] = None


class RunResponse(BaseModel):
    id: str
    repository_id: Optional[str] = None
    status: str
    trigger: Optional[str] = None
    coverage_before: Optional[float] = None
    coverage_after: Optional[float] = None
    iterations: Optional[int] = None
    pr_url: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
