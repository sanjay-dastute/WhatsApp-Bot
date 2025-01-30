# Author: SANJAY KR
from .. import db
from sqlalchemy.orm import relationship

class Samaj(db.Model):
    __tablename__ = "samaj"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, unique=True, index=True)
    members = relationship("Member", back_populates="samaj")

class Member(db.Model):
    __tablename__ = "members"
    id = db.Column(db.Integer, primary_key=True, index=True)
    samaj_id = db.Column(db.Integer, db.ForeignKey("samaj.id"))
    name = db.Column(db.String)
    gender = db.Column(db.String)
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String)
    mobile_1 = db.Column(db.String)
    mobile_2 = db.Column(db.String, nullable=True)
    
    education = db.Column(db.String, nullable=True)
    occupation = db.Column(db.String, nullable=True)
    marital_status = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    birth_date = db.Column(db.String, nullable=True)
    anniversary_date = db.Column(db.String, nullable=True)
    native_place = db.Column(db.String, nullable=True)
    current_city = db.Column(db.String, nullable=True)
    languages_known = db.Column(db.String, nullable=True)
    skills = db.Column(db.String, nullable=True)
    hobbies = db.Column(db.String, nullable=True)
    emergency_contact = db.Column(db.String, nullable=True)
    relationship_status = db.Column(db.String, nullable=True)
    family_role = db.Column(db.String, nullable=True)
    medical_conditions = db.Column(db.String, nullable=True)
    dietary_preferences = db.Column(db.String, nullable=True)
    social_media_handles = db.Column(db.String, nullable=True)
    profession_category = db.Column(db.String, nullable=True)
    volunteer_interests = db.Column(db.String, nullable=True)

    samaj = relationship("Samaj", back_populates="members")
