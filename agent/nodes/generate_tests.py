"""LLM-powered test file generation."""

from agent.state import AgentState
from llm.client import get_llm_client
from llm.prompts.generate_tests import build_test_generation_prompt
from core.constants import TEST_FRAMEWORKS


async def generate_tests(state: AgentState) -> dict:
    """Generate test files for each target using LLM with AST context."""
    llm = get_llm_client()
    generated_tests = {}

    for target_file in state["target_files"]:
        # Read source file content
        file_path = f"{state['local_path']}/{target_file}"
        with open(file_path, "r") as f:
            source_code = f.read()

        # Get AST summary for this file
        ast_data = state["ast_map"].get(target_file, {})

        # Detect language and framework
        language = ast_data.get("language", "python")
        framework = TEST_FRAMEWORKS.get(language, "pytest")

        # Build prompt with source code + AST context
        prompt = build_test_generation_prompt(
            source_code=source_code,
            ast_summary=ast_data,
            framework=framework,
            language=language,
        )

        # Generate test via LLM
        response = await llm.generate(prompt)
        generated_tests[target_file] = response

    return {"generated_tests": generated_tests, "iterations": 0}
