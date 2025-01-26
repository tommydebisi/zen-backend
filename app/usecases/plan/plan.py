from app.database import PlanRepository
from app.database.models.plan import Plan, PlanUpdate
from app.services.paystack.setup import paystack
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

class PlanUseCase:
    def __init__(self, plan_repo: PlanRepository):
        self.plan_repo = plan_repo

    def create_plan(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a new plan."""
        plan_data = Plan(**data)
        

        # Check if the plan already exists
        if self.plan_repo.get_by_newplan(plan_data.newplan):
            return False, {
                "message": "Plan already exists."
            }
        
        if  plan_data.interval != 'walkIn':
            response: Dict = paystack.plan.create(
                name=plan_data.newplan,
                interval=plan_data.interval,
                amount=plan_data.Price * 100, # convert accordingly in paystack
                currency="NGN",
            )

            if not response.get('status'):
                return False, {
                    "message": response.get('message')
                }
            
            response_data: Dict = response.get('data')
            plan_data.plan_code = response_data.get('plan_code')


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
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            return {
                "message": "Plan not found."
            }

        # stringify the ObjectId
        plan['_id'] = str(plan['_id'])

        return {
            "message": "Plan found.",
            "data": plan
        }

    def update_plan(self, plan_id: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Update a plan by its ID.
        If no plan matches the ID or no changes were made, return an appropriate message.
        """
        try:
            # Add or update the `updated_at` field
            update_plan_data = PlanUpdate(**data)

            # Perform the update operation
            result = self.plan_repo.find_and_update_plan({"_id": ObjectId(plan_id)}, update_plan_data.to_bson())

            # Check if the plan exists
            if result.matched_count == 0:
                return False, {"message": "Plan not found."}

            # Check if any changes were made
            if result.modified_count == 0:
                return False, {"message": "No changes were made to the plan."}
            
            # get the update plan by id
            plan_data = Plan(**self.plan_repo.get_by_id(plan_id=plan_id))
            data_update = update_plan_data.to_bson()

            if data_update.get('Price'):
                data_update['amount'] = data_update['Price'] * 100
                del data_update['Price']
            if data_update.get('newplan'):
                data_update['name'] = data_update['newplan']
                del data_update['newplan']

            del data_update['updated_at']

            # make changes to plan in paystack
            response: Dict = paystack.plan.update(
                plan_id=plan_data.plan_code,
                **data_update
            )
            return response.get('status'), {"message": response.get('message'),}

        except PyMongoError as e:
            raise RuntimeError(f"Database error during plan update: {str(e)}")

    def delete_plan(self, plan_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Delete a plan by its ID.
        If no plan matches the ID, return an error message.
        """
        try:
            result = self.plan_repo.find_and_delete_plan({"_id": ObjectId(plan_id)})
            
            if result.deleted_count == 0:
                return False, {"message": "Plan not found or already deleted."}

            return True, {"message": "Plan deleted successfully."}

        except PyMongoError as e:
            raise RuntimeError(f"Database error during plan deletion: {str(e)}")