from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo.errors import ServerSelectionTimeoutError
from app.database.repository.user import UserRepository
from app.usecases.user.user import UserUseCase
from app.database.repository.token import TokenRepository
from app.database.repository.subscription import SubscriptionRepository
from app.usecases.subscription.subscription import SubscriptionUseCase
from app.usecases.token.token import TokenUseCase


from app.v1.auth.auth_route import auth_bp
from app.database.connection import mongo
from app.database.base import Database  # Import Database class

import logging
import cloudinary
import os


# Initialize extensions
jwt = JWTManager()
cors = CORS()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# Logger setup
logger = logging.getLogger(__name__)
app = Flask(__name__)

def init_app():
    # global database
    app.config.from_prefixed_env()
    # Initialize Flask extensions
    mongo.init_app(app)
    jwt.init_app(app)

    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Configure logger
    logging.basicConfig(level=logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    # Check MongoDB connection and initialize Database instance
    try:
        # Perform a test connection to MongoDB to check if it’s available
        mongo.cx.server_info()  # This will raise an immediate error if MongoDB is not available

        app.extensions['database'] = Database(mongo.db)
        app.logger.info("MongoDB connection established.")
    except ServerSelectionTimeoutError as e:
        # Log the detailed connection error
        app.logger.error(f"Failed to connect to MongoDB: {e.details}")
        raise RuntimeError("Cannot start app: Database connection failed.")

    # initialize repositories and usecases
    db_instance = app.extensions['database']  # Ensure 'database' is added to extensions

    # subscription repo and usecase
    subscription_repo = SubscriptionRepository(db_instance)
    subscription_use_case = SubscriptionUseCase(subscription_repo)
    
    # user repo and usecase
    user_repo = UserRepository(db_instance)
    user_use_case = UserUseCase(user_repo, subscription_repo)

    # token repo and usecase
    token_repo = TokenRepository(db_instance)
    token_use_case = TokenUseCase(token_repo)


    auth_bp.user_use_case = user_use_case
    auth_bp.token_use_case = token_use_case
    auth_bp.subscription_use_case = subscription_use_case

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    # jwt error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"error": True, "message": "Token has expired"}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"error": True, "message": "Invalid token"}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"error": True, "message": "Missing token"}, 401

    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]

        return token_use_case.is_jti_blacklisted(jti)
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {"error": True, "message": "Token has been revoked"}, 401
    
    return app