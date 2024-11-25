from app.database.repository.team import TeamRepository
from app.database.models.team import Team
from bson import ObjectId
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

class TeamUseCase:
    def __init__(self, team_repo: TeamRepository):
        self.team_repo = team_repo

    def create_team(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a new team."""
        team_data = Team(**data)
        bson_data = team_data.to_bson()

        # Insert into database
        result_data = self.team_repo.create_team(bson_data)
    
        return True, {
            "message": "Team Member created successfully.",
            "data": {
                "team_id": str(result_data['_id']),
                "name": result_data['name'],
                "position": result_data['position'],
                "context": result_data['context'],
                "image": result_data['image_url']
            }
        }

    def get_all_teams(self) -> Tuple[bool, Dict[str, Any]]:
        """Fetch all teams."""
        teams =  self.team_repo.get_all_teams()

        return True, {
            "message": "Team Members found.",
            "data": teams
        }
        

    def get_team_by_id(self, team_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Fetch a team by ID."""
        team_member =  self.team_repo.get_by_id(team_id)
        if not team_member:
            return False, {
                "message": "Team Member not found."
            }
        
        return True, {
            "message": "Team Member found.",
            "data": {
                "team_id": str(team_member['_id']),
                "name": team_member['name'],
                "position": team_member['position'],
                "context": team_member['context'],
                "image": team_member['image_url']
            }
        }

    def update_team(self, team_id: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Update a team."""
        # update the updated_at field
        data.update({"updated_at": datetime.now()})

        self.team_repo.find_and_update_team({"_id": ObjectId(team_id)}, data)
        return True, {
            "message": "Team Member updated successfully."
        }

    def delete_team(self, team_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Delete a team."""
        self.team_repo.find_and_delete_team({"_id": ObjectId(team_id)})
        return True, {
            "message": "Team Member deleted successfully."
        }