"""Prompt templates for test patching."""

from pathlib import Path


def build_patch_prompt(
    test_content: str,
    diagnosis: dict,
    source_file: str,
    local_path: str,
) -> str:
    """Build the LLM prompt for patching failing tests."""

    # Read the source file for context
    source_code = ""
    try:
        source_code = (Path(local_path) / source_file).read_text(encoding="utf-8")
    except FileNotFoundError:
        pass

    return f"""You are an expert test engineer. Fix the failing test file based on the diagnosis below.

## Original Test File
```
{test_content}
```

## Source Code Being Tested
```
{source_code}
```

## Diagnosis
- Error type: {diagnosis.get('error_type', 'unknown')}
- Root cause: {diagnosis.get('root_cause', 'unknown')}
- Suggested fix: {diagnosis.get('suggested_fix', 'unknown')}

## Instructions
- Fix ONLY the failing parts — do not rewrite tests that already pass
- Ensure imports are correct
- Ensure assertions match actual function behavior
- Return ONLY the complete fixed test file code, no explanations
"""
