from app.database.repository.user import UserRepository
from app.database.models.user import User
from flask_jwt_extended import create_access_token, create_refresh_token
from typing import Optional, Tuple, Dict, Any
from bson import ObjectId


class UserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo


    def register_user(self, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Register a new user."""
        user_data = User(**data)
        user_data.set_password(data["Password"])

        if self.user_repo.get_by_email(user_data.email):
            return False, {
                "message": "User already exists."
            }

        # Insert into database
        result_id = self.user_repo.create_user(user_data.to_json())
        print(result_id)

        # Fetch the inserted record
        result_data = self.user_repo.get_by_id(result_id)

        return True, {
            "message": "User registered successfully.",
            "data": {
                "user_id": str(result_data['_id']),
                "email": result_data['email']
            }
        }

    def login_user(self, email: str, password: str) -> Tuple[bool, Optional[Dict[str, str]]]:
        """Authenticate and login a user."""
        user = self.user_repo.get_by_email(email)
        if not user:
            return False, {
                "message": "User not found."
            }
        
        user_data = User(**user)


        # Check if the provided password matches the stored hashed password
        if not user_data.check_password(password):
            return False, {
                "message": "Invalid email or password.",
            }

        # Generate JWT access token
        access_token = create_access_token(identity={
            "user_id": str(user_data.id),
            "role": user_data.role
        })
        refresh_token = create_refresh_token(identity={
            "user_id": str(user_data.id),
            "role": user_data.role
        })

        return True, {
            "message": "User logged in successfully.",
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        }

    def get_all_users(self):
        """Fetch all users."""
        return self.user_repo.get_all_users()
    
    # get a user by id
    def get_user(self, user_id: str):
        """Get a user by Id"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False, {
                "message": "User not found."
            }
        
        # convert _id to string
        user["_id"] = str(user["_id"])
        user_data = User(**user)

        # change to json
        user_bson = user_data.to_bson()

        # remove password
        user_bson.pop("Password")
        user_bson['_id'] = str(user_bson['_id'])

        return True, {
            "data": user_bson
        }


    def refresh_token(self, identity: str) -> Tuple[str, str]:
        """Refresh JWT access token."""
        new_access_token = create_access_token(identity=identity)
        return True, new_access_token
    
    def update_user_with_id(self, user_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update a user."""
        self.user_repo.find_and_update_user({"_id": ObjectId(user_id)}, data)
        return True, "User updated successfully."