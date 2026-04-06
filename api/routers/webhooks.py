"""GitHub webhook handler."""

from fastapi import APIRouter, Request, HTTPException

from github_integration.webhook_verify import verify_webhook_signature
from core.config import settings

router = APIRouter()


@router.post("/github")
async def github_webhook(request: Request):
    """Receive GitHub push/PR webhook events."""
    # Verify HMAC signature
    signature = request.headers.get("X-Hub-Signature-256")
    body = await request.body()

    if not verify_webhook_signature(body, signature, settings.github_webhook_secret):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")

    if event_type == "push":
        # TODO: trigger agent run for push events
        pass
    elif event_type == "pull_request":
        # TODO: handle PR events
        pass

    return {"status": "received"}
