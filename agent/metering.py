"""Per-run token/cost accounting for LLM-calling nodes."""

from agent.state import AgentState
from llm.client import LLMResponse, enforce_token_budget


def account_usage(state: AgentState, *responses: LLMResponse) -> dict:
    """Sum usage from LLM responses, enforce the run budget, return state deltas.

    ``tokens_used``/``cost_usd`` use additive reducers on ``AgentState``, so each
    node returns only its own delta and LangGraph accumulates the run total. The
    budget kill switch is checked against the projected running total.
    """
    delta_tokens = sum(r.total_tokens for r in responses)
    delta_cost = sum(r.cost_usd for r in responses)
    running_total = state.get("tokens_used", 0) + delta_tokens
    enforce_token_budget(running_total)
    return {"tokens_used": delta_tokens, "cost_usd": delta_cost}
