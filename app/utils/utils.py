import re
from bson import ObjectId
from typing import Any, Dict


def validateEmail(email: str) -> bool:
    """
        takes in the email of the user, checks if
        it is valid and returns a bool
    """
    # define pattern to search for in the email
    pattern = r'^[a-zA-Z0-9]+@\w+.[a-z]{3}'

    # check if email is a valid pattern
    if re.search(pattern, email):
        return True
    return False




def serialize_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively convert ObjectId fields to strings in a MongoDB document."""
    for key, value in document.items():
        if isinstance(value, ObjectId):
            document[key] = str(value)
        elif isinstance(value, dict):  # Recursively process sub-documents
            document[key] = serialize_document(value)
        elif isinstance(value, list):  # Process lists of documents
            document[key] = [serialize_document(item) if isinstance(item, dict) else item for item in value]
    return document
