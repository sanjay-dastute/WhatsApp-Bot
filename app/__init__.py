# Author: SANJAY KR
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/whatsapp_bot')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure logging
    import logging
    import sys
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)
    
    app.logger.info("Starting Flask application")
    
    # Log environment variables
    app.logger.info("Environment variables:")
    for key, value in os.environ.items():
        if not any(sensitive in key.lower() for sensitive in ['password', 'secret', 'token']):
            app.logger.info(f"{key}: {value}")
            
    # Set Flask secret key
    app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'development-secret-key-do-not-use-in-production')
    app.logger.info("Flask configuration loaded")
    
    # Load configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'development-secret-key-do-not-use-in-production')
    app.config['JWT_ALGORITHM'] = os.environ.get('JWT_ALGORITHM', 'HS256')
    app.config['JWT_ACCESS_TOKEN_EXPIRE_MINUTES'] = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
    app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin')
    
    from config.settings import Config
    Config.init_app(app)
    
    # Verify configuration loaded correctly
    app.logger.info("Verifying configuration...")
    app.logger.info(f"ADMIN_USERNAME: {app.config.get('ADMIN_USERNAME')}")
    app.logger.info(f"JWT_SECRET_KEY: {bool(app.config.get('JWT_SECRET_KEY'))}")
    app.logger.info(f"JWT_ALGORITHM: {app.config.get('JWT_ALGORITHM')}")
    
    # Ensure critical config values are set
    assert app.config.get('ADMIN_USERNAME'), "ADMIN_USERNAME must be configured"
    assert app.config.get('ADMIN_PASSWORD'), "ADMIN_PASSWORD must be configured"
    assert app.config.get('JWT_SECRET_KEY'), "JWT_SECRET_KEY must be configured"
    
    # Log configuration values for debugging (without sensitive data)
    app.logger.info("Configuration loaded:")
    app.logger.info(f"JWT_ALGORITHM: {app.config['JWT_ALGORITHM']}")
    app.logger.info(f"JWT_ACCESS_TOKEN_EXPIRE_MINUTES: {app.config['JWT_ACCESS_TOKEN_EXPIRE_MINUTES']}")
    app.logger.info(f"JWT_SECRET_KEY is set: {bool(app.config.get('JWT_SECRET_KEY'))}")
    
    # Log configuration for debugging
    app.logger.info(f"JWT_SECRET_KEY configured: {bool(app.config.get('JWT_SECRET_KEY'))}")
    app.logger.info(f"JWT_ALGORITHM configured: {app.config.get('JWT_ALGORITHM')}")
    
    # Ensure critical config values are set
    assert "JWT_SECRET_KEY" in app.config, "JWT_SECRET_KEY must be configured"
    assert "JWT_ACCESS_TOKEN_EXPIRE_MINUTES" in app.config, "JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be configured"
    
    app.logger.info("Flask configuration loaded successfully")
    
    db.init_app(app)
    
    with app.app_context():
        try:
            app.logger.info("Initializing database connection...")
            app.logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            app.logger.info("Checking database tables...")
            from .models.family import Samaj, Member
            
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            app.logger.info(f"Existing tables: {existing_tables}")
            
            if not existing_tables:
                app.logger.info("Creating database tables...")
                db.create_all()
                app.logger.info("Database tables created successfully")
                
                # Check if there's any data
                samaj_count = db.session.query(Samaj).count()
                if samaj_count == 0:
                    app.logger.info("Generating sample data...")
                    try:
                        from app.utils.generate_sample_data import generate_sample_data
                        data = generate_sample_data(50)
                        app.logger.info("Sample data generated successfully")
                    except Exception as e:
                        app.logger.error(f"Error importing generate_sample_data: {str(e)}")
                        raise
                    
                    for entry in data:
                        try:
                            samaj = Samaj(name=entry["samaj"])
                            db.session.add(samaj)
                            db.session.commit()
                            
                            member = Member(
                                samaj_id=samaj.id,
                                name=entry["name"],
                                gender=entry["gender"],
                                age=entry["age"],
                                blood_group=entry["blood_group"],
                                mobile_1=entry["mobile_1"],
                                mobile_2=entry["mobile_2"],
                                education=entry["education"],
                                occupation=entry["occupation"],
                                marital_status=entry["marital_status"],
                                address=entry["address"],
                                email=entry["email"],
                                birth_date=entry["birth_date"],
                                anniversary_date=entry["anniversary_date"],
                                native_place=entry["native_place"],
                                current_city=entry["current_city"],
                                languages_known=entry["languages_known"],
                                skills=entry["skills"],
                                hobbies=entry["hobbies"],
                                emergency_contact=entry["emergency_contact"],
                                relationship_status=entry["relationship_status"],
                                family_role=entry["family_role"],
                                medical_conditions=entry["medical_conditions"],
                                dietary_preferences=entry["dietary_preferences"],
                                social_media_handles=entry["social_media_handles"],
                                profession_category=entry["profession_category"],
                                volunteer_interests=entry["volunteer_interests"]
                            )
                            db.session.add(member)
                            db.session.commit()
                            app.logger.info(f"Added member {member.name} to samaj {samaj.name}")
                        except Exception as e:
                            app.logger.error(f"Error during sample data generation: {str(e)}")
                            db.session.rollback()
                            continue
                    app.logger.info("Sample data generation completed")
                else:
                    app.logger.info(f"Using existing data: {samaj_count} samaj records found")
            else:
                app.logger.info(f"Using existing tables: {existing_tables}")
            
            if db.session.query(Samaj).first() is None:
                app.logger.info("Generating sample data...")
                try:
                    from app.utils.generate_sample_data import generate_sample_data
                    data = generate_sample_data(50)
                    app.logger.info("Sample data generated successfully")
                except Exception as e:
                    app.logger.error(f"Error importing generate_sample_data: {str(e)}")
                    raise
                
                for entry in data:
                    try:
                        samaj = Samaj(name=entry["samaj"])
                        db.session.add(samaj)
                        db.session.flush()
                        
                        member = Member(
                            samaj_id=samaj.id,
                            name=entry["name"],
                            gender=entry["gender"],
                            age=entry["age"],
                            blood_group=entry["blood_group"],
                            mobile_1=entry["mobile_1"],
                            mobile_2=entry["mobile_2"],
                            education=entry["education"],
                            occupation=entry["occupation"],
                            marital_status=entry["marital_status"],
                            address=entry["address"],
                            email=entry["email"],
                            birth_date=entry["birth_date"],
                            anniversary_date=entry["anniversary_date"],
                            native_place=entry["native_place"],
                            current_city=entry["current_city"],
                            languages_known=entry["languages_known"],
                            skills=entry["skills"],
                            hobbies=entry["hobbies"],
                            emergency_contact=entry["emergency_contact"],
                            relationship_status=entry["relationship_status"],
                            family_role=entry["family_role"],
                            medical_conditions=entry["medical_conditions"],
                            dietary_preferences=entry["dietary_preferences"],
                            social_media_handles=entry["social_media_handles"],
                            profession_category=entry["profession_category"],
                            volunteer_interests=entry["volunteer_interests"]
                        )
                        db.session.add(member)
                        db.session.commit()
                        app.logger.info(f"Added member {member.name} to samaj {samaj.name}")
                    except Exception as e:
                        app.logger.error(f"Error during sample data generation: {str(e)}")
                        db.session.rollback()
                        continue
                app.logger.info("Sample data generation completed")
        except Exception as e:
            app.logger.error(f"Error during database initialization: {str(e)}")
            raise
    
    # Initialize WhatsApp service before routes
    from .services.whatsapp_service import WhatsAppService, get_whatsapp_service
    
    # Initialize service in app context
    with app.app_context():
        get_whatsapp_service()
    
    from .routes.whatsapp import whatsapp_bp
    from .routes.admin import admin_bp
    from .routes.auth import auth_bp
    
    app.register_blueprint(whatsapp_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    
    # Register CLI commands
    from .cli import check_db
    app.cli.add_command(check_db)
    
    return app
