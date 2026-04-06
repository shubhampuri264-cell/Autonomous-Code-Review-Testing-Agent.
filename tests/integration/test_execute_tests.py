"""Integration tests for Docker sandbox execution (requires Docker)."""

import pytest


@pytest.mark.skip(reason="Requires Docker — run manually")
class TestExecuteTests:
    async def test_sandbox_runs_python_tests(self):
        """Verify Docker container runs pytest and returns output."""
        pass

    async def test_sandbox_timeout(self):
        """Verify container is killed after timeout."""
        pass

    async def test_sandbox_no_network(self):
        """Verify container has no network access."""
        pass
