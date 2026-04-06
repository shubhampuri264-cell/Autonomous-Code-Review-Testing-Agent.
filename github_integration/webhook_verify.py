"""GitHub webhook HMAC-SHA256 signature verification."""

import hashlib
import hmac


def verify_webhook_signature(
    payload: bytes,
    signature: str | None,
    secret: str | None,
) -> bool:
    """Verify GitHub webhook payload signature."""
    if not signature or not secret:
        return False

    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
