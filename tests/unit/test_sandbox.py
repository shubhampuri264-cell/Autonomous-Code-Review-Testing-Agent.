"""Unit tests for sandbox backend dispatch and command building (no Docker)."""

import pytest

from sandbox.backends.local import (
    _build_command,
    _is_timeout,
    _source_suffix,
)
from sandbox.executor import run_tests_in_sandbox
from core.exceptions import SandboxError


class TestBuildCommand:
    def test_python_command_has_coverage_and_test_target(self):
        cmd, env = _build_command("python", "calc")
        assert "test_calc.py" in cmd
        assert "--cov=calc" in cmd
        assert "-p" in cmd and "no:cacheprovider" in cmd
        assert env["PYTHONPATH"] == "/workspace"
        assert env["COVERAGE_FILE"].startswith("/tmp")

    def test_js_command_uses_jest(self):
        cmd, env = _build_command("javascript", "calc")
        assert cmd[0:2] == ["npx", "jest"]
        assert "test_calc.js" in cmd
        assert env["NODE_PATH"] == "/workspace"


class TestHelpers:
    def test_source_suffix(self):
        assert _source_suffix("python") == ".py"
        assert _source_suffix("javascript") == ".js"
        assert _source_suffix("typescript") == ".js"

    def test_is_timeout_detects_read_timeout(self):
        assert _is_timeout(Exception("HTTPConnectionPool: Read timed out."))
        assert not _is_timeout(Exception("connection refused"))


class TestDispatch:
    async def test_fargate_backend_fails_closed(self, monkeypatch):
        monkeypatch.setattr("core.config.settings.sandbox_backend", "fargate")
        with pytest.raises(SandboxError, match="not provisioned"):
            await run_tests_in_sandbox("x.py", "test", "python")

    async def test_unknown_backend_rejected(self, monkeypatch):
        monkeypatch.setattr("core.config.settings.sandbox_backend", "bogus")
        with pytest.raises(SandboxError, match="Unknown sandbox backend"):
            await run_tests_in_sandbox("x.py", "test", "python")
