from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
from datetime import datetime, timedelta
from .objectid import PydanticObjectId
from enum import Enum



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
    plan_id: PydanticObjectId = Field(None, alias="plan_id")
    email: str
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


    def set_end_date(self, values: Dict) -> datetime:
        start_date = values.get("start_date")
        duration: int = values.get("duration")

        if not start_date or not duration:
            raise ValueError("start_date and duration must be provided")

        self.end_date = start_date + timedelta(days=duration)

    def to_json(self) -> dict:
        """Convert model to JSON-compatible dictionary."""
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
