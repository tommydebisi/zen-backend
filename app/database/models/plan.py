from enum import Enum
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from .objectid import PydanticObjectId

class IntervalType(str, Enum):
    Daily = "daily"
    Monthly = "monthly"
    Weekly = "weekly"
    Quarterly = "quarterly"
    Biannually = "biannually"
    Annually = "annually"
    Hourly = "hourly"
    WalkIn = 'walkIn'


class Plan(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    plan_code: Optional[str] = None
    newplan: str
    Price: int
    benefits: List[str]
    interval: IntervalType
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
    

class PlanUpdate(BaseModel):
    newplan: Optional[str] = None
    Price: Optional[int] = None
    benefits: Optional[List[str]] = None
    interval: Optional[IntervalType] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        return data