# Author: SANJAY KR
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..controllers.whatsapp_controller import handle_webhook

whatsapp_bp = Blueprint("whatsapp", __name__)

@whatsapp_bp.route("/webhook", methods=["POST"])
def webhook():
    db = get_db()
    try:
        request_data = request.form
        if 'NumMedia' in request_data and int(request_data['NumMedia']) > 0:
            return jsonify({
                "success": False,
                "message": "Media attachments are not supported. Please send text messages only."
            }), 400
            
        # Extract phone number from Twilio format
        phone_number = request_data["From"].split(":")[-1].strip()
        response, success = handle_webhook(
            phone_number=phone_number,
            message=request_data["Body"],
            db=db
        )
        return jsonify({"success": success, "message": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
