"""LangGraph agent state schema."""

import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict, total=False):
    """State passed between LangGraph nodes."""

    # Repository context
    repo_url: str
    branch: str
    local_path: str
    file_list: list[str]

    # AST analysis
    ast_map: dict
    file_summaries: dict

    # Target selection
    target_files: list[str]
    coverage_config: dict

    # Test generation
    generated_tests: dict[str, str]  # source_file -> test_content

    # Execution results
    test_results: list[dict]
    failures: list[dict]
    coverage_pct: float

    # Self-correction
    iterations: int
    max_iterations: int
    coverage_threshold: int

    # Diagnosis
    diagnosis: dict
    patch_plan: dict

    # Cost meter (accumulated across LLM-calling nodes)
    tokens_used: Annotated[int, operator.add]
    cost_usd: Annotated[float, operator.add]

    # Output
    pr_url: str
    run_id: str
    status: str
    error_message: str

    # Language config
    languages: list[str]
