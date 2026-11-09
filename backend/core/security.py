import hashlib
import hmac
import time
from collections import defaultdict, deque

from fastapi import HTTPException

from core.config import FILE_SIGNING_SECRET, SIGNED_URL_TTL_S


def _sig(kind: str, obj_id: str, exp: int) -> str:
    msg = f"{kind}:{obj_id}:{exp}".encode()
    return hmac.new(FILE_SIGNING_SECRET.encode(), msg, hashlib.sha256).hexdigest()[:40]


def signed_url(kind: str, obj_id: str, download: bool = False, ttl: int = SIGNED_URL_TTL_S) -> str:
    """Relative, time-limited URL for a stored file (kind: upload | gen | zip)."""
    exp = int(time.time()) + ttl
    url = f"/api/files/{kind}/{obj_id}?exp={exp}&sig={_sig(kind, obj_id, exp)}"
    return url + "&download=1" if download else url


def verify_signature(kind: str, obj_id: str, exp: int, sig: str) -> None:
    if exp < time.time() or not hmac.compare_digest(_sig(kind, obj_id, exp), sig):
        raise HTTPException(status_code=403, detail="Link expired or invalid")


class RateLimiter:
    """In-memory sliding window per user; swap for Redis when running multiple workers."""

    def __init__(self, limit: int, window_s: int):
        self.limit, self.window = limit, window_s
        self.hits: dict[str, deque] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.time()
        q = self.hits[key]
        while q and q[0] < now - self.window:
            q.popleft()
        if len(q) >= self.limit:
            raise HTTPException(status_code=429, detail="Too many requests, please slow down")
        q.append(now)


upload_limiter = RateLimiter(30, 60)
job_limiter = RateLimiter(12, 60)
