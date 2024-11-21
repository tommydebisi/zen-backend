from app.database.base import Database
from app.database.models.user import User
from bson import ObjectId
from typing import Dict, Any

class UserRepository:
    def __init__(self, db: Database):
        self.db = db
        self.db.db[User.__name__].create_index("expiry_date", expireAfterSeconds=0)

    def get_by_email(self, email: str):
        """Fetch a user by email."""
        return self.db.get_one(User.__name__, {"email": email})
    
    def get_by_id(self, user_id: str):
        """Fetch a user by ID."""
        return self.db.get_one(User.__name__, {"_id": ObjectId(user_id)})

    def get_all_users(self):
        """Fetch all users."""
        return self.db.get_all(User.__name__)

    def create_user(self, data: Dict):
        """Insert a new user record."""
        result = self.db.insert_one(User.__name__, data)

        # fetch the inserted record
        return str(result.inserted_id)
    
    def find_and_update_user(self, query: Dict[str, Any], data: Dict):
        """Find a user by query and update the record."""
        return self.db.update_one(User.__name__, query, data)
    
    def find_and_delete_user(self, query: Dict[str, Any]):
        """Find a user by query and delete the record."""
        return self.db.delete_one(User.__name__, query)