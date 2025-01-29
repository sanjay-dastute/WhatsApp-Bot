from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..routes.auth import get_current_user
import csv
from fastapi.responses import StreamingResponse
from io import StringIO
from ..models.base import get_db
from ..models.family import Samaj, Member
from typing import List
from pydantic import BaseModel

router = APIRouter()

class MemberResponse(BaseModel):
    id: int
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
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

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
               "Education", "Occupation", "Marital Status", "Address", "Email"]
    writer.writerow(headers)
    
    # Write data
    for member in members:
        writer.writerow([
            member.name, member.gender, member.age, member.blood_group,
            member.mobile_1, member.mobile_2, member.education,
            member.occupation, member.marital_status, member.address,
            member.email
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=members_{samaj_name or 'all'}.csv"}
    )
