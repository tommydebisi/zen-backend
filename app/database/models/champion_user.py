from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from datetime import datetime


class ChampionUser(BaseModel):
    firstName: str
    lastName: str
    email: str
    date: datetime
    image_url: str
    PhoneNumber: str
    sex: Optional[str] = None
    isOfficial: bool
    unique_id: str
    status: Optional[str] = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data


class ChampionUserUpdate(BaseModel):
    # Team/Club
    Association: Optional[str] = None
    Nationality: Optional[str] = None
    Language: Optional[str] = None

    # Place of departure
    Departure_state: Optional[str] = None
    Departure_country: Optional[str] = None

    # discipline
    Category: Optional[List[Dict[str, str]]] = None
    Selection: Optional[str] = None
    status: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        return data