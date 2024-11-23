from flask import Blueprint
from flask import abort, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from app.usecases.user.user import UserUseCase
from typing import Dict


user_bp = Blueprint('user', __name__)

@user_bp.get('/', strict_slashes=False)
@jwt_required()
def get_user():
    claims = get_jwt()

    try:
        usecase: UserUseCase = user_bp.user_use_case
        success, resp_data = usecase.get_user(claims['sub'].get('user_id'))
        
        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), 400

        return jsonify({"error": not success, "data": resp_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get user: {str(e)}")
        abort(500, 'Failed to get user')