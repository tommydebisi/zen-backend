from app.database import PaymentHistoryRepository
from app.database.models.payment_history import PaymentHistory
from bson import ObjectId
from typing import Dict, Any, Tuple
from datetime import datetime


class PaymentHistoryUseCase:
    def __init__(self, payment_history_repo: PaymentHistoryRepository):
        self.payment_history_repo = payment_history_repo

    def get_all_payment_history_by_user_id(self, user_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
            Fetch all payment history by user
        """
        histories = self.payment_history_repo.all_payment_history_by_user_id(user_id=user_id)
        
        return True, {
            "message": "Payment histories found.",
            "data": histories
        }
    
    def get_all_payment_history(self) -> Tuple[bool, Dict[str, Any]]:
        """
            Fetch all payment history by user
        """
        histories = self.payment_history_repo.all_payment_history()
        
        return True, {
            "message": "Payment histories found.",
            "data": histories
        }