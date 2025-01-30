# Author: SANJAY KR
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/whatsapp_bot')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'os.getenv("JWT_SECRET_KEY")')
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'os.getenv("TWILIO_ACCOUNT_SID")')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', 'os.getenv("TWILIO_PHONE_NUMBER")')
