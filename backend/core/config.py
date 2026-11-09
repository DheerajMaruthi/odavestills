import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

APP_NAME = "auragem"
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
FILE_SIGNING_SECRET = os.environ["FILE_SIGNING_SECRET"]

# "gemini" = real AI generation, "mock" = clearly labelled development mode (no AI).
AI_PROVIDER = (os.environ.get("AI_PROVIDER") or ("gemini" if EMERGENT_LLM_KEY else "mock")).lower()
IMAGE_MODEL = os.environ.get("IMAGE_MODEL") or "gemini-3-pro-image-preview"
QUALITY_JUDGE_MODEL = os.environ.get("QUALITY_JUDGE_MODEL") or "gemini-3-flash-preview"
GENERATION_TIMEOUT_S = int(os.environ.get("GENERATION_TIMEOUT_S", "240"))
MAX_PROVIDER_ATTEMPTS = int(os.environ.get("MAX_PROVIDER_ATTEMPTS", "2"))
QUALITY_RETRY_BELOW = float(os.environ.get("QUALITY_RETRY_BELOW", "7.5"))
MAX_QUALITY_RETRIES = int(os.environ.get("MAX_QUALITY_RETRIES", "2"))
MAX_CONCURRENT_JOBS = int(os.environ.get("MAX_CONCURRENT_JOBS", "3"))

RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")
RAZORPAY_ENABLED = bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET)

FREE_TRIAL_CREDITS = int(os.environ.get("FREE_TRIAL_CREDITS", "3"))
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_MB", "15")) * 1024 * 1024
MAX_OUTPUTS_PER_JOB = 4
SIGNED_URL_TTL_S = 6 * 3600

# Credits charged per successfully delivered image, per mode.
CREDIT_COST = {"product": 1, "model": 1, "bg_removal": 1}

# Prices in paise. Edit here (or seed DB) to change pricing.
PLANS = [
    {"id": "free", "name": "Free Trial", "credits": FREE_TRIAL_CREDITS, "price_paise": 0, "period_days": 0,
     "features": ["3 trial images", "All photography styles", "Quality check on every image"], "purchasable": False},
    {"id": "starter", "name": "Starter", "credits": 20, "price_paise": 129900, "period_days": 30,
     "features": ["20 images", "Product & model photography", "Background removal", "Commercial usage rights"], "purchasable": True},
    {"id": "growth", "name": "Growth", "credits": 75, "price_paise": 399900, "period_days": 30, "popular": True,
     "features": ["75 images", "Everything in Starter", "Up to 4 variations per run", "Priority processing"], "purchasable": True},
    {"id": "business", "name": "Business", "credits": 300, "price_paise": 1199900, "period_days": 30,
     "features": ["300 images", "Everything in Growth", "Bulk catalogue projects", "Dedicated support"], "purchasable": True},
]
PLANS_BY_ID = {p["id"]: p for p in PLANS}
