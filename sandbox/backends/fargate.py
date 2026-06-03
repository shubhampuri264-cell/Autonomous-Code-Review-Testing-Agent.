"""Fargate (ECS) sandbox backend — ephemeral, $0-safe, opt-in.

Not provisioned yet: selecting ``SANDBOX_BACKEND=fargate`` fails closed until the
AWS resources exist (ECR sandbox image, ECS task def, public-subnet/no-NAT
networking, IAM). See the roadmap Phase 3 / Phase 8 AWS sections. This module
makes no AWS calls — provisioning is gated behind explicit approval per the $0
cost posture.
"""

from core.exceptions import SandboxError


async def run_tests_in_sandbox(
    source_path: str,
    test_content: str,
    language: str,
) -> str:
    """Placeholder until the Fargate backend is provisioned (fails closed)."""
    raise SandboxError(
        "Fargate sandbox backend is not provisioned. Use SANDBOX_BACKEND=local, or "
        "provision ECR/ECS/IAM first (requires AWS approval per the $0 cost posture)."
    )
