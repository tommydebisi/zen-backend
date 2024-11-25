from flask import Blueprint, abort, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from app.usecases.team.team import TeamUseCase
from typing import Dict
from cloudinary.uploader import upload

team_bp = Blueprint('team', __name__)


@team_bp.post('/create', strict_slashes=False)
def create_team():
    try:
        data: Dict = request.form.copy()

        # upload image
        image_file = request.files.get('image')
        if image_file:
            upload_result: Dict = upload(image_file)
            data["image_url"] = upload_result.get('secure_url')

        # create team
        usecase: TeamUseCase = team_bp.team_use_case
        success, resp_data = usecase.create_team(data)

        return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
                "data": resp_data.get("data")
            }), 201

    except Exception as e:
        current_app.logger.error(f"Failed to create team: {str(e)}")
        abort(500, 'Failed to create team')


@team_bp.get('/<team_id>', strict_slashes=False)
def get_team(team_id):
    try:
        usecase: TeamUseCase = team_bp.team_use_case
        success, resp_data = usecase.get_team_by_id(team_id)

        return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
                "data": resp_data.get("data")
            }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get team: {str(e)}")
        abort(500, 'Failed to get team')

@team_bp.get('/all', strict_slashes=False)
def get_all_teams():
    try:
        usecase: TeamUseCase = team_bp.team_use_case
        success, resp_data = usecase.get_all_teams()

        if not success:
            return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
            }), 400

        return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
                "data": resp_data.get("data")
            }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to get all teams: {str(e)}")
        abort(500, 'Failed to get all teams')

@team_bp.put('/update/<team_id>', strict_slashes=False)
def update_team(team_id):
    try:
        data: Dict = request.form.copy()

        # upload image
        image_file = request.files.get('image')
        if image_file:
            upload_result: Dict = upload(image_file)
            data["image_url"] = upload_result.get('secure_url')

        # update team
        usecase: TeamUseCase = team_bp.team_use_case
        success, resp_data = usecase.update_team(team_id, data)

        return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
            }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to update team: {str(e)}")
        abort(500, 'Failed to update team')

@team_bp.delete('/delete/<team_id>', strict_slashes=False)
def delete_team(team_id):
    try:
        usecase: TeamUseCase = team_bp.team_use_case
        success, resp_data = usecase.delete_team(team_id)

        return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
            }), 200

    except Exception as e:
        current_app.logger.error(f"Failed to delete team: {str(e)}")
        abort(500, 'Failed to delete team')