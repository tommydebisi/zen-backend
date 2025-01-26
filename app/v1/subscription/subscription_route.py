from flask import abort, jsonify, current_app, Blueprint, g, request
from app.utils.decorators import admin_required, auth_required
from app.usecases import SubscriptionUseCase
from typing import Dict

subscription_bp = Blueprint('subscription', __name__)


@subscription_bp.get('/all', strict_slashes=False)
@admin_required()
def get_all_subscriptions_with_user_details():
    try:
        usecase: SubscriptionUseCase = subscription_bp.subscription_use_case
        success, resp_data = usecase.get_all_subscriptions_with_user_details()
        
        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), 400

        return jsonify({"error": not success, "data": resp_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get all subscriptions: {str(e)}")
        abort(500, 'Failed to get all subscriptions')


@subscription_bp.put('/cancel/<subscription_id>', strict_slashes=False)
@auth_required()
def cancel_subscription(subscription_id: str):
    try:
        usecase: SubscriptionUseCase = subscription_bp.subscription_use_case
        success, resp_data = usecase.cancel_subscription(subscription_id=subscription_id)

        return jsonify({
            "error": not success,
            "message": resp_data.get("message")
            }), resp_data.get("status")
    except Exception as e:
        current_app.logger.error(f"Failed to cancel subscription: {str(e)}")
        abort(500, 'Failed to cancel subscription')


@subscription_bp.put('/renew/plan/<plan_id>', strict_slashes=False)
@auth_required()
def renew_subscription_plan(plan_id: str):
    try:
        user_id: str = g.user_id
        usecase: SubscriptionUseCase = subscription_bp.subscription_use_case
        success, resp_data = usecase.renew_plan(plan_id=plan_id, user_id=user_id)

        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), resp_data.get("status")

        return jsonify({"error": not success,
                        "message": resp_data.get("message"),
                        "data": resp_data.get("data", {})
                        }), resp_data.get("status")
    except Exception as e:
        current_app.logger.error(f"Failed to renew subscription plan: {str(e)}")
        abort(500, 'Failed to renew subscription plan')


@subscription_bp.put('/upgrade/plan/<plan_id>', strict_slashes=False)
@auth_required()
def upgrade_subscription_plan(plan_id: str):
    try:
        user_id: str = g.user_id
        usecase: SubscriptionUseCase = subscription_bp.subscription_use_case
        success, resp_data = usecase.upgrade_subscription(plan_id=plan_id, user_id=user_id)

        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), resp_data.get("status")

        return jsonify({"error": not success,
                        "message": resp_data.get("message"),
                        "data": resp_data.get("data")
                        }), resp_data.get("status")
    except Exception as e:
        current_app.logger.error(f"Failed to upgrade subscription plan: {str(e)}")
        abort(500, 'Failed to upgrade subscription plan')

@subscription_bp.post('/pay', strict_slashes=False)
def initialize_payment():
    try:
        request_data: Dict = request.get_json()
        usecase: SubscriptionUseCase = subscription_bp.subscription_use_case
        success, resp_data = usecase.initialize_payment(request_data.get('amount') * 100, request_data.get('email'))

        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), 400

        return jsonify({"error": not success, "data": resp_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to initialize payment: {str(e)}")
        abort(500, 'Failed to initialize payment')

@subscription_bp.get('/verify/<reference>', strict_slashes=False)
def verify_payment(reference: str):
    try:
        usecase: SubscriptionUseCase = subscription_bp.subscription_use_case
        success, resp_data = usecase.verify_payment(reference=reference)

        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), 400

        return jsonify({"error": not success, "data": resp_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to initialize payment: {str(e)}")
        abort(500, 'Failed to initialize payment')