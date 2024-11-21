from app.database.repository.subscription import SubscriptionRepository
from app.database.repository.user import UserRepository
from app.database.models.subscription import Subscription
from bson import ObjectId
from typing import Dict, Any, Optional, Tuple


class SubscriptionUseCase:
    def __init__(self, subscription_repo: SubscriptionRepository, user_repo: UserRepository):
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo

    def create_subscription(self, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Create a new subscription."""
        subscription_data = Subscription(**data)

        # check if user exists 
        user_data = self.user_repo.get_by_id(subscription_data.user_id)
        if not user_data:
            return False, "User not found."

        if self.subscription_repo.get_by_user_id(subscription_data.user_id):
            return False, "Subscription already exists."
        
        #  update user expiry date to none
        self.user_repo.find_and_update_user({"_id": ObjectId(subscription_data.user_id)}, {"expiry_date": None})
        
        bson_data = subscription_data.to_bson()

        # Insert into database
        result_data = self.subscription_repo.create_subscription(bson_data)
    
        return True, "Subscription created successfully.", {
            "subscription_id": str(result_data['_id']),
            "user_id": str(result_data['user_id']),
            "plan": result_data['plan']
        }

    def get_all_subscriptions(self) -> Optional[Dict[str, Any]]:
        """Fetch all subscriptions."""
        return self.subscription_repo.get_all_subscriptions()

    def get_subscription_by_id(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a subscription by ID."""
        return self.subscription_repo.get_by_id(subscription_id)

    def update_subscription(self, subscription_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update a subscription."""
        self.subscription_repo.find_and_update_subscription({"_id": ObjectId(subscription_id)}, data)
        return True, "Subscription updated successfully."

    def delete_subscription(self, subscription_id: str) -> Tuple[bool, str]:
        """Delete a subscription."""
        self.subscription_repo.find_and_delete_subscription({"_id": ObjectId(subscription_id)})
        return True, "Subscription deleted successfully."