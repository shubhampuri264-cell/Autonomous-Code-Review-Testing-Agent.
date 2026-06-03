"""Unit tests for LLM parsing, cost metering, and budget enforcement."""

import pytest

from agent.metering import account_usage
from llm.client import (
    LLMClient,
    LLMResponse,
    TokenBudgetExceeded,
    enforce_token_budget,
    estimate_cost,
)
from llm.parsers import extract_code, extract_json


class TestExtractCode:
    def test_strips_language_fence(self):
        text = "```python\nassert add(1, 2) == 3\n```"
        assert extract_code(text) == "assert add(1, 2) == 3"

    def test_strips_bare_fence(self):
        text = "```\nx = 1\n```"
        assert extract_code(text) == "x = 1"

    def test_strips_short_language_tag(self):
        text = "Here you go:\n```py\nx = 1\n```"
        assert extract_code(text) == "x = 1"

    def test_returns_stripped_text_when_no_fence(self):
        assert extract_code("  no fences here  ") == "no fences here"

    def test_keeps_inner_blank_lines(self):
        text = "```python\na = 1\n\nb = 2\n```"
        assert extract_code(text) == "a = 1\n\nb = 2"


class TestExtractJson:
    def test_parses_fenced_json(self):
        text = '```json\n{"error_type": "import_error"}\n```'
        assert extract_json(text) == {"error_type": "import_error"}

    def test_parses_bare_json(self):
        assert extract_json('{"a": 1}') == {"a": 1}

    def test_returns_empty_on_invalid(self):
        assert extract_json("not json at all") == {}


class TestCostMeter:
    def test_total_tokens(self):
        assert LLMResponse("x", input_tokens=10, output_tokens=5).total_tokens == 15

    def test_estimate_cost_known_model(self):
        # gemini-2.0-flash priced at (0.10, 0.40) per 1M tokens
        cost = estimate_cost("gemini-2.0-flash", 1_000_000, 1_000_000)
        assert cost == pytest.approx(0.50)

    def test_estimate_cost_unknown_model_is_zero(self):
        assert estimate_cost("mystery-model", 1000, 1000) == 0.0


class TestTokenBudget:
    def test_under_budget_passes(self, monkeypatch):
        monkeypatch.setattr("llm.client.settings.token_budget_per_run", 1000)
        enforce_token_budget(999)  # no raise

    def test_over_budget_raises(self, monkeypatch):
        monkeypatch.setattr("llm.client.settings.token_budget_per_run", 1000)
        with pytest.raises(TokenBudgetExceeded):
            enforce_token_budget(1001)

    def test_zero_budget_disables_kill_switch(self, monkeypatch):
        monkeypatch.setattr("llm.client.settings.token_budget_per_run", 0)
        enforce_token_budget(10_000_000)  # no raise


class TestAccountUsage:
    def test_sums_deltas(self, monkeypatch):
        monkeypatch.setattr("llm.client.settings.token_budget_per_run", 0)
        r1 = LLMResponse("a", input_tokens=10, output_tokens=5, cost_usd=0.001)
        r2 = LLMResponse("b", input_tokens=20, output_tokens=10, cost_usd=0.002)
        out = account_usage({"tokens_used": 100}, r1, r2)
        assert out == {"tokens_used": 45, "cost_usd": pytest.approx(0.003)}

    def test_enforces_running_total(self, monkeypatch):
        monkeypatch.setattr("llm.client.settings.token_budget_per_run", 120)
        r = LLMResponse("a", input_tokens=15, output_tokens=10)
        with pytest.raises(TokenBudgetExceeded):
            account_usage({"tokens_used": 100}, r)  # 100 + 25 > 120


class TestClientProvider:
    def test_unsupported_provider_raises(self):
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            LLMClient("does-not-exist")
