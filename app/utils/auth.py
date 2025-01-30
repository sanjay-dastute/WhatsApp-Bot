# Author: SANJAY KR
from functools import wraps
from flask import request, jsonify
from ..controllers.auth_controller import verify_token

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "Missing token"}), 401
        
        username = verify_token(token.split(' ')[1])
        if not username:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated_function
