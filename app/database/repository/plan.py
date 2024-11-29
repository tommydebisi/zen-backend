from app.database.base import Database
from app.database.models.plan import Plan
from bson import ObjectId
from typing import Dict, Any

class PlanRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, plan_id: str):
        """Fetch a plan by ID."""
        return self.db.get_one(Plan.__name__, {"_id": ObjectId(plan_id)})
    
    def get_by_newplan(self, newplan: str):
        """Fetch a plan by name."""
        return self.db.get_one(Plan.__name__, {"newplan": newplan})

    def get_all_plans(self):
        """Fetch all plans."""
        return self.db.get_all(Plan.__name__)

    def create_plan(self, data: Dict):
        """Insert a new plan record."""
        result = self.db.insert_one(Plan.__name__, data)

        # Fetch the inserted record
        return self.get_by_id(str(result.inserted_id))

    def find_and_update_plan(self, query: Dict[str, Any], data: Dict):
        """Find a plan by query and update the record."""
        return self.db.update_one(Plan.__name__, query, data)

    def find_and_delete_plan(self, query: Dict[str, Any]):
        """Find a plan by query and delete the record."""
        return self.db.delete_one(Plan.__name__, query)