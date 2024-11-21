from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone, timedelta
from .objectid import PydanticObjectId
from werkzeug.security import generate_password_hash, check_password_hash


class User(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    email: str
    Password: str
    firstName: str
    lastName: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    date: Optional[datetime] = None
    Address: Optional[str] = None
    City: Optional[str] = None
    PostalCode: Optional[str] = None
    PhoneNumber: Optional[str] = None
    expiry_date: Optional[datetime] = datetime.now(timezone.utc) + timedelta(minutes=1)

    image_url: Optional[str] = None

    # Emergency Contact
    EmergencyFirstName: Optional[str] = None
    EmergencyLastName: Optional[str] = None
    EmergencyPhoneNumber: Optional[str] = None
    Relationship: Optional[str] = None

    # Medical Information
    allergies: Optional[bool] = None
    allergyDetails: Optional[str] = None

    # Archery Experience
    ArcheryExperience: Optional[bool] = None
    DetailExperience: Optional[str] = None
    BeginnersLesson: Optional[bool] = None

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
        self.Password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if password matches hashed password."""
        return check_password_hash(self.Password, password)

    def to_json(self) -> dict:
        """Convert model to JSON-compatible dictionary."""
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self) -> dict:
        """Convert model to BSON-compatible dictionary for MongoDB."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
