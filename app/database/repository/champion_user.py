from app.database.base import Database
from app.database.models.champion_user import ChampionUser
from bson import ObjectId
from typing import Dict, Any


class ChampionUserRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, champion_user_id: str):
        """Fetch a user by ID."""
        return self.db.get_one(ChampionUser.__name__, {"_id": ObjectId(champion_user_id)})
    
    def create_champion_user(self, data: Dict):
        """Insert a new user record."""
        result = self.db.insert_one(ChampionUser.__name__, data)

        # fetch the inserted record
        return str(result.inserted_id)
    
    def find_and_update_champion_user(self, query: Dict[str, Any], data: Dict):
        """Find a champion user by query and update the record."""
        return self.db.update_one(ChampionUser.__name__, query, data)
    
    def find_and_delete_champion_user(self, query: Dict[str, Any]):
        """Find a champoion user by query and delete the record."""
        return self.db.delete_one(ChampionUser.__name__, query)