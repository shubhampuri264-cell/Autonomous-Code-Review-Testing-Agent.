"""Unified LLM client abstraction over Gemini and Claude APIs."""

from core.config import settings


class LLMClient:
    """Abstract LLM client — delegates to configured provider."""

    def __init__(self, provider: str):
        self.provider = provider

        if provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            self._model = genai.GenerativeModel("gemini-2.0-flash")
        elif provider == "anthropic":
            import anthropic
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def generate(self, prompt: str) -> str:
        """Generate text from prompt."""
        if self.provider == "gemini":
            response = self._model.generate_content(prompt)
            return response.text
        elif self.provider == "anthropic":
            response = self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text


def get_llm_client() -> LLMClient:
    """Get configured LLM client instance."""
    return LLMClient(provider=settings.llm_provider)
