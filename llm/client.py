"""Unified async LLM client over Gemini, Claude, and Bedrock providers.

Calls are non-blocking (run in a worker thread), throttled by a process-wide
rate limiter, retried with exponential backoff, and metered for token usage and
estimated cost so a run can enforce a hard token budget.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import settings

# Approximate USD pricing per 1M tokens as (input, output). Used only for the
# cost meter; treat values as estimates, not billing-accurate figures.
_PRICING: dict[str, tuple[float, float]] = {
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-2.5-flash": (0.30, 2.50),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-opus-4-8": (5.00, 25.00),
}
_DEFAULT_PRICING = (0.0, 0.0)


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate USD cost for a call from the per-model pricing table."""
    in_price, out_price = _PRICING.get(model, _DEFAULT_PRICING)
    return (input_tokens * in_price + output_tokens * out_price) / 1_000_000


@dataclass
class LLMResponse:
    """Generated text plus token/cost accounting for a single call."""

    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class TokenBudgetExceeded(RuntimeError):
    """Raised when a run exceeds its configured token budget (kill switch)."""


def enforce_token_budget(total_tokens: int) -> None:
    """Fail closed when accumulated run tokens exceed the configured budget."""
    budget = settings.token_budget_per_run
    if budget and total_tokens > budget:
        raise TokenBudgetExceeded(
            f"Run exceeded token budget: {total_tokens} > {budget} tokens"
        )


class _RateLimiter:
    """Process-wide async throttle enforcing a minimum interval between calls."""

    def __init__(self, min_interval: float):
        self._min_interval = min_interval
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def wait(self) -> None:
        async with self._lock:
            delay = self._min_interval - (time.monotonic() - self._last)
            if delay > 0:
                await asyncio.sleep(delay)
            self._last = time.monotonic()


class LLMClient:
    """Async LLM client; delegates to the configured provider."""

    def __init__(self, provider: str):
        self.provider = provider
        self._rate_limiter = _RateLimiter(settings.llm_min_request_interval)

        if provider == "gemini":
            import google.generativeai as genai

            genai.configure(api_key=settings.gemini_api_key)
            self.model = settings.gemini_model
            self._model = genai.GenerativeModel(self.model)
        elif provider == "anthropic":
            import anthropic

            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_model
        elif provider == "bedrock":
            import anthropic

            self._client = anthropic.AnthropicBedrock(aws_region=settings.aws_region)
            self.model = settings.bedrock_model
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def generate(self, prompt: str) -> LLMResponse:
        """Generate text with rate-limiting, retries, and usage metering."""
        await self._rate_limiter.wait()
        return await self._generate_with_retry(prompt)

    @retry(
        stop=stop_after_attempt(settings.llm_max_retries),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        reraise=True,
    )
    async def _generate_with_retry(self, prompt: str) -> LLMResponse:
        if self.provider == "gemini":
            return await asyncio.to_thread(self._gemini_call, prompt)
        return await asyncio.to_thread(self._anthropic_call, prompt)

    def _gemini_call(self, prompt: str) -> LLMResponse:
        response = self._model.generate_content(prompt)
        usage = getattr(response, "usage_metadata", None)
        in_tok = int(getattr(usage, "prompt_token_count", 0) or 0)
        out_tok = int(getattr(usage, "candidates_token_count", 0) or 0)
        return self._build_response(response.text, in_tok, out_tok)

    def _anthropic_call(self, prompt: str) -> LLMResponse:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        usage = getattr(response, "usage", None)
        in_tok = int(getattr(usage, "input_tokens", 0) or 0)
        out_tok = int(getattr(usage, "output_tokens", 0) or 0)
        return self._build_response(response.content[0].text, in_tok, out_tok)

    def _build_response(self, text: str, in_tok: int, out_tok: int) -> LLMResponse:
        return LLMResponse(
            text=text,
            input_tokens=in_tok,
            output_tokens=out_tok,
            cost_usd=estimate_cost(self.model, in_tok, out_tok),
        )


_clients: dict[str, LLMClient] = {}


def get_llm_client() -> LLMClient:
    """Return a cached LLM client for the configured provider.

    Caching keeps the rate limiter's state shared across nodes in a run.
    """
    provider = settings.llm_provider
    if provider not in _clients:
        _clients[provider] = LLMClient(provider)
    return _clients[provider]
