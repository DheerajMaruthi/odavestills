import logging
import os

import requests
from fastapi import Depends
from pymongo.errors import DuplicateKeyError
from starlette.concurrency import run_in_threadpool

from core.config import FREE_TRIAL_CREDITS
from core.db import db
from core.models import CreditTransaction, Organization, User

try:
    from backend.clerk_auth import require_user
except ModuleNotFoundError:
    from clerk_auth import require_user

logger = logging.getLogger(__name__)


def _clerk_profile(user_id: str) -> tuple[str, str]:
    try:
        r = requests.get(f"https://api.clerk.com/v1/users/{user_id}", timeout=10,
                         headers={"Authorization": f"Bearer {os.environ['CLERK_SECRET_KEY']}", "User-Agent": "auragem"})
        r.raise_for_status()
        data = r.json()
        emails = data.get("email_addresses") or []
        email = emails[0]["email_address"] if emails else ""
        name = " ".join(x for x in [data.get("first_name"), data.get("last_name")] if x)
        return email, name or email.split("@")[0]
    except Exception as exc:  # profile is display-only; never block sign-in on it
        logger.warning("clerk profile lookup failed: %s", exc)
        return "", ""


async def current_user(auth: dict = Depends(require_user)) -> User:
    uid = auth["user_id"]
    doc = await db.users.find_one({"_id": uid})
    if doc:
        return User.from_mongo(doc)
    email, name = await run_in_threadpool(_clerk_profile, uid)
    org = Organization(name=f"{name or 'My'} Studio", owner_id=uid)
    user = User(id=uid, email=email, name=name, credits=FREE_TRIAL_CREDITS, organization_id=org.id)
    try:
        await db.users.insert_one(user.to_mongo())
    except DuplicateKeyError:
        return User.from_mongo(await db.users.find_one({"_id": uid}))
    await db.organizations.insert_one(org.to_mongo())
    await db.credit_transactions.insert_one(CreditTransaction(
        user_id=uid, kind="trial", amount=FREE_TRIAL_CREDITS, balance_after=FREE_TRIAL_CREDITS,
        description="Free trial credits").to_mongo())
    return user
