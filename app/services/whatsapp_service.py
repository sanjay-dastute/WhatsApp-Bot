# Author: SANJAY KR
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flask import current_app
import os
from dotenv import load_dotenv
from typing import Dict, Any, Tuple, Optional

load_dotenv()

class WhatsAppService:
    def __init__(self):
        try:
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            
            if not account_sid or not auth_token:
                raise ValueError("Twilio credentials not properly configured")
                
            self.client = Client(account_sid, auth_token)
            self.current_sessions: Dict[str, Dict[str, Any]] = {}
            current_app.logger.info("WhatsApp service initialized successfully")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize WhatsApp service: {str(e)}")
            raise

    def send_message(self, to: str, message: str) -> bool:
        try:
            self.client.messages.create(
                from_="whatsapp:+14155238886",
                body=message,
                to=f"whatsapp:{to}"
            )
            return True
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
            "emergency_contact": lambda x: x.isdigit() and len(x) == 10
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
            "emergency_contact": "Please enter a valid 10-digit contact number"
        }
        
        return is_valid, error_messages[field] if not is_valid else value

    def handle_message(self, from_number: str, message: str) -> Tuple[str, bool]:
        current_app.logger.info(f"Processing message from {from_number}: {message}")
        if message.lower() == "start":
            self.current_sessions[from_number] = {
                "step": 0,
                "data": {}
            }
            current_app.logger.info(f"Started new session for {from_number}")
            return "Welcome to Family & Samaj Data Collection Bot!\nPlease enter your Samaj name:", True

        if from_number not in self.current_sessions:
            current_app.logger.warning(f"No active session for {from_number}")
            return "Please send 'Start' to begin the data collection process.", True

        session = self.current_sessions[from_number]
        step = session["step"]
        data = session["data"]

        steps = {
            0: ("samaj", "Please enter your full name:"),
            1: ("name", "Please enter your gender (Male/Female/Other):"),
            2: ("gender", "Please enter your age:"),
            3: ("age", "Please enter your blood group:"),
            4: ("blood_group", "Please enter your primary mobile number:"),
            5: ("mobile_1", "Please enter your secondary mobile number (or type 'skip'):"),
            6: ("mobile_2", "Please enter your education:"),
            7: ("education", "Please enter your occupation:"),
            8: ("occupation", "Please enter your marital status:"),
            9: ("marital_status", "Please enter your address:"),
            10: ("address", "Please enter your email:"),
            11: ("email", "Please enter your birth date (DD/MM/YYYY):"),
            12: ("birth_date", "Please enter your anniversary date (DD/MM/YYYY or type 'skip'):"),
            13: ("anniversary_date", "Please enter your native place:"),
            14: ("native_place", "Please enter your current city:"),
            15: ("current_city", "Please enter languages known (comma-separated):"),
            16: ("languages_known", "Please enter your skills (comma-separated):"),
            17: ("skills", "Please enter your hobbies (comma-separated):"),
            18: ("hobbies", "Please enter emergency contact number:"),
            19: ("emergency_contact", "Please enter your relationship status:"),
            20: ("relationship_status", "Please enter your family role:"),
            21: ("family_role", "Please enter any medical conditions (or type 'skip'):"),
            22: ("medical_conditions", "Please enter dietary preferences:"),
            23: ("dietary_preferences", "Please enter social media handles (comma-separated or type 'skip'):"),
            24: ("social_media_handles", "Please enter your profession category:"),
            25: ("profession_category", "Please enter volunteer interests (comma-separated or type 'skip'):")
        }

        if step in steps:
            field, next_prompt = steps[step]
            is_valid, result = self.validate_input(field, message)
            if not is_valid:
                current_app.logger.warning(f"Invalid input for field '{field}' from {from_number}: {message}")
                return result, True
            
            if message.lower() == "skip" and field == "mobile_2":
                data[field] = None
                current_app.logger.info(f"User {from_number} skipped optional field '{field}'")
            else:
                data[field] = result
                current_app.logger.info(f"User {from_number} provided valid input for '{field}': {result}")
            session["step"] = step + 1
            current_app.logger.info(f"Advanced session for {from_number} to step {step + 1}")
            return next_prompt, True

        try:
            # Here we would typically save the data to the database
            current_app.logger.info(f"Completed data collection for user {from_number}")
            del self.current_sessions[from_number]
            return "Thank you for providing your information! Your data has been saved.", True
        except Exception as e:
            current_app.logger.error(f"Failed to save user data: {str(e)}")
            return "An error occurred while saving your information. Please try again later.", False
