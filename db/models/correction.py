"""Correction model."""

from pydantic import BaseModel


class Correction(BaseModel):
    id: str
    test_file_id: str
    iteration: int
    failure_summary: str
    patch_applied: str
    result: str  # resolved | unresolved | partial
