"""Local Docker sandbox backend — run tests in isolated containers.

A run mounts a single read-only work directory at /workspace containing the
source module (`<stem>.py`) and the generated test (`test_<stem>.py`), so the
test can import the module by its stem. Coverage/cache writes go to a tmpfs at
/tmp. The container has no network, tight CPU/memory limits, a hard timeout, and
is always force-removed afterwards.
"""

import os
import shutil
import tempfile
from pathlib import Path

import docker

from core.config import settings
from core.constants import SANDBOX_TIMEOUT_SECONDS
from core.exceptions import SandboxError, SandboxTimeoutError


DOCKER_IMAGES = {
    "python": "agent-sandbox-python",
    "javascript": "agent-sandbox-node",
    "typescript": "agent-sandbox-node",
}


async def run_tests_in_sandbox(
    source_path: str,
    test_content: str,
    language: str,
) -> str:
    """Execute tests in a fresh Docker container and return the raw output.

    Container constraints: no network, 512MB memory, 1 CPU, 60s timeout,
    read-only root fs (writable tmpfs at /tmp), destroyed after execution.
    """
    client = docker.from_env()
    image = DOCKER_IMAGES.get(language, "agent-sandbox-python")
    stem = Path(source_path).stem
    suffix = _source_suffix(language)

    # Stage source + test into one read-only work dir mounted at /workspace.
    work_dir = tempfile.mkdtemp(prefix="agent-sandbox-")
    shutil.copyfile(source_path, os.path.join(work_dir, f"{stem}{suffix}"))
    Path(work_dir, f"test_{stem}{suffix}").write_text(test_content, encoding="utf-8")

    command, environment = _build_command(language, stem)

    container = None
    try:
        container = client.containers.run(
            image=image,
            command=command,
            environment=environment,
            working_dir="/workspace",
            volumes={os.path.abspath(work_dir): {"bind": "/workspace", "mode": "ro"}},
            mem_limit=settings.sandbox_memory_limit,
            cpu_quota=int(settings.sandbox_cpu_limit * 100000),
            network_disabled=True,
            security_opt=["no-new-privileges"],
            read_only=True,
            tmpfs={"/tmp": "size=64M"},
            detach=True,
        )

        try:
            container.wait(timeout=SANDBOX_TIMEOUT_SECONDS)
        except Exception as e:  # classify: timeout vs. real error
            if _is_timeout(e):
                container.kill()
                raise SandboxTimeoutError(
                    f"Container timed out after {SANDBOX_TIMEOUT_SECONDS}s"
                ) from e
            raise SandboxError(f"Sandbox wait failed: {e}") from e

        return container.logs().decode("utf-8", errors="ignore")

    except docker.errors.ContainerError as e:
        raise SandboxError(f"Container error: {e}") from e
    finally:
        if container is not None:
            try:
                container.remove(force=True)
            except docker.errors.APIError:
                pass
        shutil.rmtree(work_dir, ignore_errors=True)


def _build_command(language: str, stem: str) -> tuple[list[str], dict]:
    """Return the test command + environment for the given language."""
    if language == "python":
        command = [
            "python", "-m", "pytest", f"test_{stem}.py",
            "-v", "-ra", "--tb=short",
            f"--cov={stem}", "--cov-report=term-missing",
            "-p", "no:cacheprovider",
        ]
        environment = {
            "PYTHONPATH": "/workspace",
            "PYTHONDONTWRITEBYTECODE": "1",
            "COVERAGE_FILE": "/tmp/.coverage",
        }
    else:
        command = [
            "npx", "jest", f"test_{stem}.js",
            "--coverage", "--json", "--outputFile=/tmp/results.json",
            "--coverageDirectory=/tmp/coverage",
        ]
        environment = {"NODE_PATH": "/workspace"}
    return command, environment


def _is_timeout(exc: Exception) -> bool:
    """Detect a docker `wait` read-timeout (vs. a genuine error)."""
    return "timed out" in str(exc).lower()


def _source_suffix(language: str) -> str:
    return ".py" if language == "python" else ".js"
