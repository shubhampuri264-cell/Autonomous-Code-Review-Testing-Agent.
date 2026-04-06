"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check — no auth required."""
    return {"status": "healthy", "service": "autonomous-code-review-agent"}
