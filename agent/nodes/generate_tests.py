"""LLM-powered test file generation."""

from pathlib import Path

from agent.state import AgentState
from agent.metering import account_usage
from llm.client import get_llm_client
from llm.parsers import extract_code
from llm.prompts.generate_tests import build_test_generation_prompt
from core.constants import TEST_FRAMEWORKS


async def generate_tests(state: AgentState) -> dict:
    """Generate test files for each target using LLM with AST context."""
    llm = get_llm_client()
    generated_tests = {}
    responses = []

    for target_file in state["target_files"]:
        # Read source file content
        source_code = (Path(state["local_path"]) / target_file).read_text(
            encoding="utf-8"
        )

        # Get AST summary for this file
        ast_data = state["ast_map"].get(target_file, {})

        # Detect language and framework
        language = ast_data.get("language", "python")
        framework = TEST_FRAMEWORKS.get(language, "pytest")

        # Build prompt with source code + AST context. The sandbox mounts the
        # source as `<stem>.py`, so the test must import it by that stem.
        prompt = build_test_generation_prompt(
            source_code=source_code,
            ast_summary=ast_data,
            framework=framework,
            language=language,
            module_name=Path(target_file).stem,
        )

        # Generate test via LLM and strip any markdown fences
        response = await llm.generate(prompt)
        responses.append(response)
        generated_tests[target_file] = extract_code(response.text)

    return {
        "generated_tests": generated_tests,
        "iterations": 0,
        **account_usage(state, *responses),
    }
