from app.database.base import Database
from app.database.models.walk_in import WalkIn
from bson import ObjectId
from typing import Dict, Any

class WalkInRepository:
    def __init__(self, db: Database):
        self.db = db

    def create_walk_in(self, data: Dict):
        """Insert a new record."""
        result = self.db.insert_one(WalkIn.__name__, data)

        # Fetch the inserted record
        return self.get_by_id(str(result.inserted_id))
    
    def get_by_id(self, walk_ins_id: str):
        """Fetch a Walk-Ins by ID."""
        return self.db.get_one(WalkIn.__name__, {"_id": ObjectId(walk_ins_id)})