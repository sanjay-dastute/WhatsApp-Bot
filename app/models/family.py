from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Samaj(Base):
    __tablename__ = "samaj"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    members = relationship("Member", back_populates="samaj")

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True, index=True)
    samaj_id = Column(Integer, ForeignKey("samaj.id"))
    name = Column(String)
    gender = Column(String)
    age = Column(Integer)
    blood_group = Column(String)
    mobile_1 = Column(String)
    mobile_2 = Column(String, nullable=True)
    
    education = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    anniversary_date = Column(String, nullable=True)
    native_place = Column(String, nullable=True)
    current_city = Column(String, nullable=True)
    languages_known = Column(String, nullable=True)
    skills = Column(String, nullable=True)
    hobbies = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    relationship_status = Column(String, nullable=True)
    family_role = Column(String, nullable=True)
    medical_conditions = Column(String, nullable=True)
    dietary_preferences = Column(String, nullable=True)
    social_media_handles = Column(String, nullable=True)
    profession_category = Column(String, nullable=True)
    volunteer_interests = Column(String, nullable=True)

    samaj = relationship("Samaj", back_populates="members")
