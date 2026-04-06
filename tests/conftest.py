"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_python_source():
    """Sample Python source code for testing."""
    return '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


class Calculator:
    def __init__(self):
        self.history = []

    def compute(self, op: str, a: float, b: float) -> float:
        if op == "add":
            result = a + b
        elif op == "subtract":
            result = a - b
        elif op == "multiply":
            result = a * b
        elif op == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            result = a / b
        else:
            raise ValueError(f"Unknown operation: {op}")
        self.history.append((op, a, b, result))
        return result
'''


@pytest.fixture
def sample_ast_map():
    """Sample AST map for testing."""
    return {
        "calculator.py": {
            "functions": [
                {"name": "add", "start_line": 1, "end_line": 3},
                {"name": "divide", "start_line": 6, "end_line": 9},
            ],
            "classes": [
                {"name": "Calculator", "start_line": 12, "end_line": 30},
            ],
            "imports": [],
            "node_count": 85,
            "language": "python",
        }
    }
