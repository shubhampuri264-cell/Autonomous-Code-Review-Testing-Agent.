"""Run management endpoints."""

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from uuid import uuid4

from api.dependencies import verify_auth, get_db
from api.schemas.runs import RunTriggerRequest, RunResponse
from core.constants import RunStatus, TriggerType

router = APIRouter()


@router.post("/trigger", response_model=RunResponse)
async def trigger_run(
    request: RunTriggerRequest,
    background_tasks: BackgroundTasks,
    user=Depends(verify_auth),
    db=Depends(get_db),
):
    """Trigger a new agent run for a repository."""
    from agent.graph import agent_workflow

    run_id = str(uuid4())

    # Create run record
    run_data = {
        "id": run_id,
        "repository_id": request.repository_id,
        "status": RunStatus.PENDING,
        "trigger": TriggerType.MANUAL,
        "iterations": 0,
    }
    db.table("runs").insert(run_data).execute()

    # Launch agent in background
    background_tasks.add_task(
        agent_workflow.ainvoke,
        {
            "repo_url": request.repository_id,  # Resolved from repo record
            "branch": request.branch or "main",
            "coverage_threshold": request.coverage_threshold or 80,
            "max_iterations": request.max_iterations or 3,
            "run_id": run_id,
        },
    )

    return RunResponse(id=run_id, status=RunStatus.PENDING)


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: str, user=Depends(verify_auth), db=Depends(get_db)):
    """Get status and details of a specific run."""
    result = db.table("runs").select("*").eq("id", run_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Run not found")
    return result.data


@router.get("/")
async def list_runs(repo_id: str, user=Depends(verify_auth), db=Depends(get_db)):
    """List all runs for a repository."""
    result = (
        db.table("runs")
        .select("*")
        .eq("repository_id", repo_id)
        .order("started_at", desc=True)
        .execute()
    )
    return result.data
