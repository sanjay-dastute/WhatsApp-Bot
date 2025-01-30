# Author: SANJAY KR
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    DEBUG = True
    TESTING = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"])
    
    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
    TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
    TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]
    
    # Admin Configuration
    ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
    ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
    
    @classmethod
    def init_app(cls, app):
        app.config.from_object(cls)
