"""Select files to test based on complexity and coverage gaps."""

from agent.state import AgentState


async def select_targets(state: AgentState) -> dict:
    """Rank files by AST node count and select targets for test generation."""
    ast_map = state["ast_map"]

    # Score each file by complexity (number of AST nodes)
    scored = []
    for file_path, ast_data in ast_map.items():
        complexity = ast_data.get("node_count", 0)
        function_count = len(ast_data.get("functions", []))
        class_count = len(ast_data.get("classes", []))
        score = complexity + (function_count * 10) + (class_count * 15)
        scored.append((file_path, score))

    # Sort by score descending, select top files
    scored.sort(key=lambda x: x[1], reverse=True)
    target_files = [f for f, _ in scored if _ > 0]

    return {"target_files": target_files}
