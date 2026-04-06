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


def extract_code(text: str, language: str = "") -> str:
    """Extract code from LLM response, stripping markdown fences."""
    # Remove markdown code fences if present
    pattern = rf"```(?:{language})?\s*\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()
