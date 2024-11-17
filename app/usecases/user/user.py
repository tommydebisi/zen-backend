from app.database.repository.user import UserRepository
from app.database.models.user import User
from flask_jwt_extended import create_access_token, create_refresh_token
from typing import Optional, Tuple, Dict, Any
from bson import ObjectId


class UserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register_user(self, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Register a new user."""
        user_data = User(**data)
        user_data.set_password(data["password"])

        if self.user_repo.get_by_email(user_data.email):
            return False, "User already exists."

        # Insert into database
        result_id = self.user_repo.create_user(user_data.to_json())
        print(result_id)

        # Fetch the inserted record
        result_data = self.user_repo.get_by_id(result_id)

        return True, "User registered successfully.", {
            "user_id": str(result_data['_id']),
            "email": result_data['email']
        }

    def login_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, str]]]:
        """Authenticate and login a user."""
        user = self.user_repo.get_by_email(email)
        if not user:
            return False, "User not found.", None
        
        user_data = User(**user)

        # Check if the provided password matches the stored hashed password
        if not user_data.check_password(password):
            return False, "Incorrect password.", None

        # Generate JWT access token
        access_token = create_access_token(identity=str(user["_id"]))
        refresh_token = create_refresh_token(identity=str(user["_id"]))
        return True, "Login successful.", {
            "access": access_token,
            "refresh": refresh_token
        }

    def get_all_users(self):
        """Fetch all users."""
        return self.user_repo.get_all_users()
    
    def refresh_token(self, identity: str) -> Tuple[str, str]:
        """Refresh JWT access token."""
        new_access_token = create_access_token(identity=identity)
        return True, new_access_token
    
    def update_user_with_id(self, user_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update a user."""
        self.user_repo.find_and_update_user({"_id": ObjectId(user_id)}, data)
        return True, "User updated successfully."