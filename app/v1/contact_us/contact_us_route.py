from flask import Blueprint
from flask import abort, jsonify, request, current_app
from app.usecases import ContactUsUseCase
from typing import Dict

contact_us_bp = Blueprint('contact_us', __name__)

@contact_us_bp.post('/send_message', strict_slashes=False)
def send_contact_message():
    try:
        usecase: ContactUsUseCase = contact_us_bp.contact_us_use_case
        data: Dict[str, str] = request.get_json()
        success, resp_data = usecase.send_contact_message(data)

        return jsonify({"error": not success, "data": resp_data.get("message")}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to send contact message: {str(e)}")
        abort(500, 'Failed to send contact message')