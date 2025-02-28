# Author: SANJAY KR
import os
from sqlalchemy.orm import Session
from flask import current_app
from ..models.family import Samaj, Member
from ..services.whatsapp_service import get_whatsapp_service
from twilio.base.exceptions import TwilioRestException

def get_service():
    try:
        return get_whatsapp_service()
    except RuntimeError:
        current_app.logger.error("WhatsApp service not initialized")
        return None

def handle_webhook(phone_number: str, message: str, db: Session):
    try:
        whatsapp_service = get_service()
        if whatsapp_service is None:
            return "Service temporarily unavailable. Please try again later.", False
            
        if not whatsapp_service.client:
            current_app.logger.error("Twilio client not properly initialized")
            return "Service temporarily unavailable. Please try again later.", False
            
        if not phone_number or not message:
            current_app.logger.error(f"Missing required parameters: phone={phone_number}, message={message}")
            return "Invalid request format. Please try again.", False
            
        # Clean up phone number and validate format
        phone_number = phone_number.replace("whatsapp:", "").strip()
        if not phone_number.startswith("+"):
            phone_number = "+" + phone_number
            
        if not phone_number[1:].isdigit() or len(phone_number) < 10:
            current_app.logger.error(f"Invalid phone number format: {phone_number}")
            return "Invalid phone number format. Please try again.", False
            
        # Check if this is the system number
        system_number = os.getenv("TWILIO_PHONE_NUMBER", "whatsapp:+14155238886").replace("whatsapp:", "")
        if phone_number == system_number:
            current_app.logger.error(f"Received message from system number: {phone_number}")
            return "Cannot process messages from the system number.", False
            
        current_app.logger.info(f"Processing webhook for {phone_number}: {message}")
        
        # Process the message
        response, success = whatsapp_service.handle_message(phone_number, message)
        if not success:
            current_app.logger.error(f"Failed to process message from {phone_number}")
            return "Failed to process your message. Please try again later.", False
            
        return response, True
            
        current_app.logger.info(f"Received webhook for {phone_number}: {message}")
        phone_number = phone_number.replace("whatsapp:", "")
        whatsapp_service = get_service()
        response, success = whatsapp_service.handle_message(phone_number, message)
        
        if not success:
            current_app.logger.error(f"Failed to process message for {phone_number}")
            return response, False
        
        session = whatsapp_service.current_sessions.get(phone_number)
        if not session:
            try:
                if not whatsapp_service.send_message(phone_number, response):
                    current_app.logger.error(f"Failed to send WhatsApp message to {phone_number}")
                    return "Failed to send response message", False
                return response, True
            except Exception as e:
                current_app.logger.error(f"Error sending message to {phone_number}: {str(e)}")
                return "Failed to send response message", False
            
        if session["step"] >= 26:
            try:
                data = session["data"]
                samaj = db.query(Samaj).filter(Samaj.name == data["samaj"]).first()
                if not samaj:
                    samaj = Samaj(name=data["samaj"])
                    db.add(samaj)
                    db.flush()

                member = Member(
                    samaj_id=samaj.id,
                    name=data["name"],
                    gender=data["gender"],
                    age=int(data["age"]),
                    blood_group=data["blood_group"],
                    mobile_1=data["mobile_1"],
                    mobile_2=data["mobile_2"],
                    education=data["education"],
                    occupation=data["occupation"],
                    marital_status=data["marital_status"],
                    address=data["address"],
                    email=data["email"],
                    birth_date=data["birth_date"],
                    anniversary_date=data.get("anniversary_date"),
                    native_place=data["native_place"],
                    current_city=data["current_city"],
                    languages_known=data["languages_known"],
                    skills=data["skills"],
                    hobbies=data["hobbies"],
                    emergency_contact=data["emergency_contact"],
                    relationship_status=data["relationship_status"],
                    family_role=data["family_role"],
                    medical_conditions=data.get("medical_conditions"),
                    dietary_preferences=data["dietary_preferences"],
                    social_media_handles=data.get("social_media_handles"),
                    profession_category=data["profession_category"],
                    volunteer_interests=data.get("volunteer_interests")
                )
                db.add(member)
                db.commit()
                del whatsapp_service.current_sessions[phone_number]
                current_app.logger.info(f"Successfully saved data for {phone_number}")
            except Exception as e:
                current_app.logger.error(f"Database error for {phone_number}: {str(e)}")
                db.rollback()
                return "An error occurred while saving your information. Please try again.", False
        
        try:
            if not whatsapp_service.send_message(phone_number, response):
                current_app.logger.error(f"Failed to send WhatsApp message to {phone_number}")
                return "Failed to send response message", False
            return response, True
        except Exception as e:
            current_app.logger.error(f"Error sending message to {phone_number}: {str(e)}")
            return "Failed to send response message", False
    except Exception as e:
        current_app.logger.error(f"Unexpected error processing webhook: {str(e)}")
        return "An unexpected error occurred", False
    
    try:
        if not whatsapp_service.send_message(phone_number, response):
            current_app.logger.error(f"Failed to send WhatsApp message to {phone_number}")
            return "Failed to send response message", False
        current_app.logger.info(f"Successfully sent message to {phone_number}")
        return response, True
    except TwilioRestException as e:
        current_app.logger.error(f"Twilio error for {phone_number}: {str(e)}")
        return "Failed to send response message", False
    except Exception as e:
        current_app.logger.error(f"Unexpected error for {phone_number}: {str(e)}")
        return "An unexpected error occurred", False
