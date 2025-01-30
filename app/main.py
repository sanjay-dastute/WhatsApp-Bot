# Author: SANJAY KR
from flask import Flask
from flask_cors import CORS
from .routes.whatsapp import whatsapp_bp
from .routes.admin import admin_bp
from .routes.auth import auth_bp
from .models.base import init_db

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Initialize database
    init_db()
    
    # Register blueprints
    app.register_blueprint(whatsapp_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
