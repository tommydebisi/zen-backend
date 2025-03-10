from flask import abort, jsonify, request, current_app, Blueprint
from pydantic import ValidationError
from typing import Dict
from app.usecases import FileUploadUseCase

file_upload_bp = Blueprint('file_upload', __name__)

@file_upload_bp.post('/upload', strict_slashes=False)
def upload_file():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"error": True, "message": "file not found"}), 400

        usecase: FileUploadUseCase = file_upload_bp.file_upload_use_case
        success, resp_data = usecase.upload(file)

        if not success:
            return jsonify({"error": not success, "message": resp_data.get("message")}), 400

        return jsonify({"error": not success, "message": resp_data.get("message"), "data": resp_data.get("data")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to upload file: {str(e)}")
        abort(500, 'Failed to upload file')