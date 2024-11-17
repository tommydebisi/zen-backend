from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from .objectid import PydanticObjectId
from werkzeug.security import generate_password_hash, check_password_hash


class User(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    email: str
    password: str
    first_name: str
    last_name: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    date_of_birth: Optional[datetime] = None
    street: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None

    image_url: Optional[str] = None

    # Emergency Contact
    emergency_first_name: Optional[str] = None
    emergency_last_name: Optional[str] = None
    emergency_relationship: Optional[str] = None
    emergency_phone_number: Optional[str] = None

    # Medical Information
    has_allergies: Optional[bool] = None
    allergy_details: Optional[str] = None

    # Archery Experience
    previous_experience: Optional[bool] = None
    experience_details: Optional[str] = None
    interested_in_beginner_lessons: Optional[bool] = None

    # Member acknowledgement
    member_acknowledgement: Optional[bool] = None

    # Consent for Archery Range Rules & Code of Conduct
    acknowledge_risks: Optional[bool] = None
    consent_to_media: Optional[bool] = None
    initials: Optional[str] = None

    # Enable arbitrary types to support custom ObjectId
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def set_password(self, password: str) -> None:
        """Set hashed password."""
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if password matches hashed password."""
        return check_password_hash(self.password, password)

    def to_json(self) -> dict:
        """Convert model to JSON-compatible dictionary."""
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
