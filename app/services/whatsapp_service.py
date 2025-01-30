# Author: SANJAY KR
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flask import current_app, has_app_context, Flask
import os
from dotenv import load_dotenv
from typing import Dict, Any, Tuple, Optional

load_dotenv()

_instance = None

def get_whatsapp_service():
    if not has_app_context():
        raise RuntimeError("No Flask application context")
    
    app = current_app._get_current_object()
    if not hasattr(app, 'extensions'):
        app.extensions = {}
    if 'whatsapp_service' not in app.extensions:
        service = WhatsAppService()
        service.init_app(app)
    return app.extensions['whatsapp_service']

class WhatsAppService:
    def __init__(self):
        self.current_sessions: Dict[str, Dict[str, Any]] = {}
        self.client = None
        
    @classmethod
    def get_instance(cls):
        global _instance
        if _instance is None:
            _instance = cls()
        return _instance
        
    def init_app(self, app):
        try:
            # Check if service is already initialized
            if hasattr(app, 'extensions') and 'whatsapp_service' in app.extensions:
                return app.extensions['whatsapp_service']
                
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            
            if not account_sid or not auth_token:
                app.logger.error("Twilio credentials not properly configured")
                raise ValueError("Twilio credentials not properly configured")
                
            self.client = Client(account_sid, auth_token)
            
            # Store instance in app context
            if not hasattr(app, 'extensions'):
                app.extensions = {}
            app.extensions['whatsapp_service'] = self
            
            app.logger.info("WhatsApp service initialized successfully")
            return self
        except Exception as e:
            app.logger.error(f"Failed to initialize WhatsApp service: {str(e)}")
            raise

    def send_message(self, to: str, message: str) -> bool:
        try:
            if not self.client:
                current_app.logger.error("Twilio client not initialized")
                return False
                
            system_number = os.getenv("TWILIO_PHONE_NUMBER", "whatsapp:+14155238886")
            
            # Clean up the destination number
            to_number = to.strip().replace(" ", "").replace("whatsapp:", "")
            if not to_number.startswith("+"):
                to_number = "+" + to_number
                
            # Validate number format (must be E.164 format)
            if not to_number.startswith("+") or not to_number[1:].isdigit():
                current_app.logger.error(f"Invalid phone number format: {to_number}")
                return False
                
            if to_number == system_number.replace("whatsapp:", ""):
                current_app.logger.error(f"Cannot send message to system number: {to_number}")
                return False
                
            self.client.messages.create(
                from_=system_number,
                body=message,
                to=f"whatsapp:{to_number}"
            )
            current_app.logger.info(f"Successfully sent message to {to_number}")
            return True
        except TwilioRestException as e:
            if "same To and From" in str(e):
                current_app.logger.error(f"Cannot send message to system number: {to_number}")
                return False
            current_app.logger.error(f"Twilio API error: {str(e)}")
            return False
        except Exception as e:
            current_app.logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return False

    def validate_input(self, field: str, value: str) -> tuple[bool, str]:
        current_app.logger.debug(f"Validating field '{field}' with value '{value}'")
        validations = {
            "gender": lambda x: x.lower() in ["male", "female", "other"],
            "age": lambda x: x.isdigit() and 0 <= int(x) <= 120,
            "blood_group": lambda x: x.upper() in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
            "mobile_1": lambda x: x.isdigit() and len(x) == 10,
            "mobile_2": lambda x: x.isdigit() and len(x) == 10 if x.lower() != "skip" else True,
            "email": lambda x: "@" in x and "." in x.split("@")[1],
            "birth_date": lambda x: len(x.split("/")) == 3,
            "anniversary_date": lambda x: len(x.split("/")) == 3 if x.lower() != "skip" else True,
            "emergency_contact": lambda x: x.isdigit() and len(x) == 10,
            "family_role": lambda x: x.title() in ["Head", "Spouse", "Child", "Parent", "Sibling", "Other"],
            "family_head": lambda x: bool(x.strip()),
            "marital_status": lambda x: x.title() in ["Single", "Married", "Divorced", "Widowed"],
            "relationship_status": lambda x: x.title() in ["Single", "Married", "Divorced", "Widowed", "Other"],
            "medical_conditions": lambda x: bool(x.strip()) if x.lower() != "skip" else True,
            "dietary_preferences": lambda x: bool(x.strip()),
            "social_media_handles": lambda x: bool(x.strip()) if x.lower() != "skip" else True,
            "volunteer_interests": lambda x: bool(x.strip()) if x.lower() != "skip" else True,
            "samaj": lambda x: bool(x.strip()) and len(x.strip()) >= 2,
            "name": lambda x: bool(x.strip()) and len(x.strip()) >= 2,
            "education": lambda x: bool(x.strip()),
            "occupation": lambda x: bool(x.strip()),
            "address": lambda x: bool(x.strip()),
            "native_place": lambda x: bool(x.strip()),
            "current_city": lambda x: bool(x.strip()),
            "languages_known": lambda x: bool(x.strip()),
            "skills": lambda x: bool(x.strip()),
            "hobbies": lambda x: bool(x.strip()),
            "profession_category": lambda x: bool(x.strip())
        }
        
        if field not in validations:
            return True, value
            
        is_valid = validations[field](value)
        error_messages = {
            "gender": "Please enter Male, Female, or Other",
            "age": "Please enter a valid age between 0 and 120",
            "blood_group": "Please enter a valid blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)",
            "mobile_1": "Please enter a valid 10-digit mobile number",
            "mobile_2": "Please enter a valid 10-digit mobile number or type 'skip'",
            "email": "Please enter a valid email address",
            "birth_date": "Please enter date in DD/MM/YYYY format",
            "anniversary_date": "Please enter date in DD/MM/YYYY format or type 'skip'",
            "emergency_contact": "Please enter a valid 10-digit contact number",
            "family_role": "Please enter a valid role (Head, Spouse, Child, Parent, Sibling, Other)",
            "family_head": "Please enter the family head's name",
            "marital_status": "Please enter a valid status (Single, Married, Divorced, Widowed)",
            "family_context": "Please provide valid family information"
        }
        
        return is_valid, error_messages[field] if not is_valid else value

    def handle_message(self, from_number: str, message: str) -> Tuple[str, bool]:
        try:
            # Extract and format phone number
            phone_number = from_number.split(":")[-1].strip()
            if not phone_number.startswith("+"):
                phone_number = "+" + phone_number
                
            current_app.logger.info(f"Processing message from {phone_number}: {message}")
            
            if not self.client:
                current_app.logger.error("Twilio client not initialized")
                return "Service temporarily unavailable. Please try again later.", False
                
            # Check if this is the system number
            system_number = os.getenv("TWILIO_PHONE_NUMBER", "whatsapp:+14155238886").replace("whatsapp:", "")
            if phone_number == system_number:
                current_app.logger.error(f"Cannot process messages from system number: {phone_number}")
                return "Cannot process messages from the system number.", False
                
            if message.lower() == "start":
                self.current_sessions[phone_number] = {
                    "step": 0,
                    "data": {},
                    "family_context": {
                        "is_new_family": False,
                        "family_id": None,
                        "family_name": None,
                        "samaj_id": None,
                        "correction_mode": False,
                        "field_to_correct": None,
                        "pending_validation": [],
                        "role_confirmed": False
                    }
                }
                current_app.logger.info(f"Started new session for {phone_number}")
                return "Welcome to Family & Samaj Data Collection Bot!\nPlease enter your Samaj name:", True
                
            if from_number not in self.current_sessions:
                current_app.logger.warning(f"No active session for {from_number}")
                return "Please send 'Start' to begin the data collection process.", True
        except Exception as e:
            current_app.logger.error(f"Error processing message: {str(e)}")
            return "An error occurred. Please try again.", False

        try:
            session = self.current_sessions[from_number]
            step = session["step"]
            data = session["data"]
        except Exception as e:
            current_app.logger.error(f"Error accessing session data for {from_number}: {str(e)}")
            return "An error occurred. Please try again by sending 'Start'.", False

        steps = {
            0: ("samaj", "Please enter your full name:"),
            1: ("name", "Please enter your family role (Head/Spouse/Child/Parent/Sibling/Other):"),
            2: ("family_role", "Please enter the family head's name (if you are Head, enter your own name):"),
            3: ("family_head", "Please enter your gender (Male/Female/Other):"),
            4: ("gender", "Please enter your age:"),
            5: ("age", "Please enter your blood group:"),
            6: ("blood_group", "Please enter your primary mobile number:"),
            7: ("mobile_1", "Please enter your secondary mobile number (or type 'skip'):"),
            8: ("mobile_2", "Please enter your education:"),
            9: ("education", "Please enter your occupation:"),
            10: ("occupation", "Please enter your marital status (Single/Married/Divorced/Widowed):"),
            11: ("marital_status", "Please enter your address:"),
            12: ("address", "Please enter your email:"),
            13: ("email", "Please enter your birth date (DD/MM/YYYY):"),
            14: ("birth_date", "Please enter your anniversary date (DD/MM/YYYY or type 'skip'):"),
            15: ("anniversary_date", "Please enter your native place:"),
            16: ("native_place", "Please enter your current city:"),
            17: ("current_city", "Please enter languages known (comma-separated):"),
            18: ("languages_known", "Please enter your skills (comma-separated):"),
            19: ("skills", "Please enter your hobbies (comma-separated):"),
            20: ("hobbies", "Please enter emergency contact number:"),
            21: ("emergency_contact", "Please enter your relationship status:"),
            22: ("relationship_status", "Please enter your medical conditions (or type 'skip'):"),
            23: ("medical_conditions", "Please enter your dietary preferences:"),
            24: ("dietary_preferences", "Please enter your social media handles (or type 'skip'):"),
            25: ("social_media_handles", "Please enter your profession category:"),
            26: ("profession_category", "Please enter your volunteer interests (or type 'skip'):"),
            27: ("volunteer_interests", "Please review your information:\n{}\nIs this correct? (Yes/No):")
        }

        if step in steps:
            field, next_prompt = steps[step]
            is_valid, result = self.validate_input(field, message)
            if not is_valid:
                current_app.logger.warning(f"Invalid input for field '{field}' from {from_number}: {message}")
                return result, True
            
            if message.lower() == "skip" and field in ["mobile_2", "anniversary_date", "medical_conditions", "social_media_handles", "volunteer_interests"]:
                data[field] = None
                current_app.logger.info(f"User {from_number} skipped optional field '{field}'")
            else:
                if field == "family_role":
                    family_role = result.title()
                    if family_role == "Head":
                        session["family_context"]["is_new_family"] = True
                        data["family_head"] = data.get("name", "")
                    elif family_role not in ["Spouse", "Child", "Parent", "Sibling", "Other"]:
                        return "Please enter a valid role (Head/Spouse/Child/Parent/Sibling/Other)", True
                    data[field] = family_role
                    if family_role != "Head":
                        next_prompt = "Please enter the name of your family head:"
                elif field == "family_head" and data.get("family_role") != "Head":
                    session["family_context"]["role_confirmed"] = True
                    data[field] = result
                else:
                    data[field] = result
                current_app.logger.info(f"User {from_number} provided valid input for '{field}': {result}")
            
            session["step"] = step + 1
            current_app.logger.info(f"Advanced session for {from_number} to step {step + 1}")
            return next_prompt, True

        if step == 27:  # After collecting all data
            family_role = data.get("family_role", "").title()
            confirmation_message = "Please review your information:\n\n"
            confirmation_message += f"Samaj: {data.get('samaj', '')}\n"
            confirmation_message += f"Name: {data.get('name', '')}\n"
            confirmation_message += f"Role: {family_role}\n"
            
            if family_role != "Head":
                confirmation_message += f"Family Head: {data.get('family_head', '')}\n"
            
            for field, value in data.items():
                if value is not None and field not in ['samaj', 'name', 'family_role', 'family_head']:
                    confirmation_message += f"{field.replace('_', ' ').title()}: {value}\n"
            
            confirmation_message += "\nIs this information correct? (Yes/No)"
            session["step"] = 999  # Confirmation step
            return confirmation_message, True
            
        if step == 999:  # Confirmation step
            if message.lower() == "yes":
                try:
                    current_app.logger.info(f"User {from_number} confirmed data")
                    family_context = session.get("family_context", {})
                    family_role = data.get("family_role", "").title()
                    
                    # Validate family relationships before saving
                    if family_role == "Head":
                        if not data.get("name"):
                            return "Error: Name is required for family head.", False
                        response = f"Thank you! Your information has been saved. You are registered as the head of {data['name']}'s family in {data['samaj']} Samaj."
                    else:
                        if not data.get("family_head"):
                            return "Error: Family head name is required for non-head members.", False
                        
                        # Validate family role relationships
                        if family_role == "Spouse":
                            response = f"Thank you! Your information has been saved. You are registered as the spouse in {data['family_head']}'s family."
                        elif family_role == "Parent":
                            response = f"Thank you! Your information has been saved. You are registered as a parent in {data['family_head']}'s family."
                        elif family_role == "Child":
                            response = f"Thank you! Your information has been saved. You are registered as a child in {data['family_head']}'s family."
                        elif family_role == "Sibling":
                            response = f"Thank you! Your information has been saved. You are registered as a sibling in {data['family_head']}'s family."
                        else:
                            response = f"Thank you! Your information has been saved. You are registered as a {family_role.lower()} in {data['family_head']}'s family."
                    
                    del self.current_sessions[from_number]
                    return response, True
                except Exception as e:
                    current_app.logger.error(f"Failed to save user data: {str(e)}")
                    return "An error occurred while saving your information. Please try again later.", False
            elif message.lower() == "no":
                session["step"] = 1000  # Correction step
                field_list = "\n".join([
                    f"{i+1}. {field.replace('_', ' ').title()}: {value}" 
                    for i, (field, value) in enumerate(data.items())
                    if field != "family_head" or data.get("family_role", "").title() != "Head"
                ])
                return f"Which field would you like to correct? Enter the number:\n{field_list}", True
            else:
                return "Please reply with 'Yes' to confirm or 'No' to make corrections.", True
                
        if step == 1000:  # Field selection for correction
            try:
                field_index = int(message) - 1
                fields = list(data.keys())
                if 0 <= field_index < len(fields):
                    field_to_correct = fields[field_index]
                    session["correction_field"] = field_to_correct
                    session["step"] = 1001
                    return f"Current value of {field_to_correct.replace('_', ' ').title()}: {data[field_to_correct]}\nPlease enter the new value:", True
                else:
                    return "Please enter a valid number from the list.", True
            except ValueError:
                return "Please enter a valid number.", True
                
        if step == 1001:  # Correcting the field
            field = session["correction_field"]
            is_valid, result = self.validate_input(field, message)
            if not is_valid:
                return result, True
            
            data[field] = result
            session["step"] = 999  # Back to confirmation
            confirmation_message = "Updated information:\n\n"
            for field, value in data.items():
                confirmation_message += f"{field.replace('_', ' ').title()}: {value}\n"
            confirmation_message += "\nIs this information correct? (Yes/No)"
            return confirmation_message, True
