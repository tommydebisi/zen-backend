from app.database.base import Database
from app.database.models.record import Record
from bson import ObjectId
from typing import Dict, Any

class RecordRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, record_id: str):
        """Fetch a record by ID."""
        return self.db.get_one(Record.__name__, {"_id": ObjectId(record_id)})
    
    def get_by_competition(self, competition: str):
        """Fetch a record by competition."""
        return self.db.get_one(Record.__name__, {"competition": competition})

    def get_all_records(self):
        """Fetch all records."""
        return self.db.get_all(Record.__name__)

    def create_record(self, data: Dict):
        """Insert a new record."""
        result = self.db.insert_one(Record.__name__, data)

        # Fetch the inserted record
        return self.get_by_id(str(result.inserted_id))

    def find_and_update_record(self, query: Dict[str, Any], data: Dict):
        """Find a record by query and update the record."""
        return self.db.update_one(Record.__name__, query, data)

    def find_and_delete_record(self, query: Dict[str, Any]):
        """Find a record by query and delete the record."""
        return self.db.delete_one(Record.__name__, query)
    
    def find_and_sort_by(self, key: str, order: int):
        """Sort records by key."""
        return self.db.sort_by(Record.__name__, key, order)