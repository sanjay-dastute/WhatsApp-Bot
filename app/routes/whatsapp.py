# Author: SANJAY KR
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..controllers.whatsapp_controller import handle_webhook

whatsapp_bp = Blueprint("whatsapp", __name__)

@whatsapp_bp.route("/webhook", methods=["POST"])
def webhook():
    db = next(get_db())
    try:
        response, success = handle_webhook(
            phone_number=request.form["From"],
            message=request.form["Body"],
            db=db
        )
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
