import logging
import os

import requests
from starlette.concurrency import run_in_threadpool

from core.config import APP_NAME, EMERGENT_LLM_KEY

logger = logging.getLogger(__name__)

STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
_storage_key = None


def init_storage(force: bool = False) -> str:
    global _storage_key
    if _storage_key and not force:
        return _storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_LLM_KEY}, timeout=30)
    resp.raise_for_status()
    _storage_key = resp.json()["storage_key"]
    return _storage_key


def _request(method: str, path: str, headers: dict | None = None, **kw) -> requests.Response:
    for attempt in range(2):
        key = init_storage(force=attempt > 0)
        resp = requests.request(method, f"{STORAGE_URL}/objects/{path}",
                                headers={"X-Storage-Key": key, **(headers or {})}, timeout=120, **kw)
        if resp.status_code == 404 and attempt == 0:
            continue  # possibly a stale storage key; re-init once
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp


def build_path(kind: str, user_id: str, name: str) -> str:
    return f"{APP_NAME}/{kind}/{user_id}/{name}"


async def put_object(path: str, data: bytes, content_type: str) -> str:
    resp = await run_in_threadpool(_request, "PUT", path, {"Content-Type": content_type}, data=data)
    return resp.json()["path"]


async def get_object(path: str) -> bytes:
    resp = await run_in_threadpool(_request, "GET", path)
    return resp.content
