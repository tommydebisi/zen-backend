from app.database import ChampionUserRepository, PaymentHistoryRepository
from app.database.models.champion_user import ChampionUser, ChampionUserUpdate
from app.database.models.payment_history import PaymentHistory
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import Dict, Any, Tuple
from app.services.paystack.setup import paystack
from uuid import uuid4


class ChampionUserUseCase:
    def __init__(self, champion_user_repo: ChampionUserRepository, payment_history_repo: PaymentHistoryRepository):
        self.champion_user_repo= champion_user_repo
        self.payment_history_repo = payment_history_repo

    def create_champion_user(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a new champion user."""
        # Generate unique id
        data['unique_id'] = str(uuid4())[:8]
        champion_user_data = ChampionUser(**data)

        # get champion user with email and see if it already exists 
        existing_champion_data = self.champion_user_repo.get_by_email(champion_user_email=champion_user_data.email)
        if existing_champion_data:
            return False, {
                "message": "Champion user already exists.",
                "status": 409
            }
        

        bson_data = champion_user_data.to_bson()

        # Insert into database
        result_id = self.champion_user_repo.create_champion_user(bson_data)
        if not result_id:
            return False, {
                "message": "Champion user creation failed."
            }
    
        return True, {
            "message": "Champion user created successfully.",
            "data": {
                "id": result_id
            }
        }
    
    def update_champion_user(self, champion_user_id: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Update an champion user by ID.
        """
        try:   
            edit_champion_user = ChampionUserUpdate(**data)
            edit_data = edit_champion_user.to_bson()

            # get champion user by ID
            champion_user = self.champion_user_repo.get_by_id(champion_user_id=champion_user_id)
            if not champion_user:
                return False, {
                    "message": "Champion user not found."
                }
            
            # check if official price differs from athlete price
            amount = 40 if champion_user.get('isOfficial') else 50

            # change amount based on country
            amount = (amount * 1000) if edit_data.get('Departure_country').lower() == 'nigeria' else (amount * 1600)

            # update amount in champion_user
            edit_data['amount'] = amount

            result_data = self.champion_user_repo.find_and_update_champion_user({"_id": ObjectId(champion_user_id)}, edit_data)
            if result_data.matched_count == 0:
                return False, {
                    "message": "Champion user not found."
                }
            
            if result_data.modified_count == 0:
                return False, {
                    "message": "No changes were made."
                }
            
            return True, {
                "message": "Champion user updated successfully."
            }
        except PyMongoError as e:
            raise RuntimeError(f"Failed to update Champion user: {str(e)}")
        
    def champion_user_payment(self, champion_user_id: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
            Makes payment for a champion_user
        """
        try:
            edit_champion_user = ChampionUserUpdate(**data)
            edit_data = edit_champion_user.to_bson()

            # get the callback_url
            callback_url = data.get('callback_url')

            # get the champion_user making payment
            champion_user = self.champion_user_repo.get_by_id(champion_user_id=champion_user_id)

            if not champion_user:
                return False, {
                    "message": "Champion user not found."
                }
            
            amount = champion_user.get('amount')
            if champion_user.get('status') != 'payment':
                number_of_categories = len(edit_champion_user.Category)
                amount *= number_of_categories

                if number_of_categories > 1:
                    edit_data['amount'] = amount
                edit_data['status'] = 'payment'

                result_data = self.champion_user_repo.find_and_update_champion_user({"_id": ObjectId(champion_user_id)}, edit_data)
                if result_data.matched_count == 0:
                    return False, {
                        "message": "Champion user not found."
                    }


            # initialize paystack payment
            response: Dict = paystack.transaction.initialize(
                email=champion_user.get('email'),
                amount=amount*100,
                callback_url=callback_url,
                metadata={
                        "custom": {
                            "type": "competition",
                            "unique_id": champion_user.get('unique_id'),
                            "first_name": champion_user.get('firstName')
                        }
                    }
            )

            if not response.get('status'):
                return False, {
                    "message": response.get('message')
                }
            response_data: Dict = response.get('data')

            # send email to champion_user
            self.champion_user_repo.send_welcome_email(ChampionUser(**champion_user), response_data.get('authorization_url'))
            
            return True, {
                "message": response.get('message'),
                "data": {
                    "authorization_url": response_data.get('authorization_url'),
                    "reference": response_data.get('reference')
                }
            }
        except PyMongoError as e:
            raise RuntimeError(f"Failed to update Champion user: {str(e)}")

    def get_all_champion_users(self) -> Tuple[bool, Dict[str, Any]]:
        """Fetch all champion users."""
        champion_users = self.champion_user_repo.get_all_champion_users()

        return True, {
            "message": "Champion users found.",
            "data": champion_users
        }
    
    def update_champion_user_payment_status(self, champion_user_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Update an champion user payment by ID.
        """
        try:
            # get the champion_user making payment
            champion_user_data = self.champion_user_repo.get_by_id(champion_user_id=champion_user_id)
            if not champion_user_data:
                return False, {
                    "message": "Champion user not found."
                }

            result_data = self.champion_user_repo.find_and_update_champion_user({"_id": ObjectId(champion_user_id)}, { "status": "paid" })
            if result_data.matched_count == 0:
                return False, {
                    "message": "Champion user not found."
                }
            

            # save payment history
            history_data = {
                "email": champion_user_data.get('email'),
                "status": "success",
                "amount": champion_user_data.get('amount'),
            }

            payment_history = PaymentHistory(**history_data)
            bson_data = payment_history.to_bson()
            self.payment_history_repo.create_payment_history(bson_data)
            
            return True, {
                "message": "Champion user payment updated successfully."
            }
        except PyMongoError as e:
            raise RuntimeError(f"Failed to update Champion user payment: {str(e)}")