# Author: SANJAY KR
from flask import Blueprint, request, jsonify
from ..controllers.auth_controller import authenticate_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/token", methods=["POST"])
def login():
    data = request.form
    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Missing username or password"}), 400
    
    token_data = authenticate_user(data["username"], data["password"])
    if not token_data:
        return jsonify({"error": "Invalid credentials"}), 401
    
    return jsonify(token_data)
