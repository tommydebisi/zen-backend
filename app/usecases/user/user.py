from app.database import (
    UserRepository,
    SubscriptionRepository,
    PlanRepository,
    ArcherRankRepository,
    PaymentHistoryRepository
)
from app.database.models.user import User, UserUpdate
from app.database.models.subscription import Subscription
from app.database.models.plan import Plan
from flask_jwt_extended import create_access_token, create_refresh_token
from app.services.paystack.setup import paystack
from typing import Optional, Tuple, Dict, Any
from bson import ObjectId


class UserUseCase:
    def __init__(self, user_repo: UserRepository, subscription_repo: SubscriptionRepository, plan_repo: PlanRepository, rank_repo: ArcherRankRepository, pay_history_repo: PaymentHistoryRepository):
        self.user_repo = user_repo
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.rank_repo = rank_repo
        self.pay_history_repo = pay_history_repo


    def register_user(self, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Register a new user."""
        user_data = User(**data)
        user_data.set_password(data["Password"])

        if self.user_repo.get_by_email(user_data.email):
            return False, {
                "message": "User already exists."
            }

        # create a customer account in paystack
        response: Dict = paystack.customer.create(
            first_name=user_data.firstName,
            last_name=user_data.lastName,
            email=user_data.email,
            phone=user_data.PhoneNumber,
        )

        if not response.get('status'):
            return False, {
                "message": response.get('message'),
            }
        
        response_data: Dict = response.get('data')

        # # update the current user model with the necessary codes from paystack
        user_data.customer_code = response_data.get('customer_code')
        user_data.status = "Terms_Condition"

        # Insert into database
        result_id = self.user_repo.create_user(user_data.to_bson())

        # # Fetch the inserted record
        result_data = self.user_repo.get_by_id(result_id)

        return True, {
            "message": "User registered successfully.",
            "data": {
                "user_id": str(result_data['_id']),
                "email": result_data['email'],
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
                "refresh_token": refresh_token,
                "status": user_data.status,
                "plan_id": str(user_data.plan_id)
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
        response_data = {}

        # get user image_url
        response_data['image_url'] = user.get('image_url')
        response_data['user_status'] = user.get('status')
        
        plan = self.plan_repo.get_by_id(str(user.get('plan_id')))
        if plan:
            plan_data = Plan(**plan)
            response_data['plan_id'] = str(plan_data.id)
            response_data["plan"] = plan_data.newplan
            response_data["benefits"] = plan_data.benefits
            response_data["price"] = plan_data.Price // 100

        # get user's total points
        points = self.rank_repo.find_all_points_by_email(user.get('email'))
        if points:
            response_data["points"] = points[0].get('total_points', 0)
        else:
            response_data["points"] = 0

        subscription = self.subscription_repo.get_by_plan_user_id(user_id=user_id, plan_id=str(user.get('plan_id')))
        if subscription:
            subscription_data = Subscription(**subscription)
            response_data["status"] = subscription_data.status
            response_data["end_date"] = subscription_data.end_date

            # get all payment history for a user
            response_data['payment_history'] = self.pay_history_repo.all_payment_history_by_user_id(str(user["_id"]))

        # convert _id to string
        user["_id"] = str(user["_id"])
        user_data = User(**user)
        response_data["fullName"] = user_data.firstName + " " + user_data.lastName


        return True, {
            "message": "User found.",
            "data": response_data
        }


    def refresh_token(self, identity: str) -> Tuple[str, str]:
        """Refresh JWT access token."""
        new_access_token = create_access_token(identity=identity)
        return True, new_access_token
    
    def update_user_with_id(self, user_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update a user."""
        user_update_data = UserUpdate(**data)

        # get the user
        user_data = self.user_repo.get_by_id(user_id)
        if user_data is None:
            return False, "User does not exist"
        
        if data.get('route') == 'acknowledgment':
            if user_data.get('status') != 'Terms_Condition':
                return False, "User already filled or not allowed to fill form"
            user_update_data.status = 'Waiver'
        elif data.get('route') == 'conduct':
            if user_data.get('status') != 'Waiver' and user_data.get('status') != 'Payment':
                return False, "User already filled or not allowed to fill form"
            user_update_data.status = 'Payment'

        if  user_data.get('status') != 'Payment':
            self.user_repo.find_and_update_user({"_id": ObjectId(user_id)}, user_update_data.to_bson())
        return True, "User updated successfully."