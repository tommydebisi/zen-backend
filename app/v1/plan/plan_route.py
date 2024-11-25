from flask import Blueprint, abort, jsonify, request, current_app
# from flask_jwt_extended import jwt_required
from app.usecases.plan.plan import PlanUseCase
from typing import Dict

plan_bp = Blueprint('plan', __name__)


@plan_bp.post('/create', strict_slashes=False)
def create_plan():
    try:
        request_data: Dict = request.get_json()
    
        usecase: PlanUseCase = plan_bp.plan_use_case
        success, resp_data = usecase.create_plan(request_data)
        if not success:
            return jsonify({"error": not success, "data": resp_data.get("message")}), 400

        return jsonify({"error": not success, "data": resp_data.get("message")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to create plan: {str(e)}")
        abort(500, 'Failed to create plan')

@plan_bp.get('/all', strict_slashes=False)
def get_all_plans():
    try:
        usecase: PlanUseCase = plan_bp.plan_use_case
        success, resp_data = usecase.get_all_plans()

        return jsonify({"error": not success, "data": resp_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get all plans: {str(e)}")
        abort(500, 'Failed to get all plans')

@plan_bp.put('/update/<plan_id>', strict_slashes=False)
def update_plan(plan_id):
    try:
        request_data: Dict = request.get_json()
        request_data['plan_id'] = plan_id

        usecase: PlanUseCase = plan_bp.plan_use_case
        success, resp_data = usecase.update_plan(plan_id, request_data)

        return jsonify({"error": not success, "data": resp_data.get("message")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to update plan: {str(e)}")
        abort(500, 'Failed to update plan')


@plan_bp.delete('/delete/<plan_id>', strict_slashes=False)
def delete_plan(plan_id):
    try:
        usecase: PlanUseCase = plan_bp.plan_use_case
        success, resp_data = usecase.delete_plan(plan_id)

        return jsonify({"error": not success, "data": resp_data.get("message")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to delete plan: {str(e)}")
        abort(500, 'Failed to delete plan')