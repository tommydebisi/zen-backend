from app.database import ArcherRankRepository
from app.database.models.archer_rank import ArcherRank, ArcherRankUpdate
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import Dict, Any, Tuple
from datetime import datetime


class ArcherRankUseCase:
    def __init__(self, archer_rank_repo: ArcherRankRepository):
        self.archer_rank_repo = archer_rank_repo

    def create_archer_rank(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a new archer rank."""
        archer_rank_data = ArcherRank(**data)

        # check if the archer rank name with the same type exists
        archer_rank = self.archer_rank_repo.filter_and_sort_by({"type": archer_rank_data.type, "full_name": archer_rank_data.full_name.strip()}, "point", 1)
        if len(archer_rank) > 0:
            return False, {
                "message": "Archer rank already exists."
            }
        
        bson_data = archer_rank_data.to_bson()

        # Insert into database
        result_data = self.archer_rank_repo.create_archer_rank(bson_data)
        if not result_data:
            return False, {
                "message": "Archer rank creation failed."
            }
        
        # stringify the ObjectId
        result_data['_id'] = str(result_data['_id'])
    
        return True, {
            "message": "Archer rank created successfully.",
            "data": result_data
        }

    def get_all_archer_ranks(self) -> Tuple[bool, Dict[str, Any]]:
        """Fetch all archer ranks."""
        # filter and sort archer rank by General, Recurve, Compound, and Barebow
        general_archer_ranks =  self.archer_rank_repo.filter_and_sort_by({"type": "General"}, "point", -1)
        recurve_archer_ranks =  self.archer_rank_repo.filter_and_sort_by({"type": "Recurve"}, "point", -1)
        compound_archer_ranks =  self.archer_rank_repo.filter_and_sort_by({"type": "Compound"}, "point", -1)
        barebow_archer_ranks =  self.archer_rank_repo.filter_and_sort_by({"type": "Barebow"}, "point", -1)

        return True, {
            "message": "Archer ranks found.",
            "data": {
                "General": general_archer_ranks,
                "Recurve": recurve_archer_ranks,
                "Compound": compound_archer_ranks,
                "Barebow": barebow_archer_ranks
            }
        }


    def get_archer_rank_by_id(self, archer_rank_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Fetch an archer rank by ID."""
        archer_rank =  self.archer_rank_repo.get_by_id(archer_rank_id)
        if not archer_rank:
            return False, {
                "message": "Archer rank not found."
            }
        
        # stringify the ObjectId
        archer_rank['_id'] = str(archer_rank['_id'])
        
        return True, {
            "message": "Archer rank found.",
            "data": archer_rank
        }

    def update_archer_rank(self, archer_rank_id: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Update an archer rank by ID.
        """
        try:   
            edit_archer_rank = ArcherRankUpdate(**data)

            # get the archer rank by ID
            archer_rank = self.archer_rank_repo.get_by_id(archer_rank_id)
            archer_rank_data = ArcherRank(**archer_rank)
            edit_archer_rank.point = edit_archer_rank.point + archer_rank_data.point

            edit_data = edit_archer_rank.to_bson()

            result_data = self.archer_rank_repo.find_and_update_archer_rank({"_id": ObjectId(archer_rank_id)}, edit_data)
            if result_data.matched_count == 0:
                return False, {
                    "message": "Archer rank not found."
                }
            
            if result_data.modified_count == 0:
                return False, {
                    "message": "No changes were made."
                }
            
            return True, {
                "message": "Archer rank updated successfully."
            }
        except PyMongoError as e:
            raise RuntimeError(f"Failed to update archer rank: {str(e)}")
        

    def delete_archer_rank(self, archer_rank_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Delete an archer rank by ID."""
        try:
            result_data = self.archer_rank_repo.find_and_delete_archer_rank({"_id": ObjectId(archer_rank_id)})
            if result_data.deleted_count == 0:
                return False, {
                    "message": "Archer rank not found."
                }
            
            return True, {
                "message": "Archer rank deleted successfully."
            }
        except PyMongoError as e:
            raise RuntimeError(f"Failed to delete archer rank: {str(e)}")