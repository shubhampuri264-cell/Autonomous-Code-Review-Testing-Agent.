"""Prompt templates for failure diagnosis."""


def build_diagnosis_prompt(
    failures: list[dict],
    generated_tests: dict[str, str],
    local_path: str,
) -> str:
    """Build the LLM prompt for diagnosing test failures."""

    failure_details = ""
    for f in failures:
        failure_details += f"""
### {f.get('source_file', 'unknown')}
- Test: {f.get('test_name', 'unknown')}
- Error: {f.get('error_message', 'no message')}
- Traceback: {f.get('traceback', 'none')}
"""

    return f"""You are an expert test debugger. Analyze the following test failures and provide a structured diagnosis.

## Failures
{failure_details}

## Instructions
For each failing test, provide:
1. **error_type**: The category of error (import_error, assertion_error, type_error, etc.)
2. **root_cause**: Why the test failed (1-2 sentences)
3. **suggested_fix**: Specific code change to fix the test

Return your response as valid JSON with the source file as the key:
{{
  "file_path": {{
    "error_type": "...",
    "root_cause": "...",
    "suggested_fix": "..."
  }}
}}
"""
