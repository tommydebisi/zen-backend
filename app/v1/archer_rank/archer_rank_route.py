from flask import Blueprint, abort, jsonify, request, current_app
from app.usecases import ArcherRankUseCase
from app.utils.decorators import admin_required
from typing import Dict
from cloudinary.uploader import upload

archer_rank_bp = Blueprint('archer_rank', __name__)


@archer_rank_bp.post('/create', strict_slashes=False)
@admin_required()
def create_archer_rank():
    try:
        data: Dict = request.form.copy()

        # upload image
        image_file = request.files.get('image')
        if image_file:
            upload_result: Dict = upload(image_file)
            data["image_url"] = upload_result.get('secure_url')

        # create archer rank
        usecase: ArcherRankUseCase = archer_rank_bp.archer_rank_use_case
        success, resp_data = usecase.create_archer_rank(data)
        if not success:
            return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
            }), 400

        return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
                "data": resp_data.get("data")
            }), 201

    except Exception as e:
        current_app.logger.error(f"Failed to create archer rank: {str(e)}")
        abort(500, 'Failed to create archer rank')

@archer_rank_bp.get('/<archer_rank_id>', strict_slashes=False)
@admin_required()
def get_archer_rank(archer_rank_id):
    try:
        usecase: ArcherRankUseCase = archer_rank_bp.archer_rank_use_case
        success, resp_data = usecase.get_archer_rank_by_id(archer_rank_id)

        if not success:
            return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
            }), 404

        return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
                "data": resp_data.get("data")
            }), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get archer rank: {str(e)}")
        abort(500, 'Failed to get archer rank')


@archer_rank_bp.get('/all', strict_slashes=False)
def get_all_archer_ranks():
    try:
        usecase: ArcherRankUseCase = archer_rank_bp.archer_rank_use_case
        success, resp_data = usecase.get_all_archer_ranks()

        if not success:
            return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
            }), 404

        return jsonify({
                "error": not success,
                "message": resp_data.get("message"),
                "data": resp_data.get("data")
            }), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get all archer ranks: {str(e)}")
        abort(500, 'Failed to get all archer ranks')


@archer_rank_bp.put('/update/<archer_rank_id>', strict_slashes=False)
@admin_required()
def update_archer_rank(archer_rank_id):
    try:
        data: Dict = request.get_json()

        usecase: ArcherRankUseCase = archer_rank_bp.archer_rank_use_case
        success, resp_data = usecase.update_archer_rank(archer_rank_id, data)

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
        current_app.logger.error(f"Failed to update archer rank: {str(e)}")
        abort(500, 'Failed to update archer rank')


@archer_rank_bp.delete('/delete/<archer_rank_id>', strict_slashes=False)
@admin_required()
def delete_archer_rank(archer_rank_id):
    try:
        usecase: ArcherRankUseCase = archer_rank_bp.archer_rank_use_case
        success, resp_data = usecase.delete_archer_rank(archer_rank_id)

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
        current_app.logger.error(f"Failed to delete archer rank: {str(e)}")
        abort(500, 'Failed to delete archer rank')