from twilio.rest import Client
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class WhatsAppService:
    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.current_sessions: Dict[str, Dict[str, Any]] = {}

    def send_message(self, to: str, message: str) -> None:
        self.client.messages.create(
            from_="whatsapp:+14155238886",
            body=message,
            to=f"whatsapp:{to}"
        )

    def handle_message(self, from_number: str, message: str) -> str:
        if message.lower() == "start":
            self.current_sessions[from_number] = {
                "step": 0,
                "data": {}
            }
            return "Welcome to Family & Samaj Data Collection Bot!\nPlease enter your Samaj name:"

        if from_number not in self.current_sessions:
            return "Please send 'Start' to begin the data collection process."

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
            11: ("email", "Please enter your birth date (DD/MM/YYYY):")
        }

        if step in steps:
            field, next_prompt = steps[step]
            if message.lower() == "skip" and field == "mobile_2":
                data[field] = None
            else:
                data[field] = message
            session["step"] = step + 1
            return next_prompt

        return "Thank you for providing your information! Your data has been saved."
