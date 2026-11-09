from fastapi import APIRouter, Depends

from ai.prompts import catalog
from core.config import AI_PROVIDER, CREDIT_COST, MAX_OUTPUTS_PER_JOB, PLANS, RAZORPAY_ENABLED
from core.db import db
from core.deps import current_user
from core.models import CreditTransaction, GeneratedImage, GenerationJob, Project, User, UserSubscription
from services.serializers import image_out, job_out, project_out

router = APIRouter(prefix="/api")


def _platform() -> dict:
    return {"ai_mode": "mock" if AI_PROVIDER == "mock" else "live", "payments_mode": "razorpay" if RAZORPAY_ENABLED else "demo"}


@router.get("/catalog")
async def get_catalog():
    return {**catalog(), "plans": PLANS, "credit_cost": CREDIT_COST, "max_outputs": MAX_OUTPUTS_PER_JOB, **_platform()}


async def _active_subscription(user_id: str) -> dict | None:
    sub = UserSubscription.from_mongo(await db.user_subscriptions.find_one({"user_id": user_id, "status": "active"}, sort=[("created_at", -1)]))
    return sub.model_dump() if sub else None


@router.get("/me")
async def me(user: User = Depends(current_user)):
    org = await db.organizations.find_one({"_id": user.organization_id}, {"name": 1})
    return {**user.model_dump(), "organization_name": (org or {}).get("name"),
            "subscription": await _active_subscription(user.id), **_platform()}


@router.get("/dashboard")
async def dashboard(user: User = Depends(current_user)):
    jobs = [GenerationJob.from_mongo(d) async for d in db.generation_jobs.find({"user_id": user.id}).sort("created_at", -1).limit(6)]
    imgs = [GeneratedImage.from_mongo(d) async for d in db.generated_images.find({"user_id": user.id, "is_deleted": False}).sort("created_at", -1).limit(8)]
    projects = [Project.from_mongo(d) async for d in db.projects.find({"user_id": user.id, "is_deleted": False}).sort("created_at", -1).limit(4)]
    txns = [CreditTransaction.from_mongo(d).model_dump() async for d in db.credit_transactions.find({"user_id": user.id}).sort("created_at", -1).limit(8)]
    counts = {}
    for p in projects:
        counts[p.id] = await db.generated_images.count_documents({"project_id": p.id, "is_deleted": False})
    return {
        "stats": {
            "total_generated": user.total_generated, "credits": user.credits, "plan": user.plan,
            "projects": await db.projects.count_documents({"user_id": user.id, "is_deleted": False}),
            "active_jobs": await db.generation_jobs.count_documents({"user_id": user.id, "status": {"$in": ["queued", "processing"]}}),
        },
        "recent_jobs": [job_out(j, []) for j in jobs],
        "recent_images": [image_out(i) for i in imgs],
        "recent_projects": [project_out(p, counts.get(p.id, 0)) for p in projects],
        "transactions": txns,
        "subscription": await _active_subscription(user.id),
    }
