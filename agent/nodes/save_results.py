"""Persist run metadata to Supabase."""

from agent.state import AgentState
from db.crud.runs import update_run
from db.crud.test_files import create_test_file_records


async def save_results(state: AgentState) -> dict:
    """Save run summary, test files, and corrections to database."""
    run_id = state.get("run_id")

    # Update run record
    await update_run(
        run_id=run_id,
        status=state.get("status", "failed"),
        coverage_after=state.get("coverage_pct", 0.0),
        iterations=state.get("iterations", 0),
        pr_url=state.get("pr_url"),
        error_message=state.get("error_message"),
    )

    # Save generated test files
    await create_test_file_records(
        run_id=run_id,
        generated_tests=state.get("generated_tests", {}),
        test_results=state.get("test_results", []),
    )

    return {"run_id": run_id}
