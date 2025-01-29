from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..routes.auth import get_current_user
import csv
from fastapi.responses import StreamingResponse, JSONResponse
from io import StringIO
from ..models.base import get_db
from ..models.family import Samaj, Member
from typing import List, Dict, Any
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

router = APIRouter()

class MemberResponse(BaseModel):
    id: int
    samaj: str
    name: str
    gender: str
    age: int
    blood_group: str
    mobile_1: str
    mobile_2: str | None = None
    education: str | None = None
    occupation: str | None = None
    marital_status: str | None = None
    address: str | None = None
    email: str | None = None
    birth_date: str | None = None
    anniversary_date: str | None = None
    native_place: str | None = None
    current_city: str | None = None
    languages_known: str | None = None
    skills: str | None = None
    hobbies: str | None = None
    emergency_contact: str | None = None
    relationship_status: str | None = None
    family_role: str | None = None
    medical_conditions: str | None = None
    dietary_preferences: str | None = None
    social_media_handles: str | None = None
    profession_category: str | None = None
    volunteer_interests: str | None = None

class AnalyticsResponse(BaseModel):
    total_members: int
    members_by_samaj: Dict[str, int]
    gender_distribution: Dict[str, int]
    age_groups: Dict[str, int]
    marital_status_distribution: Dict[str, int]
    profession_categories: Dict[str, int]

@router.get("/members", response_model=List[MemberResponse])
async def get_members(
    samaj_name: str | None = None,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    query = db.query(Member)
    if samaj_name:
        query = query.join(Samaj).filter(Samaj.name == samaj_name)
    return query.all()

@router.get("/samaj")
async def get_samaj_list(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return db.query(Samaj).all()

@router.get("/members/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    member = db.query(Member).join(Samaj).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    member_dict = {
        "id": member.id,
        "samaj": db.query(Samaj).get(member.samaj_id).name,
        "name": member.name,
        "gender": member.gender,
        "age": member.age,
        "blood_group": member.blood_group,
        "mobile_1": member.mobile_1,
        "mobile_2": member.mobile_2,
        "education": member.education,
        "occupation": member.occupation,
        "marital_status": member.marital_status,
        "address": member.address,
        "email": member.email,
        "birth_date": member.birth_date,
        "anniversary_date": member.anniversary_date,
        "native_place": member.native_place,
        "current_city": member.current_city,
        "languages_known": member.languages_known,
        "skills": member.skills,
        "hobbies": member.hobbies,
        "emergency_contact": member.emergency_contact,
        "relationship_status": member.relationship_status,
        "family_role": member.family_role,
        "medical_conditions": member.medical_conditions,
        "dietary_preferences": member.dietary_preferences,
        "social_media_handles": member.social_media_handles,
        "profession_category": member.profession_category,
        "volunteer_interests": member.volunteer_interests
    }
    return member_dict

@router.post("/import/csv")
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode()))
        
        for _, row in df.iterrows():
            samaj = db.query(Samaj).filter(Samaj.name == row["samaj"]).first()
            if not samaj:
                samaj = Samaj(name=row["samaj"])
                db.add(samaj)
                db.flush()
            
            member = Member(
                samaj_id=samaj.id,
                name=row["name"],
                gender=row["gender"],
                age=int(row["age"]),
                blood_group=row["blood_group"],
                mobile_1=row["mobile_1"],
                mobile_2=row.get("mobile_2"),
                education=row.get("education"),
                occupation=row.get("occupation"),
                marital_status=row.get("marital_status"),
                address=row.get("address"),
                email=row.get("email"),
                birth_date=row.get("birth_date"),
                anniversary_date=row.get("anniversary_date"),
                native_place=row.get("native_place"),
                current_city=row.get("current_city"),
                languages_known=row.get("languages_known"),
                skills=row.get("skills"),
                hobbies=row.get("hobbies"),
                emergency_contact=row.get("emergency_contact"),
                relationship_status=row.get("relationship_status"),
                family_role=row.get("family_role"),
                medical_conditions=row.get("medical_conditions"),
                dietary_preferences=row.get("dietary_preferences"),
                social_media_handles=row.get("social_media_handles"),
                profession_category=row.get("profession_category"),
                volunteer_interests=row.get("volunteer_interests")
            )
            db.add(member)
        
        db.commit()
        return {"message": "Data imported successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    samaj_name: str | None = None,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    query = db.query(Member)
    if samaj_name:
        query = query.join(Samaj).filter(Samaj.name == samaj_name)
    
    members = query.all()
    total_members = len(members)
    
    # Calculate analytics
    members_by_samaj = {}
    gender_distribution = {}
    age_groups = {"0-18": 0, "19-30": 0, "31-50": 0, "51+": 0}
    marital_status_distribution = {}
    profession_categories = {}
    
    for member in members:
        # Samaj distribution
        samaj_name = db.query(Samaj).get(member.samaj_id).name
        members_by_samaj[samaj_name] = members_by_samaj.get(samaj_name, 0) + 1
        
        # Gender distribution
        gender_distribution[member.gender] = gender_distribution.get(member.gender, 0) + 1
        
        # Age groups
        age = member.age
        if age <= 18:
            age_groups["0-18"] += 1
        elif age <= 30:
            age_groups["19-30"] += 1
        elif age <= 50:
            age_groups["31-50"] += 1
        else:
            age_groups["51+"] += 1
        
        # Marital status
        if member.marital_status:
            marital_status_distribution[member.marital_status] = \
                marital_status_distribution.get(member.marital_status, 0) + 1
        
        # Profession categories
        if member.profession_category:
            profession_categories[member.profession_category] = \
                profession_categories.get(member.profession_category, 0) + 1
    
    return {
        "total_members": total_members,
        "members_by_samaj": members_by_samaj,
        "gender_distribution": gender_distribution,
        "age_groups": age_groups,
        "marital_status_distribution": marital_status_distribution,
        "profession_categories": profession_categories
    }

@router.get("/export/csv")
async def export_csv(
    samaj_name: str | None = None,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    query = db.query(Member)
    if samaj_name:
        query = query.join(Samaj).filter(Samaj.name == samaj_name)
    members = query.all()

    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    headers = ["Name", "Gender", "Age", "Blood Group", "Mobile 1", "Mobile 2",
               "Education", "Occupation", "Marital Status", "Address", "Email",
               "Birth Date", "Anniversary Date", "Native Place", "Current City",
               "Languages Known", "Skills", "Hobbies", "Emergency Contact",
               "Relationship Status", "Family Role", "Medical Conditions",
               "Dietary Preferences", "Social Media Handles", "Profession Category",
               "Volunteer Interests"]
    writer.writerow(headers)
    
    # Write data
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
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=members_{samaj_name or 'all'}.csv"}
    )
