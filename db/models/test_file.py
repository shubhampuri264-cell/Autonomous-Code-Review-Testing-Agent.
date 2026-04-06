"""TestFile model."""

from pydantic import BaseModel
from typing import Optional


class TestFile(BaseModel):
    id: str
    run_id: str
    source_file: str
    test_file_path: str
    test_content: str
    tests_passed: int = 0
    tests_failed: int = 0
    coverage_pct: float = 0.0
