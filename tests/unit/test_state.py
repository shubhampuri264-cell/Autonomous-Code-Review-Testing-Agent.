"""Unit tests for agent state."""

from agent.state import AgentState


def test_agent_state_creation():
    state: AgentState = {
        "repo_url": "https://github.com/test/repo",
        "branch": "main",
        "iterations": 0,
        "max_iterations": 3,
        "coverage_threshold": 80,
        "status": "pending",
    }
    assert state["repo_url"] == "https://github.com/test/repo"
    assert state["iterations"] == 0
