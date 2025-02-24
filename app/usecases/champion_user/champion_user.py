from app.database import ChampionUserRepository
from app.database.models.champion_user import ChampionUser, ChampionUserUpdate
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import Dict, Any, Tuple
from app.services.paystack.setup import paystack
from datetime import datetime


class ChampionUserUseCase:
    def __init__(self, champion_user_repo: ChampionUserRepository):
        self.champion_user_repo= champion_user_repo

    def create_champion_user(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a new champion user."""
        champion_user_data = ChampionUser(**data)

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
            raise RuntimeError(f"Failed to update archer rank: {str(e)}")
        
    def champion_user_payment(self, champion_user_id: str, callback_url: str) -> Tuple[bool, Dict[str, Any]]:
        """
            Makes payment for a champion_user
        """
        amount = 10000
        # get the champion_user making payment
        champion_user = self.champion_user_repo.get_by_id(champion_user_id=champion_user_id)

        # initialize paystack payment
        response: Dict = paystack.transaction.initialize(
            email=champion_user.get('email'),
            amount=amount*100,
            callback_url=callback_url,
            metadata={
                    "custom": {
                        "type": "competion"
                    }
                }
        )

        if not response.get('status'):
            return False, {
                "message": response.get('message')
            }
        
        response_data: Dict = response.get('data')
        return True, {
            "message": response.get('message'),
            "data": {
                "authorization_url": response_data.get('authorization_url'),
                "reference": response_data.get('reference')
            }
        }
