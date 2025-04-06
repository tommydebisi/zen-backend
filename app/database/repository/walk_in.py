from app.database.base import Database
from app.database.models.walk_in import WalkIn
from bson import ObjectId
from typing import Dict, Any, List
from datetime import datetime, timedelta

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
    
    def get_walkin_count_pipeline(self, entry_date: datetime) -> List[Dict[str, Any]]:
        """
        Create a pipeline to count walk-ins for a specific date.
        The date is set to midnight of the given date.
        """
        start_of_day = datetime(entry_date.year, entry_date.month, entry_date.day)
        end_of_day = start_of_day + timedelta(days=1)

        pipeline = [
            {
                "$match": {
                    "entry_date": {
                        "$gte": start_of_day,
                        "$lt": end_of_day
                    }
                }
            },
            {
                "$count": "total_walkins"
            },
            {
                "$project": {
                    "_id": 0,
                    "total_walkins": 1
                }
            }
        ]
        
        return self.db.aggregate(WalkIn.__name__, pipeline)