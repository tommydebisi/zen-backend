from flask import Blueprint
from flask import abort, jsonify, current_app
from app.utils.decorators import admin_required
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