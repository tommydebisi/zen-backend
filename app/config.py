from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    ZEN_HOST = os.getenv('ZEN_HOST', '127.0.0.1')
    ZEN_PORT = os.getenv('ZEN_PORT', '5000')
    DEBUG = True if os.getenv('FLASK_ENV') == 'development' else False

config = Config()