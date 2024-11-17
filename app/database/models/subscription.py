from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
from datetime import datetime, timedelta
from .objectid import PydanticObjectId
from enum import Enum


class PlanType(str, Enum):
    ANNUAL = "Annual Membership"
    MONTHLY = "Monthly Membership"
    QUARTERLY = "Quarterly"
    DAILY = "Walk-ins"


class SubscriptionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"
    PAUSED = "paused"
    RENEWAL_DUE = "renewal_due"
    TRIAL = "trial"
    FAILED = "failed"
    GRACE_PERIOD = "grace_period"


class Subscription(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    user_id: PydanticObjectId = Field(None, alias="user_id")
    email: str
    plan: PlanType
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("end_date", mode="before", check_fields=False)
    def set_end_date(cls, v, values: Dict):
        start_date = values.get("start_date")
        plan = values.get("plan")

        if not start_date or not plan:
            raise ValueError("start_date and plan must be provided")

        if plan == PlanType.ANNUAL:
            return start_date + timedelta(days=365)
        elif plan == PlanType.QUARTERLY:
            return start_date + timedelta(days=90)
        elif plan == PlanType.MONTHLY:
            return start_date + timedelta(days=30)
        elif plan == PlanType.DAILY:
            return start_date + timedelta(days=1)
        else:
            raise ValueError(f"Unsupported plan type: {plan}")

    def to_json(self) -> dict:
        """Convert model to JSON-compatible dictionary."""
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
