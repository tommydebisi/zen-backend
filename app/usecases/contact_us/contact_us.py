from pydantic import ValidationError
from app.database.repository.contact_us import ContactUsRepository
from app.database.models.contact_us import ContactUs
from typing import Tuple, Dict, Any

class ContactUsUseCase:
    def __init__(self, contact_us_repo: ContactUsRepository):
        self.contact_us_repo = contact_us_repo

    def send_contact_message(self, data: dict) ->  Tuple[bool, Dict[str, str]]:
        try:
            contact_message = ContactUs(**data)
            self.contact_us_repo.send_email(contact_message)
            return True, {
                "message": "Message sent successfully."
            }
        except ValidationError as e:
            raise ValueError({"error": "Validation Error", "details": e.errors()})
        except Exception as e:
            raise RuntimeError({"error": "Failed to send message", "details": str(e)})