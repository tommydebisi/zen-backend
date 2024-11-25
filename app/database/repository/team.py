from app.database.base import Database
from app.database.models.team import Team
from bson import ObjectId
from typing import Dict, Any

class TeamRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, team_id: str):
        """Fetch a team by ID."""
        return self.db.get_one(Team.__name__, {"_id": ObjectId(team_id)})

    def get_all_teams(self):
        """Fetch all teams."""
        return self.db.get_all(Team.__name__)

    def create_team(self, data: Dict):
        """Insert a new team record."""
        result = self.db.insert_one(Team.__name__, data)

        # Fetch the inserted record
        return self.get_by_id(str(result.inserted_id))

    def find_and_update_team(self, query: Dict[str, Any], data: Dict):
        """Find a team by query and update the record."""
        return self.db.update_one(Team.__name__, query, data)

    def find_and_delete_team(self, query: Dict[str, Any]):
        """Find a team by query and delete the record."""
        return self.db.delete_one(Team.__name__, query)