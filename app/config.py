from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    ZEN_HOST = os.getenv('ZEN_HOST', '127.0.0.1')
    ZEN_PORT = os.getenv('ZEN_PORT', '5000')
    DEBUG = True if os.getenv('FLASK_ENV') == 'development' else False
    PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
    CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    MAIL_DEFAULT_SENDER = os.getenv('FLASK_MAIL_DEFAULT_SENDER')


config = Config()