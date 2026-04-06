"""CRUD operations for runs table."""

from typing import Optional
from db.client import get_supabase_client


async def create_run(data: dict) -> dict:
    result = get_supabase_client().table("runs").insert(data).execute()
    return result.data[0]


async def get_run(run_id: str) -> dict | None:
    result = get_supabase_client().table("runs").select("*").eq("id", run_id).single().execute()
    return result.data


async def update_run(
    run_id: str,
    status: str,
    coverage_after: Optional[float] = None,
    iterations: Optional[int] = None,
    pr_url: Optional[str] = None,
    error_message: Optional[str] = None,
):
    update_data = {"status": status}
    if coverage_after is not None:
        update_data["coverage_after"] = coverage_after
    if iterations is not None:
        update_data["iterations"] = iterations
    if pr_url:
        update_data["pr_url"] = pr_url
    if error_message:
        update_data["error_message"] = error_message

    get_supabase_client().table("runs").update(update_data).eq("id", run_id).execute()


async def list_runs_for_repo(repo_id: str) -> list[dict]:
    result = (
        get_supabase_client()
        .table("runs")
        .select("*")
        .eq("repository_id", repo_id)
        .order("started_at", desc=True)
        .execute()
    )
    return result.data
