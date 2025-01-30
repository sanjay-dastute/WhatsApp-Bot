# Author: SANJAY KR
from .. import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Samaj(db.Model):
    __tablename__ = "samaj"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    members = relationship("Member", back_populates="samaj", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Samaj {self.name}>"

class Member(db.Model):
    __tablename__ = "member"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    samaj_id = db.Column(db.Integer, db.ForeignKey("samaj.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(5))
    mobile_1 = db.Column(db.String(15))
    mobile_2 = db.Column(db.String(15))
    education = db.Column(db.String(100))
    occupation = db.Column(db.String(100))
    marital_status = db.Column(db.String(20))
    address = db.Column(db.String(200))
    email = db.Column(db.String(100))
    birth_date = db.Column(db.String(10))
    anniversary_date = db.Column(db.String(10))
    native_place = db.Column(db.String(100))
    current_city = db.Column(db.String(100))
    languages_known = db.Column(db.String(200))
    skills = db.Column(db.String(200))
    hobbies = db.Column(db.String(200))
    emergency_contact = db.Column(db.String(15))
    relationship_status = db.Column(db.String(20))
    family_role = db.Column(db.String(50))
    medical_conditions = db.Column(db.String(200))
    dietary_preferences = db.Column(db.String(100))
    social_media_handles = db.Column(db.String(200))
    profession_category = db.Column(db.String(100))
    volunteer_interests = db.Column(db.String(200))

    samaj = relationship("Samaj", back_populates="members")

    def __repr__(self):
        return f"<Member {self.name} of {self.samaj.name if self.samaj else 'Unknown Samaj'}>"
