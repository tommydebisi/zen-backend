from app.database.repository.plan import PlanRepository
from app.database.models.plan import Plan
from bson import ObjectId
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

class PlanUseCase:
    def __init__(self, plan_repo: PlanRepository):
        self.plan_repo = plan_repo

    def create_plan(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a new plan."""
        plan_data = Plan(**data)
        bson_data = plan_data.to_bson()

        # Insert into database
        result_data = self.plan_repo.create_plan(bson_data)
        if not result_data:
            return False, {
                "message": "Plan creation failed."
            }

        # stringify the ObjectId
        result_data['_id'] = str(result_data['_id'])

        return True, {
            "message": "Plan created successfully.",
            "data": result_data
        }

    def get_all_plans(self) -> Tuple[bool, Dict[str, Any]]:
        """Fetch all plans."""
        plans = self.plan_repo.get_all_plans()

        return True, {
            "message": "Plans found.",
            "data": plans
        }
        


    def get_plan_by_id(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a plan by ID."""
        return self.plan_repo.get_by_id(plan_id)

    def update_plan(self, plan_id: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Update a plan."""
        # update the updated_at field
        data.update({"updated_at": datetime.now()})

        self.plan_repo.find_and_update_plan({"_id": ObjectId(plan_id)}, data)
        return True, {
            "message": "Plan updated successfully."
        }

    def delete_plan(self, plan_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Delete a plan."""
        self.plan_repo.find_and_delete_plan({"_id": ObjectId(plan_id)})
        return True, {
            "message": "Plan deleted successfully."
        }