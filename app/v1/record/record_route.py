from flask import Blueprint, abort, jsonify, request, current_app
from app.usecases import RecordUseCase
from app.utils.decorators import admin_required
from typing import Dict
from cloudinary.uploader import upload

record_bp = Blueprint('record', __name__)


@record_bp.post('/create', strict_slashes=False)
@admin_required()
def create_record():
    try:
        data: Dict = request.form.copy()

        # upload image
        image_file = request.files.get('image')
        if image_file:
            upload_result: Dict = upload(image_file)
            data["image_url"] = upload_result.get('secure_url')

        # create record
        usecase: RecordUseCase = record_bp.record_use_case
        success, resp_data = usecase.create_record(data)
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
        current_app.logger.error(f"Failed to create record: {str(e)}")
        abort(500, 'Failed to create record')


@record_bp.get('/<record_id>', strict_slashes=False)
@admin_required()
def get_record(record_id):
    try:
        usecase: RecordUseCase = record_bp.record_use_case
        success, resp_data = usecase.get_record_by_id(record_id)

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
        current_app.logger.error(f"Failed to get record: {str(e)}")
        abort(500, 'Failed to get record')


@record_bp.get('/all', strict_slashes=False)
def get_all_records():
    try:
        usecase: RecordUseCase = record_bp.record_use_case
        success, resp_data = usecase.get_all_records()

        return jsonify({
            "error": not success,
            "data": resp_data.get("data")
        }), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get all records: {str(e)}")
        abort(500, 'Failed to get all records')


@record_bp.put('/update/<record_id>', strict_slashes=False)
@admin_required()
def update_record(record_id: str):
    """
    Update a record by its ID.
    Returns appropriate responses for various scenarios.
    """
    try:
        # Parse the request data
        request_data: Dict = request.form.to_dict(flat=True)

        # upload image
        image_file = request.files.get('image')
        if image_file:
            upload_result: Dict = upload(image_file)
            request_data["image_url"] = upload_result.get('secure_url')

        usecase: RecordUseCase = record_bp.record_use_case
        success, resp_data = usecase.update_record(record_id, request_data)

        if not success:
            return jsonify({"error": True, "message": resp_data.get("message")}), 404

        return jsonify({"error": False, "message": resp_data.get("message")}), 200

    except RuntimeError as e:
        current_app.logger.error(f"Failed to update record: {str(e)}")
        return jsonify({"error": True, "message": "Internal server error"}), 500

    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        abort(500, 'Unexpected error occurred')


@record_bp.delete('/delete/<record_id>', strict_slashes=False)
@admin_required()
def delete_record(record_id):
    """
    Delete a record by its ID.
    Returns a 404 error if the record is not found.
    """
    try:
        usecase: RecordUseCase = record_bp.record_use_case
        success, resp_data = usecase.delete_record(record_id)

        if not success:
            return jsonify({
                "error": True,
                "message": resp_data.get("message")
            }), 404

        return jsonify({
            "error": False,
            "message": resp_data.get("message")
        }), 200

    except RuntimeError as e:
        current_app.logger.error(f"Failed to delete record: {str(e)}")
        return jsonify({
            "error": True,
            "message": "Internal server error"
        }), 500