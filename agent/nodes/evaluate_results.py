"""Evaluate test results against coverage threshold."""

from agent.state import AgentState
from core.constants import RunStatus


async def evaluate_results(state: AgentState) -> dict:
    """Check if coverage threshold is met or max retries reached."""
    test_results = state.get("test_results", [])
    threshold = state.get("coverage_threshold", 80)
    iterations = state.get("iterations", 0) + 1
    failures = state.get("failures", [])

    # Calculate aggregate coverage
    total_coverage = 0.0
    if test_results:
        total_coverage = sum(r.get("coverage_pct", 0) for r in test_results) / len(
            test_results
        )

    # Decide outcome
    if not failures and total_coverage >= threshold:
        status = RunStatus.SUCCESS
    elif iterations >= state.get("max_iterations", 3):
        status = RunStatus.FAILED
    else:
        status = RunStatus.RUNNING  # will trigger retry

    return {
        "coverage_pct": total_coverage,
        "iterations": iterations,
        "status": status,
    }
