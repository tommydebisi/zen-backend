from flask import Blueprint
from flask import abort, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from pydantic import ValidationError
from app.utils.utils import validateEmail
from app.usecases.user.user import UserUseCase
from app.usecases.token.token import TokenUseCase
from app.usecases.subscription.subscription import SubscriptionUseCase
from typing import Dict
import cloudinary.uploader as uploader

auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/register/profile', strict_slashes=False)
def register():
    try:
        data: Dict = request.form.copy()

        email = data.get('email')
        password = data.get('Password')

        if not email or not password:
            abort(400, 'email and Password are required')
        if not validateEmail(email):
            abort(400, 'Invalid email address')

        image_file = request.files.get('Passport')
        if image_file:
            upload_result = uploader.upload(image_file)
            data["image_url"] = upload_result.get('secure_url')


        # register user
        usecase: UserUseCase = auth_bp.user_use_case
        success, result_data = usecase.register_user(data)
        status_code = 201 if success else 400

        if not success:
            return jsonify({"error": not success, "message": result_data.get("message")}), status_code

        return jsonify({"error": not success, "message": result_data.get("message"), "data": result_data.get("data")}), status_code
    except ValidationError as e:
        current_app.logger.error(f"Validation error: {e.json()}")
        abort(400, 'Invalid request data')
    except Exception as e:
        current_app.logger.error(f"Failed to register user: {str(e)}")
        abort(500, 'Failed to register user')

@auth_bp.put('/register/acknowledgment/<user_id>', strict_slashes=False)
def acknowledge(user_id):
    try:
        data: Dict = request.get_json()

        acknowledgement = data.get('member_acknowledgement')

        if not acknowledgement:
            abort(400, 'acknowledgement is required')

        # register user
        usecase: UserUseCase = auth_bp.user_use_case
        success, message = usecase.update_user_with_id(user_id, data)
        status_code = 200 if success else 400

        return jsonify({"error": not success, "message": message}), status_code
    except Exception as e:
        current_app.logger.error(f"Failed to register user: {str(e)}")
        abort(500, 'Failed to register user')

@auth_bp.put('/register/conduct/<user_id>', strict_slashes=False)
def archery_conduct(user_id):
    try:
        data: Dict = request.get_json()

        risks = data.get('acknowledge_risks')
        consent = data.get('consent_to_media')
        initials = data.get('initials')

        if not risks or not consent or not initials:
            abort(400, 'acknowledge_risks, consent_to_media, and intials are required')

        # register user
        usecase: UserUseCase = auth_bp.user_use_case
        success, message = usecase.update_user_with_id(user_id, data)
        status_code = 200 if success else 400

        return jsonify({"error": not success, "message": message}), status_code
    except Exception as e:
        current_app.logger.error(f"Failed to register user: {str(e)}")
        abort(500, 'Failed to register user')

@auth_bp.put('/register/subscribe/<user_id>', strict_slashes=False)
def subscribe(user_id):
    try:
        data: Dict = request.get_json()
        data['user_id'] = user_id

        # register user subscription
        usecase: SubscriptionUseCase = auth_bp.subscription_use_case
        success, message, result_data = usecase.create_subscription(data)
        status_code = 200 if success else 400

        return jsonify({"error": not success, "message": message, "data": result_data}), status_code
    except Exception as e:
        current_app.logger.error(f"Failed to register user: {str(e)}")
        abort(500, 'Failed to register user')

@auth_bp.post('/login', strict_slashes=False)
def login():
    try:
        data: Dict = request.get_json()

        email = data.get('email')
        password = data.get('Password')

        if not email or not password:
            abort(400, 'email and Password are required')

        # login user
        usecase: UserUseCase = auth_bp.user_use_case
        success, login_data = usecase.login_user(email, password)
        status_code = 200 if success else 400

        if not success:
            return jsonify({"error": True, "message": login_data.get("message")}), status_code

        return jsonify({"error": False, "message": login_data.get("message"), "tokens": login_data.get("data")}), status_code
    except Exception as e:
        current_app.logger.error(f"Failed to login user: {str(e)}")
        abort(500, 'Failed to login user')

@auth_bp.get('/users', strict_slashes=False)
@jwt_required()
def get_users():
    try:
        usecase: UserUseCase = auth_bp.user_use_case
        users = usecase.get_all_users()
        return jsonify({"error": False, "users": users}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to fetch users: {str(e)}")
        abort(500, 'Failed to fetch users')

@auth_bp.get("/refresh", strict_slashes=False)
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()

    usecase: UserUseCase = auth_bp.user_use_case
    success, new_access_token = usecase.refresh_token(identity)

    if not success:
        abort(500, 'Failed to refresh token')

    return jsonify({"error": False, "access": new_access_token}), 200

@auth_bp.get("/logout", strict_slashes=False)
@jwt_required(verify_type=False) # access both access and refresh tokens
def logout():
    jwt_data = get_jwt()
    jti = jwt_data["jti"]
    token_type = jwt_data["type"]

    try:
        usecase: TokenUseCase = auth_bp.token_use_case
        # create blacklisted token
        success = usecase.create_token({"jti": jti})
        if not success: 
            abort(500, 'Failed to logout user')

        return jsonify({"error": False, "message": f"{token_type} token revoked successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Failed to logout user: {str(e)}")
        abort(500, 'Failed to logout user')