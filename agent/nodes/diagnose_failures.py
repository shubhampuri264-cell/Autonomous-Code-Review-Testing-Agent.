"""LLM-powered failure diagnosis."""

from agent.state import AgentState
from llm.client import get_llm_client
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

    # Get structured diagnosis from LLM
    response = await llm.generate(prompt)

    return {"diagnosis": response}
