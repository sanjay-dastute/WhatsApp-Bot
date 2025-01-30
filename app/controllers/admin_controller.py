# Author: SANJAY KR
from sqlalchemy.orm import Session
from ..models.family import Samaj, Member
import csv
from io import StringIO
from typing import List, Optional

def get_members(db: Session, filters: dict = None) -> List[Member]:
    query = db.query(Member).join(Family).join(Samaj)
    
    if not filters:
        return query.all()
        
    if filters.get("samaj_name"):
        query = query.filter(Samaj.name.ilike(f"%{filters['samaj_name']}%"))
        
    if filters.get("family_name"):
        query = query.filter(Family.name.ilike(f"%{filters['family_name']}%"))
        
    if filters.get("name"):
        query = query.filter(Member.name.ilike(f"%{filters['name']}%"))
        
    if filters.get("role"):
        query = query.filter(Member.family_role == filters["role"])
        
    if filters.get("age_min"):
        query = query.filter(Member.age >= int(filters["age_min"]))
        
    if filters.get("age_max"):
        query = query.filter(Member.age <= int(filters["age_max"]))
        
    if filters.get("blood_group"):
        query = query.filter(Member.blood_group == filters["blood_group"])
        
    if filters.get("city"):
        query = query.filter(Member.current_city.ilike(f"%{filters['city']}%"))
        
    if filters.get("profession"):
        query = query.filter(Member.profession_category.ilike(f"%{filters['profession']}%"))
        
    if filters.get("is_family_head") is not None:
        query = query.filter(Member.is_family_head == filters["is_family_head"])
        
    return query.all()

def get_samaj_list(db: Session) -> List[Samaj]:
    return db.query(Samaj).all()

def get_family_list(db: Session, samaj_name: Optional[str] = None) -> List[Family]:
    query = db.query(Family).join(Samaj)
    if samaj_name:
        query = query.filter(Samaj.name.ilike(f"%{samaj_name}%"))
    return query.all()

def get_family_members(db: Session, family_id: int) -> List[Member]:
    return db.query(Member).filter(Member.family_id == family_id).all()

def get_family_summary(db: Session, filters: dict = None) -> List[dict]:
    query = db.query(Family).join(Samaj).join(Member)
    
    if filters:
        if filters.get("samaj_name"):
            query = query.filter(Samaj.name.ilike(f"%{filters['samaj_name']}%"))
        if filters.get("family_name"):
            query = query.filter(Family.name.ilike(f"%{filters['family_name']}%"))
            
    families = query.all()
    result = []
    
    for family in families:
        head = next((m for m in family.members if m.is_family_head), None)
        result.append({
            "id": family.id,
            "name": family.name,
            "samaj": family.samaj.name,
            "head_name": head.name if head else None,
            "member_count": len(family.members),
            "created_at": family.created_at
        })
    
    return result

def get_member(db: Session, member_id: int) -> Optional[Member]:
    return db.query(Member).filter(Member.id == member_id).first()

def export_members_csv(db: Session, filters: dict = None) -> tuple[str, str]:
    members = get_members(db, filters)
    
    output = StringIO()
    writer = csv.writer(output)
    
    headers = ["Name", "Gender", "Age", "Blood Group", "Mobile 1", "Mobile 2",
               "Education", "Occupation", "Marital Status", "Address", "Email",
               "Birth Date", "Anniversary Date", "Native Place", "Current City",
               "Languages Known", "Skills", "Hobbies", "Emergency Contact",
               "Relationship Status", "Family Role", "Medical Conditions",
               "Dietary Preferences", "Social Media Handles", "Profession Category",
               "Volunteer Interests"]
    writer.writerow(headers)
    
    for member in members:
        writer.writerow([
            member.name, member.gender, member.age, member.blood_group,
            member.mobile_1, member.mobile_2, member.education,
            member.occupation, member.marital_status, member.address,
            member.email, member.birth_date, member.anniversary_date,
            member.native_place, member.current_city, member.languages_known,
            member.skills, member.hobbies, member.emergency_contact,
            member.relationship_status, member.family_role, member.medical_conditions,
            member.dietary_preferences, member.social_media_handles,
            member.profession_category, member.volunteer_interests
        ])
    
    output.seek(0)
    filename = f"members_{samaj_name or 'all'}.csv"
    return output.getvalue(), filename
