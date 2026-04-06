"""Clone target repository to a temp directory."""

from agent.state import AgentState
from github_integration.cloner import clone_repository


async def clone_repo(state: AgentState) -> dict:
    """Clone the target repo and return the local path + file list."""
    local_path, file_list = await clone_repository(
        repo_url=state["repo_url"],
        branch=state.get("branch", "main"),
    )
    return {"local_path": local_path, "file_list": file_list}
