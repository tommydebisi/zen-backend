from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from .objectid import PydanticObjectId
from datetime import datetime

class TokenBlocklist(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    jti: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    # Enable arbitrary types to support custom ObjectId
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_json(self) -> dict:
        """Convert model to JSON-compatible dictionary."""
        return jsonable_encoder(self, exclude_none=True)
    
    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
    
    def __repr__(self) -> str:
        return f"<TokenBlocklist jti={self.jti}>"