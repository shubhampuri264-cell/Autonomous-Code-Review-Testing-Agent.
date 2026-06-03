"""Docker sandbox executor — run tests in isolated containers."""

import docker
import tempfile
import os

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
    """Execute tests in a fresh Docker container and return output.

    Container constraints:
    - No network access
    - 512MB memory limit
    - 1 CPU core
    - 60 second timeout
    - Destroyed immediately after execution
    """
    client = docker.from_env()
    image = DOCKER_IMAGES.get(language, "agent-sandbox-python")

    # Write test content to temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=_test_suffix(language), delete=False
    ) as f:
        f.write(test_content)
        test_path = f.name

    try:
        # Determine test command
        if language == "python":
            cmd = "python -m pytest /workspace/test_file.py -v --tb=short --json-report --json-report-file=/workspace/results.json"
        else:
            cmd = "npx jest /workspace/test_file.js --json --outputFile=/workspace/results.json"

        container = client.containers.run(
            image=image,
            command=cmd,
            volumes={
                os.path.dirname(source_path): {"bind": "/workspace/src", "mode": "ro"},
                test_path: {"bind": f"/workspace/test_file{_test_suffix(language)}", "mode": "ro"},
            },
            mem_limit=settings.sandbox_memory_limit,
            cpu_quota=int(settings.sandbox_cpu_limit * 100000),
            network_disabled=True,
            security_opt=["no-new-privileges"],
            read_only=True,
            tmpfs={"/tmp": "size=64M"},
            detach=True,
        )

        # Block until the container finishes or the timeout fires
        container.wait(timeout=SANDBOX_TIMEOUT_SECONDS)
        output = container.logs().decode("utf-8")

        # Cleanup
        container.remove(force=True)

        return output

    except docker.errors.ContainerError as e:
        raise SandboxError(f"Container error: {e}")
    except Exception as e:
        if "timed out" in str(e).lower():
            raise SandboxTimeoutError(f"Container timed out after {SANDBOX_TIMEOUT_SECONDS}s")
        raise SandboxError(f"Sandbox error: {e}")
    finally:
        os.unlink(test_path)


def _test_suffix(language: str) -> str:
    return ".py" if language == "python" else ".js"
