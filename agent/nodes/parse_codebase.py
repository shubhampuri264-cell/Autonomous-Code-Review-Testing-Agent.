"""Run tree-sitter AST parsing on all source files."""

from agent.state import AgentState
from parsing.analyzer import analyze_codebase


async def parse_codebase(state: AgentState) -> dict:
    """Parse all source files and build AST map with file summaries."""
    ast_map, file_summaries = await analyze_codebase(
        local_path=state["local_path"],
        file_list=state["file_list"],
        languages=state.get("languages", ["python"]),
    )
    return {"ast_map": ast_map, "file_summaries": file_summaries}
