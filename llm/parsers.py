"""Parse structured LLM responses."""

import json
import re


def extract_json(text: str) -> dict:
    """Extract JSON from LLM response text, handling markdown fences."""
    # Try to find JSON in code fences
    match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        text = match.group(1)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def extract_code(text: str) -> str:
    """Extract code from an LLM response, stripping any markdown fence.

    Handles fences with or without a language tag (```python, ```py, ```), and
    falls back to the stripped text when no fence is present.
    """
    match = re.search(r"```[\w.+-]*[ \t]*\r?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()
