from app.database.base import Database
from app.database.models.payment_history import PaymentHistory
from app.database.models.plan import Plan
from bson import ObjectId
from typing import Dict, Any, List


class PaymentHistoryRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_user_id(self, user_id: str):
        """Fetch an archer rank by ID."""
        return self.db.get_one(PaymentHistory.__name__, {"user_id": ObjectId(user_id)})
    
    def create_payment_history(self, data: Dict):
        """
            Create payment history
        """
        result = self.db.insert_one(PaymentHistory.__name__, data)

        # fetch the inserted record
        return str(result.inserted_id)
    
    def all_payment_history_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """
            Get all payment history for a user
        """
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id)
                }
            },
            {
                "$lookup": {
                    "from": "Plan",
                    "localField": "plan_id",
                    "foreignField": "_id",
                    "as": "plan_details"
                }
            },
            {
                "$unwind": "$plan_details"
            },
            {
                "$project": {
                    "_id": 0,
                    "plan_name": "$plan_details.newplan",
                    "amount": 1,
                    "payment_date": 1,
                    "status": 1
                }
            },
            {
                "$sort": {"payment_date": -1}
            }
        ]
        
        return self.db.aggregate(PaymentHistory.__name__, pipeline)
    
    def all_payment_history(self) -> List[Dict[str, Any]]:
        pipeline = [
            {
                "$lookup": {
                    "from": "Plan",
                    "localField": "plan_id",
                    "foreignField": "_id",  # The field in Plan to match against
                    "as": "plan_details"  # The resulting array containing matched Plan documents
                }
            },
            {
                "$unwind": {
                    "path": "$plan_details",  # Unwind the plan_details array
                    "preserveNullAndEmptyArrays": True  # Allow documents with no matching plan to pass through
                }
            },
            {
                "$project": {
                    "_id": 0,  # Exclude the MongoDB default _id field
                    "plan_name": {
                        "$cond": {
                            "if": {"$ne": ["$plan_id", None]},  # If plan_id is not null
                            "then": "$plan_details.newplan",  # Use newplan from the Plan model
                            "else": "$email"  # Otherwise, use the email field
                        }
                    },
                    "amount": 1,  # Include the amount field from PaymentHistory
                    "payment_date": 1,  # Include the payment_date field from PaymentHistory
                    "status": 1  # Include the status field from PaymentHistory
                }
            },
            {
                "$sort": {"payment_date": -1}  # Sort the results by payment_date in descending order
            }
        ]

