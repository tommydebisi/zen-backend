from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
from datetime import datetime
from .objectid import PydanticObjectId

class Record(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    competition: str
    location: str
    start_date: datetime
    end_date: datetime
    rank: str
    image_url: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def to_json(self) -> Dict:
        """Convert model to JSON-compatible Dictionary."""
        return jsonable_encoder(self, exclude_none=True)
    
    def to_bson(self) -> Dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data