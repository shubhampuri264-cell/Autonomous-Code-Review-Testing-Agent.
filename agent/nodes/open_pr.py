"""Create GitHub PR with passing test suite."""

from agent.state import AgentState
from github_integration.pr_creator import create_test_pr


async def open_pr(state: AgentState) -> dict:
    """Create branch, commit test files, and open a GitHub pull request."""
    pr_url = await create_test_pr(
        repo_url=state["repo_url"],
        branch=state.get("branch", "main"),
        run_id=state.get("run_id", "unknown"),
        generated_tests=state["generated_tests"],
        test_results=state.get("test_results", []),
        coverage_pct=state.get("coverage_pct", 0.0),
    )
    return {"pr_url": pr_url}
