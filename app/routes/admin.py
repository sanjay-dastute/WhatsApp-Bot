from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
    db: Session = Depends(get_db)
):
    query = db.query(Member)
    if samaj_name:
        query = query.join(Samaj).filter(Samaj.name == samaj_name)
    return query.all()

@router.get("/samaj")
async def get_samaj_list(db: Session = Depends(get_db)):
    return db.query(Samaj).all()

@router.get("/members/{member_id}", response_model=MemberResponse)
async def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member
