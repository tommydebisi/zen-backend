from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import (
    NoAuthorizationError,
    InvalidHeaderError,
    RevokedTokenError,
    WrongTokenError,
    FreshTokenRequired,
)
from jwt.exceptions import ExpiredSignatureError
from functools import wraps
from flask import jsonify, g

def admin_required():
    """
    Decorator to restrict access to admin-only routes and handle JWT-related errors manually.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Verify the JWT token
                verify_jwt_in_request()

                # Extract user identity
                user_data = get_jwt_identity()
                g.user_id = user_data.get("user_id")
                g.role = user_data.get("role")

                # Role check
                if g.role != "admin":
                    return jsonify({"error": True, "message": "Admin access required"}), 403

            except ExpiredSignatureError:
                return jsonify({"error": True, "message": "Token has expired"}), 401
            except NoAuthorizationError:
                return jsonify({"error": True, "message": "Missing token"}), 401
            except InvalidHeaderError:
                return jsonify({"error": True, "message": "Invalid token header"}), 401
            except RevokedTokenError:
                return jsonify({"error": True, "message": "Token has been revoked"}), 401
            except WrongTokenError:
                return jsonify({"error": True, "message": "Wrong token type"}), 401
            except FreshTokenRequired:
                return jsonify({"error": True, "message": "Fresh token required"}), 401
            except Exception as e:
                # Catch all other unexpected exceptions
                return jsonify({"error": True, "message": f"Unexpected error: {str(e)}"}), 500

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def auth_required():
    """
    Decorator to allow access to authenticated users (any role) and handle JWT-related errors manually.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Verify the JWT token
                verify_jwt_in_request()

                # Extract user identity
                user_data = get_jwt_identity()
                g.user_id = user_data.get("user_id")
                g.role = user_data.get("role")

            except ExpiredSignatureError:
                return jsonify({"error": True, "message": "Token has expired"}), 401
            except NoAuthorizationError:
                return jsonify({"error": True, "message": "Missing token"}), 401
            except InvalidHeaderError:
                return jsonify({"error": True, "message": "Invalid token header"}), 401
            except RevokedTokenError:
                return jsonify({"error": True, "message": "Token has been revoked"}), 401
            except WrongTokenError:
                return jsonify({"error": True, "message": "Wrong token type"}), 401
            except FreshTokenRequired:
                return jsonify({"error": True, "message": "Fresh token required"}), 401
            except Exception as e:
                # Catch all other unexpected exceptions
                return jsonify({"error": True, "message": f"Unexpected error: {str(e)}"}), 500

            return f(*args, **kwargs)
        return decorated_function
    return decorator
