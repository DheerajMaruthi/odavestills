import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import account, billing, projects, studio
from core.config import AI_PROVIDER, CORS_ORIGINS
from core.db import client, ensure_indexes
from core.migrations import run_migrations
from services import jobs, storage

try:  # launched as `backend.server`
    from backend.clerk_auth import clerk_router
except ModuleNotFoundError:  # launched from inside backend/ as `server`
    from clerk_auth import clerk_router

logging.basicConfig(level=logging.INFO, format='{"t":"%(asctime)s","lvl":"%(levelname)s","log":"%(name)s","msg":"%(message)s"}')
logger = logging.getLogger("auragem")

app = FastAPI(title="AuraGem API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")


@app.get("/api/")
async def health():
    return {"status": "ok", "service": "auragem", "ai_provider": AI_PROVIDER}


for r in (clerk_router, account.router, projects.router, studio.router, billing.router):
    app.include_router(r)

app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def startup():
    await ensure_indexes()
    await run_migrations()
    try:
        storage.init_storage()
    except Exception as exc:
        logger.error("Storage init failed: %s", exc)
    await jobs.recover_interrupted_jobs()


@app.on_event("shutdown")
async def shutdown():
    client.close()
