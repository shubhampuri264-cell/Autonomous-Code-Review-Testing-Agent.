"""Apply LLM-generated patches to failing tests."""

from agent.state import AgentState
from llm.client import get_llm_client
from llm.prompts.patch_tests import build_patch_prompt


async def patch_tests(state: AgentState) -> dict:
    """Apply diagnosis-informed patches to test files."""
    llm = get_llm_client()
    diagnosis = state.get("diagnosis", {})
    generated_tests = dict(state["generated_tests"])

    # For each failing test file, generate a patched version
    for source_file, test_content in generated_tests.items():
        file_diagnosis = diagnosis.get(source_file)
        if not file_diagnosis:
            continue

        prompt = build_patch_prompt(
            test_content=test_content,
            diagnosis=file_diagnosis,
            source_file=source_file,
            local_path=state["local_path"],
        )

        patched = await llm.generate(prompt)
        generated_tests[source_file] = patched

    return {"generated_tests": generated_tests}
