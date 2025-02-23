from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
from datetime import datetime
from .objectid import PydanticObjectId


class ChampionUser(BaseModel):
    firstName: str
    lastName: str
    email: str
    date: datetime
    image_url: Optional[str] = None
    PhoneNumber: str
    sex: Optional[str] = None

    # Team/Club
    association: Optional[str] = None
    nationality: Optional[str] = None
    language: Optional[str] = None

    # Place of departure
    state: Optional[str] = None
    country: Optional[str] = None

    # discipline
    category: Optional[str] = None
    distance: Optional[str] = None

    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
    

class ChampionUserUpdate(BaseModel):
    # Team/Club
    association: Optional[str] = None
    nationality: Optional[str] = None
    language: Optional[str] = None

    # Place of departure
    state: Optional[str] = None
    country: Optional[str] = None

    # discipline
    category: Optional[str] = None
    distance: Optional[str] = None

    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        return data