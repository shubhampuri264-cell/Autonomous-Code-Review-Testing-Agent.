"""Execute generated tests in Docker sandbox."""

from agent.state import AgentState
from sandbox.executor import run_tests_in_sandbox
from sandbox.result_parser import parse_test_output


async def execute_tests(state: AgentState) -> dict:
    """Spin up Docker container, run tests, capture results."""
    test_results = []
    failures = []

    for source_file, test_content in state["generated_tests"].items():
        ast_data = state["ast_map"].get(source_file, {})
        language = ast_data.get("language", "python")

        # Run in isolated container
        raw_output = await run_tests_in_sandbox(
            source_path=f"{state['local_path']}/{source_file}",
            test_content=test_content,
            language=language,
        )

        # Parse structured output
        result = parse_test_output(raw_output, language)
        result["source_file"] = source_file
        test_results.append(result)

        if result.get("failures"):
            failures.extend(
                [{"source_file": source_file, **f} for f in result["failures"]]
            )

    return {"test_results": test_results, "failures": failures}
