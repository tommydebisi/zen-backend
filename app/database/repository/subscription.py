from app.database.base import Database
from app.database.models.subscription import Subscription
from bson import ObjectId
from typing import Dict, Any, List

class SubscriptionRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_email(self, email: str):
        """Fetch a subscription by email."""
        return self.db.get_one(Subscription.__name__, {"email": email})
    
    def get_by_user_id(self, user_id: str):
        """Fetch a subscription by user ID."""
        return self.db.get_one(Subscription.__name__, {"user_id": ObjectId(user_id)})
    
    def get_by_id(self, subscription_id: str):
        """Fetch a subscription by ID."""
        return self.db.get_one(Subscription.__name__, {"_id": ObjectId(subscription_id)})

    def get_all_subscriptions(self):
        """Fetch all subscriptions."""
        return self.db.get_all(Subscription.__name__)

    def create_subscription(self, data: Dict):
        """Insert a new subscription record."""
        result = self.db.insert_one(Subscription.__name__, data)

        # fetch the inserted record
        return self.get_by_id(str(result.inserted_id))
    
    def find_and_update_subscription(self, query: Dict[str, Any], data: Dict):
        """Find a subscription by query and update the record."""
        return self.db.update_one(Subscription.__name__, query, data)
    
    def find_and_delete_subscription(self, query: Dict[str, Any]):
        """Find a subscription by query and delete the record."""
        return self.db.delete_one(Subscription.__name__, query)
    
    def get_subscriptions_with_user_details(self) -> List[Dict[str, Any]]:
        """
        Retrieve subscriptions with user name, email, and status.
        """
        pipeline = [
            {
                "$lookup": {
                    "from": "User",
                    "localField": "user_id",
                    "foreignField": "_id",
                    "as": "user_details"
                }
            },
            {
                "$unwind": {
                    "path": "$user_details",
                    "preserveNullAndEmptyArrays": False
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": {
                        "$concat": [
                            "$user_details.firstName",
                            " ",
                            "$user_details.lastName"
                        ]
                    },
                    "image_url": "$user_details.image_url",
                    "email": "$email",
                    "status": "$status"
                }
            }
        ]

        return self.db.aggregate(Subscription.__name__, pipeline)