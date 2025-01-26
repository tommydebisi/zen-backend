from app.database import SubscriptionRepository, UserRepository, PlanRepository
from app.database.models.subscription import Subscription
from bson import ObjectId
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from app.services.paystack.setup import paystack


class SubscriptionUseCase:
    def __init__(self, subscription_repo: SubscriptionRepository, user_repo: UserRepository, plan_repo: PlanRepository):
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo
        self.plan_repo = plan_repo

    def create_subscription(self, user_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Create a new subscription."""
        # check if user exists 
        user_data: Dict = self.user_repo.get_by_id(user_id=user_id)
        if not user_data:
            return False, {
                "message": "User not found."
            }
        
        if user_data.get('status') != 'payment':
            return False, {
                "message": "User not done with registration"
            }
        data = dict()
        data['user_id'] = user_id
        data['plan_id'] = user_data.get('plan_id')
        data['email'] = user_data.get('email')


        plan_data = self.plan_repo.get_by_id(data.get('plan_id'))

        if not plan_data:
            return False, {
                    "message": "Plan not found."
                }

        # check if subscription with the plan and user id exists
        if sub_data := self.subscription_repo.get_by_plan_user_id(data.get('user_id'), data.get('plan_id')):
            if sub_data.get('status') != 'pending':
                return False, {
                    "message": "User already has an active subscription."
                }
        
        # create a subscription collection if user doesn't have before
        subscription = dict()
        if not sub_data:
            subscription_data = Subscription(**data)
            subscription = self.subscription_repo.create_subscription(subscription_data.to_bson())

        # initialize paystack payment
        response: Dict = paystack.transaction.initialize(
            plan=plan_data.get('plan_code'),
            email=user_data.get('email'),
            amount=plan_data.get('Price')
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
                "subscription_id": str(subscription.get('_id', "")),
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

    def upgrade_subscription(self, plan_id: str, user_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
            Upgrades to a new subscription or enables former subscription
        """
        # check if any subscription has the plan id
        sub_data = self.subscription_repo.get_by_plan_user_id(user_id=user_id, plan_id=plan_id)
        if not sub_data:
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
            
            # update plan_id field in user model
            self.user_repo.find_and_update_user({ "_id": ObjectId(user_id) }, 
                                                {
                                                    "plan_id": ObjectId(plan_id)
                                                })
            
            # create a subscription
            data = dict()
            data['user_id'] = user_id
            data['plan_id'] = plan_id
            data['email'] = user_data.get('email')

            subscription_data = Subscription(**data)
            subscription = self.subscription_repo.create_subscription(subscription_data.to_bson())

            # initialize a transaction for the new subscription
            response: Dict = paystack.transaction.initialize(
                plan=plan_data.get('plan_code'),
                email=user_data.get('email'),
                amount=plan_data.get('Price')
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
                    "subscription_id": str(subscription.get('_id', "")),
                    "reference": response_data.get('reference')
                },
                "status": 200
            }
        
        # there is subscription data, then it must be disabled
        sub_parsed_data = Subscription(**sub_data)

        # update plan_id field in user model
        self.user_repo.find_and_update_user({ "_id": ObjectId(user_id) }, 
                                            {
                                                "plan_id": ObjectId(plan_id)
                                            })

        # enable subscription
        self.subscription_repo.find_and_update_subscription({ "user_id": ObjectId(user_id), "plan_id": ObjectId(plan_id) }, 
                                                            {
                                                                "status": "enabled"
                                                            })
        
        response = paystack.subscription.enable(
            code=sub_parsed_data.subscription_code,
            token=sub_parsed_data.email_token
        )

        return response.get("status"), {
            "message": response.get("message"),
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
    
    def initialize_payment(self, amount: int, email: str) -> Tuple[bool, Dict[str, Any]]:
        """
            Initializes a payment
        """
        response: Dict = paystack.transaction.initialize(
                email=email,
                amount=amount
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
            "message": "Subscription deleted successfully."
        }