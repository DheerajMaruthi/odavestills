import json
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from core.config import PLANS_BY_ID, RAZORPAY_ENABLED, RAZORPAY_KEY_ID
from core.db import db
from core.deps import current_user
from core.models import CreditTransaction, Payment, User, UserSubscription, new_id, now_iso
from payments import razorpay
from services import credits

router = APIRouter(prefix="/api/billing")
logger = logging.getLogger(__name__)


@router.get("/summary")
async def summary(user: User = Depends(current_user)):
    txns = [CreditTransaction.from_mongo(d).model_dump() async for d in db.credit_transactions.find({"user_id": user.id}).sort("created_at", -1).limit(50)]
    pays = [Payment.from_mongo(d).model_dump(exclude={"user_id"}) async for d in db.payments.find({"user_id": user.id}).sort("created_at", -1).limit(20)]
    sub = UserSubscription.from_mongo(await db.user_subscriptions.find_one({"user_id": user.id, "status": "active"}, sort=[("created_at", -1)]))
    return {"credits": user.credits, "plan": user.plan, "subscription": sub.model_dump() if sub else None,
            "transactions": txns, "payments": pays, "payments_mode": "razorpay" if RAZORPAY_ENABLED else "demo"}


class OrderIn(BaseModel):
    plan_id: str


@router.post("/orders", status_code=201)
async def create_order(body: OrderIn, user: User = Depends(current_user)):
    plan = PLANS_BY_ID.get(body.plan_id)
    if not plan or not plan["purchasable"]:
        raise HTTPException(status_code=404, detail="Plan not available")
    pay_id = new_id()
    if RAZORPAY_ENABLED:
        try:
            order = await razorpay.create_order(plan["price_paise"], pay_id, {"user_id": user.id, "plan_id": plan["id"]})
        except Exception as exc:
            logger.error("razorpay order failed: %s", exc)
            raise HTTPException(status_code=502, detail="Payment gateway unavailable, please try again")
        order_id, provider = order["id"], "razorpay"
    else:
        order_id, provider = f"demo_order_{pay_id[:16]}", "demo"
    pay = Payment(id=pay_id, user_id=user.id, plan_id=plan["id"], order_id=order_id, amount_paise=plan["price_paise"], provider=provider)
    await db.payments.insert_one(pay.to_mongo())
    return {"mode": provider, "order_id": order_id, "amount": plan["price_paise"], "currency": "INR",
            "key_id": RAZORPAY_KEY_ID if RAZORPAY_ENABLED else None, "plan": plan,
            "prefill": {"name": user.name, "email": user.email}}


async def fulfill(order_id: str, provider_payment_id: str | None) -> bool:
    """Idempotent: only the first successful confirmation grants credits."""
    doc = await db.payments.find_one_and_update({"order_id": order_id, "status": {"$ne": "paid"}},
                                                {"$set": {"status": "paid", "provider_payment_id": provider_payment_id, "paid_at": now_iso()}})
    if not doc:
        return False
    pay = Payment.from_mongo(doc)
    plan = PLANS_BY_ID[pay.plan_id]
    await credits.grant(pay.user_id, plan["credits"], "purchase", f"{plan['name']} plan · {plan['credits']} credits", pay.id)
    await db.user_subscriptions.update_many({"user_id": pay.user_id, "status": "active"}, {"$set": {"status": "superseded"}})
    renews = (datetime.now(timezone.utc) + timedelta(days=plan["period_days"])).isoformat()
    await db.user_subscriptions.insert_one(UserSubscription(user_id=pay.user_id, plan_id=plan["id"], renews_at=renews, payment_id=pay.id).to_mongo())
    await db.users.update_one({"_id": pay.user_id}, {"$set": {"plan": plan["id"]}})
    return True


async def _owned_payment(order_id: str, user: User) -> Payment:
    pay = Payment.from_mongo(await db.payments.find_one({"order_id": order_id, "user_id": user.id}))
    if not pay:
        raise HTTPException(status_code=404, detail="Order not found")
    return pay


class VerifyIn(BaseModel):
    order_id: str
    payment_id: str
    signature: str


@router.post("/verify")
async def verify(body: VerifyIn, user: User = Depends(current_user)):
    await _owned_payment(body.order_id, user)
    if not RAZORPAY_ENABLED or not razorpay.verify_payment_signature(body.order_id, body.payment_id, body.signature):
        raise HTTPException(status_code=400, detail="Payment signature verification failed")
    await fulfill(body.order_id, body.payment_id)
    return {"ok": True}


class DemoIn(BaseModel):
    order_id: str


@router.post("/demo-complete")
async def demo_complete(body: DemoIn, user: User = Depends(current_user)):
    pay = await _owned_payment(body.order_id, user)
    if RAZORPAY_ENABLED or pay.provider != "demo":
        raise HTTPException(status_code=403, detail="Demo checkout is disabled when Razorpay is configured")
    await fulfill(pay.order_id, f"demo_pay_{new_id()[:12]}")
    return {"ok": True}


@router.post("/cancel")
async def cancel_subscription(user: User = Depends(current_user)):
    await db.user_subscriptions.update_many({"user_id": user.id, "status": "active"}, {"$set": {"status": "cancelled"}})
    await db.users.update_one({"_id": user.id}, {"$set": {"plan": "free"}})
    return {"ok": True}


@router.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    if not razorpay.verify_webhook_signature(body, request.headers.get("X-Razorpay-Signature", "")):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    event = json.loads(body)
    if event.get("event") in ("payment.captured", "order.paid"):
        entity = event["payload"]["payment"]["entity"]
        await fulfill(entity["order_id"], entity["id"])
    elif event.get("event") == "payment.failed":
        entity = event["payload"]["payment"]["entity"]
        await db.payments.update_one({"order_id": entity["order_id"], "status": "created"}, {"$set": {"status": "failed"}})
    return {"ok": True}
