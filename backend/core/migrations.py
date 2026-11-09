"""Lightweight, idempotent MongoDB migrations recorded in the `migrations` collection."""
import logging

from core.config import AI_PROVIDER, IMAGE_MODEL, PLANS, QUALITY_JUDGE_MODEL
from core.db import db
from core.models import AIProvider, SubscriptionPlan, now_iso

logger = logging.getLogger(__name__)


async def _seed_plans():
    for p in PLANS:
        plan = SubscriptionPlan(**p)
        await db.subscription_plans.replace_one({"_id": plan.id}, plan.to_mongo(), upsert=True)


async def _seed_providers():
    for kind, model in (("image_generation", IMAGE_MODEL), ("quality_judge", QUALITY_JUDGE_MODEL)):
        doc = AIProvider(id=kind, kind=kind, model=model, is_mock=AI_PROVIDER == "mock")
        await db.ai_providers.replace_one({"_id": kind}, doc.to_mongo(), upsert=True)


# Re-runnable steps: always applied on boot so config edits reach the DB.
ALWAYS = [_seed_plans, _seed_providers]
# One-shot steps: (id, fn); append new ones, never reorder.
ONCE: list = []


async def run_migrations() -> None:
    for fn in ALWAYS:
        await fn()
    for mig_id, fn in ONCE:
        if await db.migrations.find_one({"_id": mig_id}):
            continue
        await fn()
        await db.migrations.insert_one({"_id": mig_id, "applied_at": now_iso()})
        logger.info("migration applied: %s", mig_id)
