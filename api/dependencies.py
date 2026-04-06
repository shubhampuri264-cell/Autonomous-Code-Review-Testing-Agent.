"""FastAPI dependency injection."""

from fastapi import Depends, HTTPException, Header
from typing import Optional

from db.client import get_supabase_client
from core.config import settings


async def get_db():
    """Provide Supabase client instance."""
    return get_supabase_client()


async def verify_auth(authorization: Optional[str] = Header(None)):
    """Verify JWT token from Supabase Auth."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")
    client = get_supabase_client()

    try:
        user = client.auth.get_user(token)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
