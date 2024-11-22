from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ContactUs(BaseModel):
    email: str
    first_name: str
    last_name: str
    message: str
    phone_number: str

    def to_json(self) -> dict:
        """Convert model to JSON-compatible dictionary."""
        return jsonable_encoder(self, exclude_none=True)