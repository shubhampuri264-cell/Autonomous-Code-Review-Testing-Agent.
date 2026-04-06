"""Repository management endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import verify_auth, get_db
from api.schemas.repositories import RepoCreate, RepoResponse

router = APIRouter()


@router.get("/", response_model=list[RepoResponse])
async def list_repositories(user=Depends(verify_auth), db=Depends(get_db)):
    """List all connected repositories for user."""
    result = (
        db.table("repositories")
        .select("*")
        .eq("user_id", user.id)
        .execute()
    )
    return result.data


@router.post("/", response_model=RepoResponse)
async def connect_repository(
    repo: RepoCreate, user=Depends(verify_auth), db=Depends(get_db)
):
    """Connect a new GitHub repository."""
    data = {
        "user_id": user.id,
        "github_url": repo.github_url,
        "default_branch": repo.default_branch or "main",
        "coverage_threshold": repo.coverage_threshold or 80,
        "languages": repo.languages or [],
    }
    result = db.table("repositories").insert(data).execute()
    return result.data[0]


@router.delete("/{repo_id}")
async def disconnect_repository(
    repo_id: str, user=Depends(verify_auth), db=Depends(get_db)
):
    """Disconnect a repository."""
    db.table("repositories").delete().eq("id", repo_id).eq("user_id", user.id).execute()
    return {"detail": "Repository disconnected"}
