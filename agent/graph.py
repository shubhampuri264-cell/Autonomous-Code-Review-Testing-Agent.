"""LangGraph workflow definition — the core agent state machine."""

from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes.clone_repo import clone_repo
from agent.nodes.parse_codebase import parse_codebase
from agent.nodes.select_targets import select_targets
from agent.nodes.generate_tests import generate_tests
from agent.nodes.execute_tests import execute_tests
from agent.nodes.evaluate_results import evaluate_results
from agent.nodes.diagnose_failures import diagnose_failures
from agent.nodes.patch_tests import patch_tests
from agent.nodes.open_pr import open_pr
from agent.nodes.save_results import save_results


def should_retry(state: AgentState) -> str:
    """Decide whether to retry, open PR, or fail."""
    if state.get("status") == "success":
        return "open_pr"
    if state.get("iterations", 0) >= state.get("max_iterations", 3):
        return "save_results"
    return "diagnose_failures"


def build_graph() -> StateGraph:
    """Construct the agent workflow graph."""

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("clone_repo", clone_repo)
    graph.add_node("parse_codebase", parse_codebase)
    graph.add_node("select_targets", select_targets)
    graph.add_node("generate_tests", generate_tests)
    graph.add_node("execute_tests", execute_tests)
    graph.add_node("evaluate_results", evaluate_results)
    graph.add_node("diagnose_failures", diagnose_failures)
    graph.add_node("patch_tests", patch_tests)
    graph.add_node("open_pr", open_pr)
    graph.add_node("save_results", save_results)

    # Define edges — linear flow with a retry loop
    graph.set_entry_point("clone_repo")
    graph.add_edge("clone_repo", "parse_codebase")
    graph.add_edge("parse_codebase", "select_targets")
    graph.add_edge("select_targets", "generate_tests")
    graph.add_edge("generate_tests", "execute_tests")
    graph.add_edge("execute_tests", "evaluate_results")

    # Conditional: retry loop or proceed
    graph.add_conditional_edges(
        "evaluate_results",
        should_retry,
        {
            "open_pr": "open_pr",
            "diagnose_failures": "diagnose_failures",
            "save_results": "save_results",
        },
    )

    graph.add_edge("diagnose_failures", "patch_tests")
    graph.add_edge("patch_tests", "execute_tests")
    graph.add_edge("open_pr", "save_results")
    graph.add_edge("save_results", END)

    return graph


# Compiled graph ready for invocation
agent_workflow = build_graph().compile()
