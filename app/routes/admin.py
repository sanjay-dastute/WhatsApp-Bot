# Author: SANJAY KR
from flask import Blueprint, request, jsonify, send_file
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..controllers.admin_controller import (
    get_members, get_samaj_list, get_member,
    export_members_csv
)
from ..controllers.auth_controller import verify_token
from io import StringIO
from ..utils.auth import login_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/members", methods=["GET"])
@login_required
def list_members():
    db = next(get_db())
    filters = {
        "samaj_name": request.args.get("samaj_name"),
        "family_name": request.args.get("family_name"),
        "name": request.args.get("name"),
        "role": request.args.get("role"),
        "age_min": request.args.get("age_min"),
        "age_max": request.args.get("age_max"),
        "blood_group": request.args.get("blood_group"),
        "city": request.args.get("city"),
        "profession": request.args.get("profession"),
        "is_family_head": request.args.get("is_family_head", type=bool)
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    members = get_members(db, filters)
    return jsonify([{
        "id": member.id,
        "samaj": member.samaj.name,
        "family": member.family.name,
        "name": member.name,
        "role": member.family_role,
        "age": member.age,
        "blood_group": member.blood_group,
        "mobile": member.mobile_1,
        "email": member.email,
        "city": member.current_city,
        "profession": member.profession_category,
        "is_family_head": member.is_family_head
    } for member in members])

@admin_bp.route("/samaj", methods=["GET"])
@login_required
def list_samaj():
    db = next(get_db())
    samaj_list = get_samaj_list(db)
    return jsonify([{
        "id": samaj.id,
        "name": samaj.name,
        "family_count": len(samaj.families),
        "member_count": len(samaj.members),
        "created_at": samaj.created_at
    } for samaj in samaj_list])

@admin_bp.route("/families", methods=["GET"])
@login_required
def list_families():
    db = next(get_db())
    filters = {
        "samaj_name": request.args.get("samaj_name"),
        "family_name": request.args.get("family_name")
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    families = get_family_summary(db, filters)
    return jsonify(families)

@admin_bp.route("/families/<int:family_id>/members", methods=["GET"])
@login_required
def get_family_members_list(family_id: int):
    db = next(get_db())
    members = get_family_members(db, family_id)
    return jsonify([{
        "id": member.id,
        "name": member.name,
        "role": member.family_role,
        "age": member.age,
        "is_family_head": member.is_family_head,
        "mobile": member.mobile_1,
        "email": member.email
    } for member in members])

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
    filters = {
        "samaj_name": request.args.get("samaj_name"),
        "family_name": request.args.get("family_name"),
        "name": request.args.get("name"),
        "role": request.args.get("role"),
        "city": request.args.get("city"),
        "profession": request.args.get("profession")
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    csv_data, filename = export_members_csv(db, filters)
    
    output = StringIO()
    output.write(csv_data)
    output.seek(0)
    
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename
    )
