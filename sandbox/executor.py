"""Sandbox executor dispatcher — selects the configured execution backend.

Backends:
- ``local``   (default, $0): ephemeral Docker container on the host
- ``fargate`` (opt-in, AWS): ephemeral ECS task (not provisioned until AWS is set up)

Local stays the default for $0 dev; Fargate is gated behind config + AWS approval.
The public ``run_tests_in_sandbox`` signature is backend-agnostic.
"""

from core.config import settings
from core.exceptions import SandboxError


async def run_tests_in_sandbox(
    source_path: str,
    test_content: str,
    language: str,
) -> str:
    """Run tests via the configured sandbox backend and return raw output."""
    backend = settings.sandbox_backend
    if backend == "local":
        from sandbox.backends.local import run_tests_in_sandbox as _run
    elif backend == "fargate":
        from sandbox.backends.fargate import run_tests_in_sandbox as _run
    else:
        raise SandboxError(f"Unknown sandbox backend: {backend!r}")
    return await _run(source_path, test_content, language)
