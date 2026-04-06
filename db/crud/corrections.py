"""CRUD operations for corrections table."""

from uuid import uuid4
from db.client import get_supabase_client


async def create_correction_records(
    test_file_id: str,
    iteration: int,
    failure_summary: str,
    patch_applied: str,
    result: str,
):
    """Insert a correction record."""
    client = get_supabase_client()
    client.table("corrections").insert({
        "id": str(uuid4()),
        "test_file_id": test_file_id,
        "iteration": iteration,
        "failure_summary": failure_summary,
        "patch_applied": patch_applied,
        "result": result,
    }).execute()
