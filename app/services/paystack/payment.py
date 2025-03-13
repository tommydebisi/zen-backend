from typing import Dict, Callable, Tuple, Any
from flask import current_app
from app.services.paystack.setup import paystack
from app.services.paystack.models import ChargeSuccessData, SubscriptionCreateData, InvoiceUpdateData
from app.extensions import (
    UserRepository,
    SubscriptionRepository,
    PaymentHistoryRepository,
    PlanRepository,
    WalkInRepository,
    ChampionUserRepository
    )
from app.database.models.payment_history import PaymentHistory
from app.database.models.walk_in import WalkIn
from datetime import datetime


class PayStackPayment:
    @staticmethod
    def get_db():
        """
        Get the database instance from the Flask app context.
        """
        return current_app.extensions['database']

    @staticmethod
    def paymentHandler(event_type: str, data: Dict) -> Tuple[bool, Dict[str, Any]]:
        event_handlers: Dict[str, Callable[[Dict], None]] = {
            'charge.success': PayStackPayment.handle_charge_success,
            'subscription.create': PayStackPayment.handle_subscription_create,
            'subscription.disable': PayStackPayment.handle_subscription_disable,
            'invoice.update': PayStackPayment.handle_invoice_updated,
            'subscription.not_renew': PayStackPayment.handle_subscription_not_renew
        }

        # Get the handler for the event type
        handler = event_handlers.get(event_type)

        if handler:
            try:
                response = handler(data)
                return response
            except Exception as e:
                # Log the error for debugging
                current_app.logger.error(f"Error handling event '{event_type}': {e}")
        else:
            current_app.logger.error(f"No handler found for event type: {event_type}")
            current_app.logger.info(f"{data}")
            return True, {"message": "purposely unhandled"}

    @staticmethod
    def handle_charge_success(data: Dict) -> Tuple[bool, Dict[str, Any]]:
        """
            Handles the charge success event
        """
        success_data = ChargeSuccessData(**data)
        # init user repo
        user_repo = UserRepository(PayStackPayment.get_db())
        payment_history_repo = PaymentHistoryRepository(PayStackPayment.get_db())
        plan_repo = PlanRepository(PayStackPayment.get_db())
        walk_in_repo = WalkInRepository(PayStackPayment.get_db())
        champion_user_repo = ChampionUserRepository(PayStackPayment.get_db())

        # check if metadata is present, then it is a walkIn sub
        if type(success_data.metadata) is dict and success_data.metadata.get('custom'):
            if success_data.metadata['custom'].get('type') == "walkin":
                entry_date = success_data.metadata['custom'].get('entry_date')
                walk_in_data = {
                    "email": success_data.customer.email,
                    "amount": success_data.amount // 100,
                    "entry_date": entry_date
                }

                parsed_walk_in_data = WalkIn(**walk_in_data)
                walk_in_repo.create_walk_in(parsed_walk_in_data.to_bson())
            elif success_data.metadata['custom'].get('type') == "competition":
                unique_id = success_data.metadata['custom'].get('unique_id')

                # find and update champion user by unique id
                champion_user_repo.find_and_update_champion_user({ "unique_id": unique_id }, { "status": "paid" })
            elif success_data.metadata['custom'].get('type') == "subscription":
                plan_code = success_data.metadata['custom'].get('plan_code')
                customer_code = success_data.metadata['custom'].get('customer_code')

                # create a subscription for the user
                paystack.subscription.create(
                    customer=customer_code,
                    plan=plan_code,
                    authorization=success_data.authorization.authorization_code
                )

                # get the user by customer id
                user_data = user_repo.get_by_customer_code(customer_code)

                if user_data.get('status') == 'Payment':
                    # find and update the user to done
                    result = user_repo.find_and_update_user({ "customer_code": customer_code }, 
                                                    {
                                                        "auth_code": success_data.authorization.authorization_code,
                                                        "status": "done"
                                                    })
                    if result.matched_count == 0:
                            current_app.logger.info(f"Subscription not found.")
                            return False, {"message": "Subscription not found."}

                # find plan by plan code
                plan_paid_for = plan_repo.get_by_plan_code(plan_code=plan_code)

                history_data = {
                        "amount": success_data.amount,
                        "name": f"{user_data.get('firstName')} {user_data.get('lastName')}",
                        "reference": success_data.reference,
                        "payment_date": success_data.paid_at,
                        "status": success_data.status,
                        "user_id": user_data.get('_id'),
                        "plan_id": plan_paid_for.get('_id')
                    }
                history_parsed_data = PaymentHistory(**history_data)

                # update the paymentHistory
                result = payment_history_repo.create_payment_history(history_parsed_data.to_bson())

            if success_data.metadata['custom'].get('type') != "subscription":
                # update payment history
                history_data = {
                    "amount": success_data.amount,
                    "email": success_data.customer.email,
                    "reference": success_data.reference,
                    "payment_date": success_data.paid_at,
                    "status": success_data.status
                }
                history_parsed_data = PaymentHistory(**history_data)

                # update the paymentHistory
                result = payment_history_repo.create_payment_history(history_parsed_data.to_bson())

            return True, {
                "message": "Customer made a payment!"
            }

        # get the user by customer id
        user_data = user_repo.get_by_customer_code(success_data.customer.customer_code)

        # find plan by plan code
        plan_paid_for = plan_repo.get_by_plan_code(plan_code=success_data.plan.plan_code)

        history_data = {
                "amount": success_data.amount,
                "name": f"{success_data.customer.first_name} {success_data.customer.last_name}",
                "reference": success_data.reference,
                "payment_date": success_data.paid_at,
                "status": success_data.status,
                "user_id": user_data.get('_id'),
                "plan_id": plan_paid_for.get('_id')
            }
        history_parsed_data = PaymentHistory(**history_data)

        # update the paymentHistory
        result = payment_history_repo.create_payment_history(history_parsed_data.to_bson())

        return True, {
            "message": "Customer made a payment!"
        }

    @staticmethod
    def handle_subscription_create(data: Dict) -> Tuple[bool, Dict[str, Any]]:
        """
            Handles the subscription create event
        """
        success_data  = SubscriptionCreateData(**data)
        # init repo
        user_repo = UserRepository(PayStackPayment.get_db())
        subscription_repo = SubscriptionRepository(PayStackPayment.get_db())
        plan_repo = PlanRepository(PayStackPayment.get_db())

        # get the user by customer id
        user_data = user_repo.get_by_customer_code(success_data.customer.customer_code)
        plan_data = plan_repo.get_by_plan_code(success_data.plan.plan_code)

        # check if the current planId in user data is same as the one in the create event
        if str(user_data.get('plan_id')) != str(plan_data.get('_id')):
            # this is an upgrade in subscription
            # get the previous subnscription and disable it
            previous_sub = subscription_repo.get_by_plan_user_id(user_id=str(user_data.get('_id')), plan_id=str(user_data.get('plan_id')))
            # disable subscription
            paystack.subscription.disable(
                code=previous_sub.get('subscription_code'),
                token=previous_sub.get('email_token')
            )

            # update user id
            user_repo.find_and_update_user({ '_id': user_data.get('_id') }, {
                "plan_id": plan_data.get('_id'),
                "updated_at": datetime.now()
            })

        # data to create subscription
        sub_data = {
            "user_id": user_data.get('_id'),
            "plan_id": plan_data.get('_id'),
            "email": success_data.customer.email,
            "email_token": success_data.email_token,
            "subscription_code": success_data.subscription_code,
            "start_date": success_data.createdAt,
            "end_date": success_data.next_payment_date,
            "status": success_data.status
        }

        # create the subscription with the plan selected
        result = subscription_repo.create_subscription(sub_data)

        if not result:
                    return False, {"message": "Subscription not created."}
        return True, {"message": "Subscription create success"}

    @staticmethod
    def handle_subscription_disable(data: Dict) -> Tuple[bool, Dict[str, Any]]:
        """
            Handles disabling of subscription
        """
        subscription_code = data.get('subscription_code')
        email_token = data.get('email_token')
        subscription_repo = SubscriptionRepository(PayStackPayment.get_db())

        #  delete subscription
        result = subscription_repo.find_and_cancel_subscription({
                "subscription_code": subscription_code,
                "email_token": email_token,
        }, status=data.get('status'))

        if result.matched_count == 0:
            return False, {
                    "message": "Subscription not found"
                }
        
        return True, {"message": "Subscription disable success"}

    @staticmethod
    def handle_invoice_updated(data: Dict) -> Tuple[bool, Dict[str, Any]]:
        """
            handles the invoice status of subscriptions
        """
        request_data = InvoiceUpdateData(**data)

        subscription_repo = SubscriptionRepository(PayStackPayment.get_db())
        user_repo = UserRepository(PayStackPayment.get_db())
        payment_history_repo = PaymentHistoryRepository(PayStackPayment.get_db())

        # get the subscription based on the subscription code and update status
        if request_data.subscription.status == "success":
            subscription_repo.find_and_update_subscription({ "subscription_code": request_data.subscription.subscription_code },
                                                            {
                                                                "status": request_data.status,
                                                                "start_date": request_data.period_start,
                                                                "end_date": request_data.period_end
                                                            })
        else:
            subscription_repo.find_and_update_subscription({ "subscription_code": request_data.subscription.subscription_code },
                                                            {
                                                                "status": request_data.status,
                                                            })
            
        # get user by customer code
        user_data = user_repo.get_by_customer_code(request_data.customer.customer_code)

        # create payment history
        history_data = {
                "amount": request_data.amount,
                "name": f"{request_data.customer.first_name} {request_data.customer.last_name}",
                "payment_date": request_data.paid_at,
                "status": request_data.status,
                "user_id": user_data.get('_id'),
                "plan_id": user_data.get('plan_id')
            }
        history_parsed_data = PaymentHistory(**history_data)

        # update the paymentHistory
        payment_history_repo.create_payment_history(history_parsed_data.to_bson())
        return True, {
            "message": "Payment was made or not!"
        }
    
    @staticmethod
    def handle_subscription_not_renew(data: Dict) -> Tuple[bool, Dict[str, Any]]:
        """
            handles the subscriptions not renew event
        """
        subscription_repo = SubscriptionRepository(PayStackPayment.get_db())


        subscription_code = data.get('subscription_code')
        email_token = data.get('email_token')
        status = data.get('status')
        end_date = data.get('next_payment_date')

        # find and update the subscription model to non-renewing
        subscription_repo.find_and_update_subscription(
            {
                "subscription_code": subscription_code,
                "email_token": email_token
            }, { "status": status, "end_date": end_date, "updated_at": datetime.now() }
        )

        return True, {
            "message": "Subscription was cancelled"
        }
