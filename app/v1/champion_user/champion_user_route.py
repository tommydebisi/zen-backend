from flask import abort, jsonify, request, current_app, Blueprint
from pydantic import ValidationError
from typing import Dict
from app.usecases import ChampionUserUseCase
from app.utils.decorators import admin_required

champion_user_bp = Blueprint('champion_user', __name__)


@champion_user_bp.post('/create', strict_slashes=False)
def create_champion_user():
    try:
        data: Dict = request.form.copy()

        # create champion user
        usecase: ChampionUserUseCase = champion_user_bp.champion_user_use_case
        success, result_data = usecase.create_champion_user(data)
        status_code = 201 if success else 400

        if not success:
            return jsonify({"error": not success, "message": result_data.get("message")}), status_code

        return jsonify({"error": not success, "message": result_data.get("message"), "data": result_data.get("data")}), status_code
    except ValidationError as e:
        current_app.logger.error(f"Validation error: {e.json()}")
        abort(400, 'Invalid request data')
    except Exception as e:
        current_app.logger.error(f"Failed to create champion user: {str(e)}")
        abort(500, 'Failed to create champion user')

@champion_user_bp.put('/update/<champion_user_id>', strict_slashes=False)
def update_champion_user(champion_user_id: str):
    try:
        data = request.get_json()

        usecase: ChampionUserUseCase = champion_user_bp.champion_user_use_case
        success, resp_data = usecase.update_champion_user(champion_user_id, data)

        if not success:
            return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
            }), 400

        return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
            }), 200
    except Exception as e:
        current_app.logger.error(f"Failed to update Champion user: {str(e)}")
        abort(500, 'Failed to update Champion user')

@champion_user_bp.put('/pay/<champion_user_id>', strict_slashes=False)
def initialize_champion_user_payment(champion_user_id: str):
    try:
        data: Dict = request.get_json()

        callback_url = data.get('callback_url')
        if not callback_url:
            abort(400, 'call back url required')


        usecase: ChampionUserUseCase = champion_user_bp.champion_user_use_case
        success, resp_data = usecase.champion_user_payment(champion_user_id=champion_user_id, data=data)

        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), 400

        return jsonify({"error": not success, "message": resp_data.get('message'), "data": resp_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to initialize payment for Champion User: {str(e)}")
        abort(500, 'Failed to initialize payment for Champion User')


@champion_user_bp.get('/all', strict_slashes=False)
@admin_required()
def get_all_champion_users():
    try:
        usecase: ChampionUserUseCase = champion_user_bp.champion_user_use_case
        success, result_data = usecase.get_all_champion_users()

        if not success:
            return jsonify({"error": not success, "message": result_data.get("message")}), 400

        return jsonify({"error": not success, "message": result_data.get("message"), "data": result_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get all Champion users: {str(e)}")
        abort(500, 'Failed to get all Champion users')

@champion_user_bp.put('/update/payment/<champion_user_id>', strict_slashes=False)
@admin_required()
def update_champion_user_payment_status(champion_user_id: str):
    try:
        data: Dict = request.get_json()

        usecase: ChampionUserUseCase = champion_user_bp.champion_user_use_case
        success, resp_data = usecase.update_champion_user_payment_status(champion_user_id, data)

        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), 400

        return jsonify({"error": not success, "message": resp_data.get("message")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to update Champion user payment status: {str(e)}")
        abort(500, 'Failed to update Champion user payment status')