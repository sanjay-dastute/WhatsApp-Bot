# Author: SANJAY KR
from flask import Blueprint, request, jsonify, send_file
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..controllers.admin_controller import (
    get_members, get_samaj_list, get_member,
    export_members_csv
)
from ..controllers.auth_controller import verify_token
from functools import wraps
from io import StringIO

admin_bp = Blueprint("admin", __name__)

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

@admin_bp.route("/members", methods=["GET"])
@login_required
def list_members():
    db = next(get_db())
    samaj_name = request.args.get("samaj_name")
    members = get_members(db, samaj_name)
    return jsonify([member.__dict__ for member in members])

@admin_bp.route("/samaj", methods=["GET"])
@login_required
def list_samaj():
    db = next(get_db())
    samaj_list = get_samaj_list(db)
    return jsonify([samaj.__dict__ for samaj in samaj_list])

@admin_bp.route("/members/<int:member_id>", methods=["GET"])
@login_required
def get_member_details(member_id: int):
    db = next(get_db())
    member = get_member(db, member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    return jsonify(member.__dict__)

@admin_bp.route("/export/csv", methods=["GET"])
@login_required
def export_csv():
    db = next(get_db())
    samaj_name = request.args.get("samaj_name")
    csv_data, filename = export_members_csv(db, samaj_name)
    
    output = StringIO()
    output.write(csv_data)
    output.seek(0)
    
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename
    )
