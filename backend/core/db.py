import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, IndexModel

from core.config import DB_NAME, MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

_U = ("user_id", ASCENDING)
_NEW = ("created_at", DESCENDING)

INDEXES: dict[str, list[IndexModel]] = {
    "users": [IndexModel([("email", ASCENDING)], name="email")],
    "organizations": [IndexModel([("owner_id", ASCENDING)], name="owner")],
    "projects": [IndexModel([_U, _NEW], name="user_new"), IndexModel([_U, ("category", ASCENDING)], name="user_cat")],
    "uploads": [IndexModel([_U, _NEW], name="user_new")],
    "generated_images": [
        IndexModel([_U, ("is_deleted", ASCENDING), _NEW], name="user_live_new"),
        IndexModel([("job_id", ASCENDING)], name="job"),
        IndexModel([("project_id", ASCENDING)], name="project"),
    ],
    "generation_jobs": [IndexModel([_U, _NEW], name="user_new"), IndexModel([("status", ASCENDING)], name="status")],
    "credit_transactions": [IndexModel([_U, _NEW], name="user_new")],
    "payments": [IndexModel([("order_id", ASCENDING)], name="order", unique=True), IndexModel([_U, _NEW], name="user_new")],
    "user_subscriptions": [IndexModel([_U, ("status", ASCENDING)], name="user_status")],
    "generation_settings": [IndexModel([_U, ("mode", ASCENDING)], name="user_mode", unique=True)],
}


async def ensure_indexes() -> None:
    for collection, models in INDEXES.items():
        for model in models:
            try:
                await db[collection].create_indexes([model])
            except Exception as exc:
                logging.getLogger(__name__).error("ensure_indexes(%s.%s): %s", collection, model.document["name"], exc)
