"""CRUD operations for repositories table."""

from db.client import get_supabase_client


async def get_repository(repo_id: str) -> dict | None:
    result = get_supabase_client().table("repositories").select("*").eq("id", repo_id).single().execute()
    return result.data


async def list_user_repositories(user_id: str) -> list[dict]:
    result = get_supabase_client().table("repositories").select("*").eq("user_id", user_id).execute()
    return result.data


async def create_repository(data: dict) -> dict:
    result = get_supabase_client().table("repositories").insert(data).execute()
    return result.data[0]


async def delete_repository(repo_id: str, user_id: str):
    get_supabase_client().table("repositories").delete().eq("id", repo_id).eq("user_id", user_id).execute()
