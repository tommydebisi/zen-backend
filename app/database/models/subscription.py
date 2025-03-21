from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
from datetime import datetime, timedelta
from .objectid import PydanticObjectId
from enum import Enum



class SubscriptionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    NON_RENEWING = "non-renewing"
    ATTENTION = "attention"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ENABLED = "enabled"


class Subscription(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    user_id: PydanticObjectId = Field(None, alias="user_id")
    plan_id: PydanticObjectId = Field(None, alias="plan_id")
    subscription_code: Optional[str] = None
    email_token: Optional[str] = None
    email: str
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def to_json(self) -> dict:
        """Convert model to JSON-compatible dictionary."""
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
    
    @classmethod
    def from_bson(cls, data: Dict) -> "Subscription":
        """Create a model instance from a BSON dictionary."""
        return cls(**data)
