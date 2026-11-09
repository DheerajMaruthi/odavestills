from fastapi import HTTPException
from pymongo import ReturnDocument

from core.db import db
from core.models import CreditTransaction


async def _log(user_id: str, kind: str, amount: int, balance: int, description: str, ref_id: str | None):
    await db.credit_transactions.insert_one(CreditTransaction(
        user_id=user_id, kind=kind, amount=amount, balance_after=balance,
        description=description, ref_id=ref_id).to_mongo())


async def reserve(user_id: str, amount: int, description: str, ref_id: str) -> int:
    """Atomically deduct credits up-front; failures are refunded by the worker."""
    doc = await db.users.find_one_and_update(
        {"_id": user_id, "credits": {"$gte": amount}}, {"$inc": {"credits": -amount}},
        return_document=ReturnDocument.AFTER)
    if not doc:
        raise HTTPException(status_code=402, detail="Not enough credits. Please top up to continue.")
    await _log(user_id, "debit", -amount, doc["credits"], description, ref_id)
    return doc["credits"]


async def grant(user_id: str, amount: int, kind: str, description: str, ref_id: str | None = None) -> int:
    doc = await db.users.find_one_and_update(
        {"_id": user_id}, {"$inc": {"credits": amount}}, return_document=ReturnDocument.AFTER)
    await _log(user_id, kind, amount, doc["credits"], description, ref_id)
    return doc["credits"]
