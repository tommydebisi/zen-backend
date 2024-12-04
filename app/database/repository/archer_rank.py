from app.database.base import Database
from app.database.models.archer_rank import ArcherRank
from bson import ObjectId
from typing import Dict, Any


class ArcherRankRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, archer_rank_id: str):
        """Fetch an archer rank by ID."""
        return self.db.get_one(ArcherRank.__name__, {"_id": ObjectId(archer_rank_id)})

    def get_all_archer_ranks(self):
        """Fetch all archer ranks."""
        return self.db.get_all(ArcherRank.__name__)

    def create_archer_rank(self, data: Dict):
        """Insert a new archer rank record."""
        result = self.db.insert_one(ArcherRank.__name__, data)

        # Fetch the inserted record
        return self.get_by_id(str(result.inserted_id))

    def find_and_update_archer_rank(self, query: Dict[str, Any], data: Dict):
        """Find an archer rank by query and update the record."""
        return self.db.update_one(ArcherRank.__name__, query, data)

    def find_and_delete_archer_rank(self, query: Dict[str, Any]):
        """Find an archer rank by query and delete the record."""
        return self.db.delete_one(ArcherRank.__name__, query)
    
    def find_and_sort_by(self, key: str, order: int):
        """Sort archer ranks by a key."""
        return self.db.sort_by(ArcherRank.__name__, key, order)
    
    def filter_and_sort_by(self, query: Dict[str, Any], key: str, order: int):
        """Filter and sort archer ranks by a key."""
        return self.db.filter_and_sort_by(ArcherRank.__name__, query, key, order)