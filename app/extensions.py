from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mailman import Mail
import certifi
import ssl

from pymongo.errors import ServerSelectionTimeoutError

# Import database connection
from app.database.connection import mongo
from app.database.base import Database

# Import repositories
from app.database import (
    UserRepository,
    SubscriptionRepository,
    TokenRepository,
    ContactUsRepository,
    TeamRepository,
    PlanRepository,
    RecordRepository,
    ArcherRankRepository,
    PaymentHistoryRepository,
    ChampionUserRepository,
    WalkInRepository
)

# Import usecases
from app.usecases import (
    SubscriptionUseCase,
    UserUseCase,
    TokenUseCase,
    ContactUsUseCase,
    PlanUseCase,
    TeamUseCase,
    RecordUseCase,
    ArcherRankUseCase,
    PaymentHistoryUseCase,
    ChampionUserUseCase,
    FileUploadUseCase
)

# Import blueprints
from app.v1 import (
    auth_bp,
    user_bp,
    contact_us_bp,
    team_bp,
    plan_bp,
    record_bp,
    archer_rank_bp,
    subscription_bp,
    payment_bp,
    payment_history_bp,
    champion_user_bp,
    file_upload_bp
)


import logging
from typing import Dict
import cloudinary
from app.config import config


# Initialize extensions
jwt = JWTManager()
cors = CORS()
mail = Mail()

cloudinary.config(
    cloud_name=config.CLOUD_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True
)

# Logger setup
logger = logging.getLogger(__name__)
app = Flask(__name__)

def init_app():
    # global database
    app.config.from_prefixed_env()
    app.config["MAIL_SSL_CONTEXT"] = ssl.create_default_context()
    # Initialize Flask extensions
    mongo.init_app(app, tlsCAFile=certifi.where())
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": [
        "http://localhost:3000",
        "*"
    ]}})

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

    # repositories
    subscription_repo = SubscriptionRepository(db_instance)
    user_repo = UserRepository(db_instance)
    token_repo = TokenRepository(db_instance)
    contact_us_repo = ContactUsRepository(mail)
    plan_repo = PlanRepository(db_instance)
    team_repo = TeamRepository(db_instance)
    record_repo = RecordRepository(db_instance)
    archer_rank_repo = ArcherRankRepository(db_instance)
    payment_history_repo = PaymentHistoryRepository(db_instance)
    champion_user_repo = ChampionUserRepository(db_instance)
    
    # usecases
    subscription_use_case = SubscriptionUseCase(subscription_repo, user_repo, plan_repo)
    user_use_case = UserUseCase(user_repo, subscription_repo, plan_repo, archer_rank_repo, payment_history_repo)
    contact_us_use_case = ContactUsUseCase(contact_us_repo)
    token_use_case = TokenUseCase(token_repo)
    plan_use_case = PlanUseCase(plan_repo)
    team_use_case = TeamUseCase(team_repo)
    record_use_case = RecordUseCase(record_repo)
    archer_rank_use_case = ArcherRankUseCase(archer_rank_repo)
    payment_history_usecase = PaymentHistoryUseCase(payment_history_repo)
    champion_user_usecase = ChampionUserUseCase(champion_user_repo, payment_history_repo)
    file_upload_usecase = FileUploadUseCase()

    # intialize blueprints with usecases
    auth_bp.user_use_case = user_use_case
    auth_bp.token_use_case = token_use_case
    auth_bp.subscription_use_case = subscription_use_case
    user_bp.user_use_case = user_use_case
    contact_us_bp.contact_us_use_case = contact_us_use_case
    team_bp.team_use_case = team_use_case
    plan_bp.plan_use_case = plan_use_case
    record_bp.record_use_case = record_use_case
    archer_rank_bp.archer_rank_use_case = archer_rank_use_case
    subscription_bp.subscription_use_case = subscription_use_case
    payment_bp.payment_history_usecase = payment_history_usecase
    payment_history_bp.payment_history_usecase = payment_history_usecase
    champion_user_bp.champion_user_use_case = champion_user_usecase
    file_upload_bp.file_upload_use_case = file_upload_usecase


    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(user_bp, url_prefix='/api/v1/user')
    app.register_blueprint(contact_us_bp, url_prefix='/api/v1/contact')
    app.register_blueprint(team_bp, url_prefix='/api/v1/team')
    app.register_blueprint(plan_bp, url_prefix='/api/v1/plan')
    app.register_blueprint(record_bp, url_prefix='/api/v1/record')
    app.register_blueprint(archer_rank_bp, url_prefix='/api/v1/rank')
    app.register_blueprint(subscription_bp, url_prefix='/api/v1/subscription')
    app.register_blueprint(payment_bp, url_prefix='/api/v1/payment')
    app.register_blueprint(payment_history_bp, url_prefix='/api/v1/history')
    app.register_blueprint(champion_user_bp, url_prefix='/api/v1/championship')
    app.register_blueprint(file_upload_bp, url_prefix='/api/v1/file')

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