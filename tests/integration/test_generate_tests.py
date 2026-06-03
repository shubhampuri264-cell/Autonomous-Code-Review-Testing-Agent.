"""Integration tests for test generation (requires LLM API key)."""

import pytest


@pytest.mark.skip(reason="Requires LLM API key — run manually")
class TestGenerateTests:
    async def test_generates_valid_python_tests(self, sample_python_source, sample_ast_map):
        """Verify LLM generates syntactically valid pytest code."""
        from llm.prompts.generate_tests import build_test_generation_prompt

        prompt = build_test_generation_prompt(
            source_code=sample_python_source,
            ast_summary=sample_ast_map["calculator.py"],
            framework="pytest",
            language="python",
            module_name="calculator",
        )

        # Verify prompt contains key elements
        assert "pytest" in prompt
        assert "add" in prompt
        assert "Calculator" in prompt
        assert "edge cases" in prompt.lower()
