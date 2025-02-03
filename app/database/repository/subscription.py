from app.database.base import Database
from app.database.models.subscription import Subscription
from app.database.models.plan import Plan
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
    
    def get_by_plan_user_id(self, user_id: str, plan_id: str):
        """Fetch a subscription by user ID."""
        return self.db.get_one(Subscription.__name__, { "user_id": ObjectId(user_id), "plan_id": ObjectId(plan_id) })
    
    def get_by_plan_id(self, plan_id: str):
        """Fetch a subscription by user ID."""
        return self.db.get_one(Subscription.__name__, {"plan_id": ObjectId(plan_id)})
    
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
    
    def find_and_cancel_subscription(self, query: Dict[str, Any], status: str):
        """Find a subscription by query and delete the record."""
        return self.db.update_one(Subscription.__name__, query, {
            "status": status
        })
    
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
    
    def get_active_users_by_plan(self) -> List[Dict[str, Any]]:
        """
        Gets the number of active users for each plan, including plans with zero active users.
        Excludes plans where interval is 'registration' or 'walkIn'.
        """
        pipeline = [
            # 1️⃣ Filter out plans with interval 'registration' or 'walkIn'
            {
                "$match": {
                    "interval": {"$nin": ["registration", "walkIn"]}
                }
            },

            # 2️⃣ Left Join (lookup) with subscriptions collection
            {
                "$lookup": {
                    "from": "Subscription",
                    "localField": "_id",
                    "foreignField": "plan_id",
                    "as": "subscriptions"
                }
            },

            # 3️⃣ Unwind subscriptions (preserving plans with no subscriptions)
            {
                "$unwind": {
                    "path": "$subscriptions",
                    "preserveNullAndEmptyArrays": True  # Ensures plans with no subscriptions are kept
                }
            },

            # 4️⃣ Filter only active subscriptions OR keep plans with no subscriptions
            {
                "$match": {
                    "$or": [
                        {"subscriptions.status": "active"},  # Keep active subscriptions
                        {"subscriptions": None}  # Keep plans with no subscriptions
                    ]
                }
            },

            # 5️⃣ Group by plan_id and count active users
            {
                "$group": {
                    "_id": "$_id",
                    "plan_name": {"$first": "$newplan"},  # Plan name
                    "active_users": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$subscriptions.status", "active"]}, 1, 0
                            ]
                        }
                    }
                }
            },

            # 6️⃣ Format output
            {
                "$project": {
                    "_id": 0,
                    "plan_name": 1,
                    "active_users": 1
                }
            }
        ]

        return self.db.aggregate(Plan.__name__, pipeline)

    
    def get_all_active_users(self) -> List[Dict[str, Any]]:
        """
            Get the number of users actively subscribed
        """
        pipeline = [
            {"$match": {"status": "active"}},
            {"$count": "total_active_users"}
        ]
        return self.db.aggregate(Subscription.__name__, pipeline)
