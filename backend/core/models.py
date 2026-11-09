import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, Optional

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


def new_id() -> str:
    return uuid.uuid4().hex


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BaseDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    id: PyObjectId = Field(default_factory=new_id, alias="_id")
    created_at: str = Field(default_factory=now_iso)

    @classmethod
    def from_mongo(cls, doc: Optional[dict]):
        return cls.model_validate(doc) if doc else None

    def to_mongo(self) -> dict:
        return self.model_dump(by_alias=True)


class User(BaseDocument):
    email: str = ""
    name: str = ""
    organization_id: Optional[str] = None
    credits: int = 0
    plan: str = "free"
    total_generated: int = 0


class Organization(BaseDocument):
    name: str
    owner_id: str


class Project(BaseDocument):
    user_id: str
    name: str
    description: str = ""
    category: Optional[str] = None
    is_deleted: bool = False


class UploadedImage(BaseDocument):
    user_id: str
    project_id: Optional[str] = None
    storage_path: str
    filename: str
    content_type: str
    width: int
    height: int
    size_bytes: int
    is_deleted: bool = False


class GeneratedImage(BaseDocument):
    user_id: str
    job_id: str
    upload_id: str
    project_id: Optional[str] = None
    mode: str
    category: str
    style: Optional[str] = None
    storage_path: str
    content_type: str
    width: int
    height: int
    quality: dict = Field(default_factory=dict)
    is_mock: bool = False
    is_deleted: bool = False


class GenerationJob(BaseDocument):
    user_id: str
    mode: str
    upload_id: str
    project_id: Optional[str] = None
    category: str
    style: Optional[str] = None
    settings: dict = Field(default_factory=dict)
    output_count: int = 1
    status: str = "queued"  # queued | processing | completed | partial | failed
    stage: str = "Queued"
    progress: int = 0
    credits_reserved: int = 0
    credits_refunded: int = 0
    output_ids: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    error: Optional[str] = None
    provider: str = ""
    is_mock: bool = False
    parent_job_id: Optional[str] = None
    finished_at: Optional[str] = None


class CreditTransaction(BaseDocument):
    user_id: str
    kind: str  # trial | purchase | debit | refund | adjustment
    amount: int
    balance_after: int
    description: str
    ref_id: Optional[str] = None


class SubscriptionPlan(BaseDocument):
    name: str
    credits: int
    price_paise: int
    period_days: int
    features: list[str] = Field(default_factory=list)
    purchasable: bool = True
    popular: bool = False


class UserSubscription(BaseDocument):
    user_id: str
    plan_id: str
    status: str = "active"  # active | cancelled | superseded
    renews_at: Optional[str] = None
    payment_id: Optional[str] = None


class Payment(BaseDocument):
    user_id: str
    plan_id: str
    order_id: str
    amount_paise: int
    currency: str = "INR"
    provider: str  # razorpay | demo
    status: str = "created"  # created | paid | failed
    provider_payment_id: Optional[str] = None
    paid_at: Optional[str] = None


class AIProvider(BaseDocument):
    kind: str
    model: str
    enabled: bool = True
    is_mock: bool = False


class GenerationSetting(BaseDocument):
    user_id: str
    mode: str
    settings: dict[str, Any] = Field(default_factory=dict)
