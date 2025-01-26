from flask import Blueprint, abort, jsonify, request, current_app, g
from app.usecases import PaymentHistoryUseCase
from app.utils.decorators import admin_required, auth_required
from typing import Dict

payment_history_bp = Blueprint('payment_history', __name__)

@payment_history_bp.get('/all', strict_slashes=False)
@admin_required()
def get_all_payment_histories():
    try:
        usecase: PaymentHistoryUseCase = payment_history_bp.payment_history_usecase
        success, resp_data = usecase.get_all_payment_history()
        
        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), 400

        return jsonify({"error": not success, "data": resp_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get all payment histories: {str(e)}")
        abort(500, 'Failed to get all payment histories')

@payment_history_bp.get('/all/user', strict_slashes=False)
@auth_required()
def get_all_payment_histories_by_user():
    try:
        user_id = g.user_id
        usecase: PaymentHistoryUseCase = payment_history_bp.payment_history_usecase
        success, resp_data = usecase.get_all_payment_history_by_user_id(user_id=user_id)
        
        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), 400

        return jsonify({"error": not success, "data": resp_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get all payment histories: {str(e)}")
        abort(500, 'Failed to get all payment histories')