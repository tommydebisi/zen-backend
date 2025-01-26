from flask import Blueprint, abort, jsonify, request, current_app

from typing import Dict
from cloudinary.uploader import upload
import hmac
import hashlib
from app.config  import config
from app.services.paystack.payment import PayStackPayment

payment_bp = Blueprint('payment', __name__)

# Paystack's IP addresses to whitelist
PAYSTACK_WHITELISTED_IPS = [
    "52.31.139.75",
    "52.49.173.169",
    "52.214.14.220"
]

def is_ip_whitelisted(ip):
    """Check if the incoming IP is in the whitelist."""
    return ip in PAYSTACK_WHITELISTED_IPS

@payment_bp.before_request
def check_ip_whitelist():
    """Middleware to validate the IP address of incoming requests."""
    if request.endpoint == 'paystack_webhook':
        # Get the remote IP address of the request
        remote_ip = request.remote_addr

        # Check if the IP is whitelisted
        if not is_ip_whitelisted(remote_ip):
            return jsonify({"error": True, "message": "Forbidden: IP not allowed"}), 403

@payment_bp.post('/webhook', strict_slashes=False)
def payment_webhook():
    try:
        # Step 1: Validate Paystack signature
        signature = request.headers.get('X-Paystack-Signature')
        if not signature:
            return jsonify({"error": True, "message": "Signature missing"}), 400

        payload = request.get_data()
        expected_signature = hmac.new(
            config.PAYSTACK_SECRET_KEY.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()

        if signature != expected_signature:
            return jsonify({"error": True, "message": "Invalid signature"}), 400
        
        # Step 2: Parse the payload
        event_data: Dict = request.get_json()
        
        event_type = event_data.get("event")
        event_data = event_data.get("data")

        print(f"Event type {event_type}")

        # handle events
        success, resp_data = PayStackPayment.paymentHandler(event_type=event_type, data=event_data)
        # print(event_type)

        if not success:
            return jsonify({
                'error': not success, 
                'message': resp_data.get('message')
                }), 400
        return jsonify({
                'error': not success, 
                'message': resp_data.get('message')
                }), 200
    except Exception as e:
        current_app.logger.error(f"Failed to perform pay action: {str(e)}")
        abort(500, 'Failed to perform pay action')
