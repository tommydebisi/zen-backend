from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional, Dict
from .objectid import PydanticObjectId
from datetime import datetime

class PaymentHistory(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    user_id: Optional[PydanticObjectId] = Field(None, alias="user_id")
    plan_id: Optional[PydanticObjectId] = Field(None, alias="plan_id")
    amount: Optional[int] = None
    status: str
    reference: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    payment_date: datetime = Field(default_factory=datetime.now)
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