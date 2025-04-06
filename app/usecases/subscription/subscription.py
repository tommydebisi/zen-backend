from app.database import SubscriptionRepository, UserRepository, PlanRepository, WalkInRepository
from app.database.models.subscription import Subscription
from bson import ObjectId
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from app.services.paystack.setup import paystack


class SubscriptionUseCase:
    def __init__(self, subscription_repo: SubscriptionRepository, user_repo: UserRepository, plan_repo: PlanRepository, walk_in_repo: WalkInRepository):
        self.walk_in_repo = walk_in_repo
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo
        self.plan_repo = plan_repo

    def create_subscription(self, user_id: str, callback_url: str) -> Tuple[bool, Dict[str, Any]]:
        """Create a new subscription."""
        # check if user exists 
        user_data: Dict = self.user_repo.get_by_id(user_id=user_id)
        if not user_data:
            return False, {
                "message": "User not found."
            }

        if user_data.get('status') != 'Payment':
            return False, {
                "message": "User not done with registration"
            }

        plan_data = self.plan_repo.get_by_id(user_data.get('plan_id'))
        if not plan_data:
            return False, {
                    "message": "Plan not found."
                }

        # check if subscription with the plan and user id exists
        if sub_data := self.subscription_repo.get_by_plan_user_id(str(user_data.get('_id')), str(user_data.get('plan_id'))):
            if sub_data.get('status') != 'pending':
                return False, {
                    "message": "User already has an active subscription."
                }

        old_amount = plan_data.get('Price')

        new_reg = self.plan_repo.get_by_registration()
        new_amount = 0
        if new_reg:
            new_amount: int = new_reg.get('Price')
            
        new_amount += old_amount

        # initialize paystack payment
        response: Dict = paystack.transaction.initialize(
            email=user_data.get('email'),
            amount=new_amount,
            callback_url=callback_url,
            metadata={
                "custom": {
                    "type": "subscription",
                    "plan_code": plan_data.get('plan_code'),
                    "customer_code": user_data.get('customer_code'),
                    "first_name": user_data.get('firstName')
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

    def get_all_subscriptions(self) -> Optional[Dict[str, Any]]:
        """Fetch all subscriptions."""
        return self.subscription_repo.get_all_subscriptions()
    
    def get_all_subscriptions_with_user_details(self) -> Tuple[bool, Dict[str, Any]]:
        """Fetch all subscriptions with user details."""
        subscriptions = self.subscription_repo.get_subscriptions_with_user_details()

        if len(subscriptions) < 1:
            return False, {
                "message": "Subscriptions not found."
            }
        
        return True, {
            "message": "Subscriptions found.",
            "data": subscriptions
        }


    def get_subscription_by_id(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a subscription by ID."""
        return self.subscription_repo.get_by_id(subscription_id)

    def update_subscription(self, subscription_id: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Update a subscription."""
        # update the updated_at field
        data.update({"updated_at": datetime.now()})
        self.subscription_repo.find_and_update_subscription({"_id": ObjectId(subscription_id)}, data)
        return True, {
            "message": "Subscription updated successfully."
        }

    def cancel_subscription(self, subscription_id: str) -> Tuple[bool, Dict[str, Any]]:
        """cancel a subscription."""
        subs_data = Subscription(**self.subscription_repo.get_by_id(subscription_id=subscription_id))
        if not subs_data.email_token or not subs_data.subscription_code:
            return False, {
                "message": "No active subscription",
                "status": 400
            }

        response: Dict = paystack.subscription.disable(
            code=subs_data.subscription_code,
            token=subs_data.email_token
        )
        return response.get('status'), {
            "message": response.get('message'),
            "status": 200
        }

    def upgrade_subscription(self, plan_id: str, user_id: str, callback_url: str) -> Tuple[bool, Dict[str, Any]]:
        """
            Upgrades to a new subscription or enables former subscription
        """

        # need user email and plan_code
        user_data = self.user_repo.get_by_id(user_id=user_id)
        if not user_data:
            return False, {
                "message": "User not found",
                "status": 404
            }

        plan_data = self.plan_repo.get_by_id(plan_id=plan_id)
        if not plan_data:
            return False, {
                "message": "Plan not found",
                "status": 404
            }

        if user_data.get('status') != "done":
            return False, {
                "message": "No active subscription",
                "status": 400
            }

        # initialize a transaction for the new subscription
        response: Dict = paystack.transaction.initialize(
            plan=plan_data.get('plan_code'),
            email=user_data.get('email'),
            amount=plan_data.get('Price') * 100,
            callback_url=callback_url,
            metadata={
                "custom": {
                    "type": "upgrade",
                    "first_name": user_data.get('firstName'),
                }
            }
            
        )

        if not response.get('status'):
            return False, {
                "message": response.get('message'),
                "status": 400
            }
        
        response_data: Dict = response.get('data')
        return True, {
            "message": response.get('message'),
            "data": {
                "authorization_url": response_data.get('authorization_url'),
                "reference": response_data.get('reference')
            },
            "status": 200
        }

    def renew_plan(self, plan_id: str, user_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
            Renew Subscription plan that failed
        """
        sub_data = self.subscription_repo.get_by_plan_user_id(user_id=user_id, plan_id=plan_id)
        if not sub_data:
            return False, {
                "message": "No active subscription for user",
                "status": 404
            }
        
        # generate update link to renew plan
        sub_parsed_data = Subscription(**sub_data)

        response: Dict = paystack.subscription.generate_update_subscription_link(
            subscription_code=sub_parsed_data.subscription_code
        )

        return response.get('status'), {
            "message": response.get('message'),
            "data": response.get("data"),
            "status": 200
        }
    
    def initialize_payment(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
            Initializes a payment
        """
        callback_url = data.get('callback_url')
        amount = data.get('amount')
        email = data.get('email')
        entry_date = data.get('entry_date')
        full_name: str = data.get('fullName').strip()

        # get the number of people with given entry date
        number_of_people = self.walk_in_repo.get_walkin_count_pipeline(entry_date= datetime.strptime(entry_date, "%Y-%m-%dT%H:%M:%SZ"))
        if len(number_of_people) != 0 and number_of_people[0].get('total_walkins') == 6:
            return False, {
                "message": "Number of people exceeded",
                "status": 400
            }
        
        list_of_names = full_name.split()
        first_name, last_name = "", ""
        if len(list_of_names) == 1:
            first_name = list_of_names[0]
        else:
            first_name, last_name = list_of_names[0], list_of_names[1]

        response: Dict = paystack.transaction.initialize(
                email=email,
                amount=amount * 100,
                callback_url=callback_url,
                metadata={
                    "custom": {
                        "type": "walkin",
                        "entry_date": entry_date,
                        "first_name": first_name,
                        "last_name": last_name
                    }
                }
            )
        
        if not response.get('status'):
                return False, {
                    "message": response.get('message'),
                    "status": 400
                }
        
        response_data: Dict = response.get('data')
        return True, {
                "message": response.get('message'),
                "data": {
                    "authorization_url": response_data.get('authorization_url'),
                    "reference": response_data.get('reference')
                },
                "status": 200
            }
    

    def verify_payment(self, reference: str) -> Tuple[bool, Dict[str, Any]]:
        """
            verify payment by the reference
        """
        response: Dict = paystack.transaction.verify(
            reference=reference
        )

        if not response.get('status'):
                return False, {
                    "message": response.get('message'),
                    "status": 400
                }

        response_data: Dict = response.get('data')
        
        return True, {
            "status": response_data.get('status'),
            "message": response.get('message')
        }
    
    def get_active_users(self) -> Tuple[bool, Dict[str, Any]]:
        """
            Gets all active users by with plan name too
        """
        data = dict()
        # get active users by plan
        active_users_plan = self.subscription_repo.get_active_users_by_plan()
        data['active_users_per_plan'] = active_users_plan

        # get total active users
        total_active_users_result = self.subscription_repo.get_all_active_users()
        total_active_users = total_active_users_result[0]["total_active_users"] if total_active_users_result else 0

        data['total_active_users'] = total_active_users

        return True, {
            "message": "active users retrieved successfully",
            "data": data
        }
