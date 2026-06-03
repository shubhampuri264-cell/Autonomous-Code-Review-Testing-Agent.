"""LLM-powered failure diagnosis."""

from agent.state import AgentState
from agent.metering import account_usage
from llm.client import get_llm_client
from llm.parsers import extract_json
from llm.prompts.diagnose_failures import build_diagnosis_prompt


async def diagnose_failures(state: AgentState) -> dict:
    """Analyze failure messages and propose fixes via LLM."""
    llm = get_llm_client()
    failures = state.get("failures", [])

    # Build diagnosis prompt with failure output + source code
    prompt = build_diagnosis_prompt(
        failures=failures,
        generated_tests=state["generated_tests"],
        local_path=state["local_path"],
    )

    # Diagnosis is JSON keyed by source file (consumed by patch_tests)
    response = await llm.generate(prompt)
    diagnosis = extract_json(response.text)

    return {"diagnosis": diagnosis, **account_usage(state, response)}
