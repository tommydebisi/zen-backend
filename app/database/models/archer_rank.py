from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional, Dict
from .objectid import PydanticObjectId
from datetime import datetime
from enum import Enum


class ArcherRankType(str, Enum):
    RECURVE = "Recurve"
    COMPOUND = "Compound"
    BAREBOW = "Barebow"
    GENERAL = "General"

class ArcherRank(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    full_name: str
    point: int
    type: ArcherRankType
    image_url: str
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
    

class ArcherRankUpdate(BaseModel):
    point: int
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        return data