from app.database.repository.subscription import SubscriptionRepository
from app.database.repository.user import UserRepository
from app.database.repository.plan import PlanRepository
from app.database.models.subscription import Subscription
from bson import ObjectId
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


class SubscriptionUseCase:
    def __init__(self, subscription_repo: SubscriptionRepository, user_repo: UserRepository, plan_repo: PlanRepository):
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo
        self.plan_repo = plan_repo

    def create_subscription(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a new subscription."""
        subscription_data = Subscription(**data)

        # check if plan exists
        plan_data = self.plan_repo.get_by_id(subscription_data.plan_id)
        if not plan_data:
            return False, {
                "message": "Plan not found."
            }

        # check if user exists 
        user_data = self.user_repo.get_by_id(subscription_data.user_id)
        if not user_data:
            return False, {
                "message": "User not found."
            }

        if self.subscription_repo.get_by_user_id(subscription_data.user_id):
            return False, {
                "message": "User already has an active subscription."
            }
        
        #  update user expiry date to none
        self.user_repo.find_and_update_user({"_id": ObjectId(subscription_data.user_id)}, {"expiry_date": None})
        
        subscription_data.set_end_date(values={
            "start_date": subscription_data.start_date,
            "duration": plan_data['duration']
        })

        bson_data = subscription_data.to_bson()

        # Insert into database
        result_data = self.subscription_repo.create_subscription(bson_data)
    
        return True, {
            "message": "Subscription created successfully.",
            "data": {
                "subscription_id": str(result_data['_id']),
                "user_id": str(result_data['user_id']),
                "plan_id": str(result_data['plan_id']),
                "status": result_data['status'],
            }
        }

    def get_all_subscriptions(self) -> Optional[Dict[str, Any]]:
        """Fetch all subscriptions."""
        return self.subscription_repo.get_all_subscriptions()

    def get_subscription_by_id(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a subscription by ID."""
        return self.subscription_repo.get_by_id(subscription_id)

    def update_subscription(self, subscription_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update a subscription."""
        # update the updated_at field
        data.update({"updated_at": datetime.now()})
        self.subscription_repo.find_and_update_subscription({"_id": ObjectId(subscription_id)}, data)
        return True, {
            "message": "Subscription updated successfully."
        }

    def delete_subscription(self, subscription_id: str) -> Tuple[bool, str]:
        """Delete a subscription."""
        self.subscription_repo.find_and_delete_subscription({"_id": ObjectId(subscription_id)})
        return True, {
            "message": "Subscription deleted successfully."
        }