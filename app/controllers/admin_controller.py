# Author: SANJAY KR
from sqlalchemy.orm import Session
from ..models.family import Samaj, Member
import csv
from io import StringIO
from typing import List, Optional

def get_members(db: Session, samaj_name: Optional[str] = None) -> List[Member]:
    query = db.query(Member)
    if samaj_name:
        query = query.join(Samaj).filter(Samaj.name == samaj_name)
    return query.all()

def get_samaj_list(db: Session) -> List[Samaj]:
    return db.query(Samaj).all()

def get_member(db: Session, member_id: int) -> Optional[Member]:
    return db.query(Member).filter(Member.id == member_id).first()

def export_members_csv(db: Session, samaj_name: Optional[str] = None) -> tuple[str, str]:
    members = get_members(db, samaj_name)
    
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
