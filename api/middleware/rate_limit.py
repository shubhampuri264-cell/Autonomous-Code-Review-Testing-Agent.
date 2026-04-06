"""Rate limiting middleware — max 5 concurrent runs per user."""

from collections import defaultdict
import asyncio


class RateLimiter:
    """Track concurrent runs per user."""

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self._active: dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    async def acquire(self, user_id: str) -> bool:
        async with self._lock:
            if self._active[user_id] >= self.max_concurrent:
                return False
            self._active[user_id] += 1
            return True

    async def release(self, user_id: str):
        async with self._lock:
            self._active[user_id] = max(0, self._active[user_id] - 1)


rate_limiter = RateLimiter()
