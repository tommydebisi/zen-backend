from flask import Blueprint
from flask import abort, jsonify, current_app, g
from app.utils.decorators import auth_required
from app.usecases import UserUseCase
from typing import Dict


user_bp = Blueprint('user', __name__)

@user_bp.get('/', strict_slashes=False)
@auth_required()
def get_user():
    try:
        usecase: UserUseCase = user_bp.user_use_case
        success, resp_data = usecase.get_user(g.user_id)
        
        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), 400

        return jsonify({"error": not success, "data": resp_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get user: {str(e)}")
        abort(500, 'Failed to get user')