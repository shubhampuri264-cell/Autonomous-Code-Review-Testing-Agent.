"""Prompt templates for test generation."""


def build_test_generation_prompt(
    source_code: str,
    ast_summary: dict,
    framework: str,
    language: str,
) -> str:
    """Build the LLM prompt for generating test files."""

    functions = ast_summary.get("functions", [])
    classes = ast_summary.get("classes", [])
    func_names = ", ".join(f["name"] for f in functions) or "none"
    class_names = ", ".join(c["name"] for c in classes) or "none"

    return f"""You are an expert test engineer. Generate a comprehensive test file for the following {language} source code.

## Source Code
```{language}
{source_code}
```

## Code Structure (from AST analysis)
- Functions: {func_names}
- Classes: {class_names}
- Total AST nodes: {ast_summary.get('node_count', 0)}

## Requirements
- Use {framework} as the test framework
- Test all public functions and class methods
- Include edge cases: empty inputs, boundary values, error conditions
- Include at least one happy path and one unhappy path per function
- Tests must be self-contained — no external dependencies or network calls
- Use descriptive test names that explain what is being tested
- Import the source module correctly based on the file structure

## Output
Return ONLY the test file code, no explanations or markdown fences.
"""
