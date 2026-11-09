"""Razorpay REST client (orders + HMAC signature checks). Uses plain HTTPS so no SDK is required."""
import hashlib
import hmac

import requests
from starlette.concurrency import run_in_threadpool

from core.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET

API = "https://api.razorpay.com/v1"


def _create_order(amount_paise: int, receipt: str, notes: dict) -> dict:
    r = requests.post(f"{API}/orders", auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET), timeout=20,
                      json={"amount": amount_paise, "currency": "INR", "receipt": receipt[:40], "notes": notes, "payment_capture": 1})
    r.raise_for_status()
    return r.json()


async def create_order(amount_paise: int, receipt: str, notes: dict) -> dict:
    return await run_in_threadpool(_create_order, amount_paise, receipt, notes)


def _hmac(secret: str, msg: bytes) -> str:
    return hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()


def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    return hmac.compare_digest(_hmac(RAZORPAY_KEY_SECRET, f"{order_id}|{payment_id}".encode()), signature or "")


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    return bool(RAZORPAY_WEBHOOK_SECRET) and hmac.compare_digest(_hmac(RAZORPAY_WEBHOOK_SECRET, body), signature or "")
