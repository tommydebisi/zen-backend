from flask import Blueprint, abort, jsonify, request, current_app
from app.usecases import PlanUseCase
from app.utils.decorators import admin_required
from typing import Dict

plan_bp = Blueprint('plan', __name__)


@plan_bp.post('/create', strict_slashes=False)
@admin_required()
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
@admin_required()
def update_plan(plan_id):
    """
    Update a plan by its ID.
    Returns appropriate responses for various scenarios.
    """
    try:
        # Parse the request data
        request_data: Dict = request.get_json()

        usecase: PlanUseCase = plan_bp.plan_use_case
        success, resp_data = usecase.update_plan(plan_id, request_data)

        if not success:
            return jsonify({"error": True, "message": resp_data.get("message")}), 404

        return jsonify({"error": False, "message": resp_data.get("message")}), 200

    except RuntimeError as e:
        current_app.logger.error(f"Failed to update plan: {str(e)}")
        return jsonify({"error": True, "message": "Internal server error"}), 500

    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        abort(500, 'Unexpected error occurred')


@plan_bp.delete('/delete/<plan_id>', strict_slashes=False)
@admin_required()
def delete_plan(plan_id):
    """
    Delete a plan by its ID.
    Returns a 404 error if the plan is not found.
    """
    try:
        usecase: PlanUseCase = plan_bp.plan_use_case
        success, resp_data = usecase.delete_plan(plan_id)

        if not success:
            return jsonify({"error": True, "message": resp_data.get("message")}), 404

        return jsonify({"error": False, "message": resp_data.get("message")}), 200

    except RuntimeError as e:
        current_app.logger.error(f"Failed to delete plan: {str(e)}")
        return jsonify({"error": True, "message": "Internal server error"}), 500

    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        abort(500, 'Unexpected error occurred')
