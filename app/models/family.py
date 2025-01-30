# Author: SANJAY KR
from .. import db
from sqlalchemy.orm import relationship
from sqlalchemy import event
from datetime import datetime

class Family(db.Model):
    __tablename__ = "family"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    samaj_id = db.Column(db.Integer, db.ForeignKey("samaj.id", ondelete="CASCADE"), nullable=False)
    head_of_family_id = db.Column(db.Integer, db.ForeignKey("member.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    members = relationship("Member", back_populates="family", foreign_keys="Member.family_id")
    samaj = relationship("Samaj", back_populates="families")

class Samaj(db.Model):
    __tablename__ = "samaj"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    families = relationship("Family", back_populates="samaj", cascade="all, delete-orphan")
    members = relationship("Member", back_populates="samaj", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Samaj {self.name}>"

class Member(db.Model):
    __tablename__ = "member"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    samaj_id = db.Column(db.Integer, db.ForeignKey("samaj.id", ondelete="CASCADE"), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id", ondelete="CASCADE"), nullable=False)
    is_family_head = db.Column(db.Boolean, default=False)
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
    family = relationship("Family", back_populates="members", foreign_keys=[family_id])

    def validate_family_role(self):
        if self.family_role == "Head" and not self.is_family_head:
            raise ValueError("Member with Head role must be marked as family head")
        if self.family_role == "Spouse":
            existing_spouse = Member.query.filter(
                Member.family_id == self.family_id,
                Member.family_role == "Spouse",
                Member.id != self.id
            ).first()
            if existing_spouse:
                raise ValueError("Family already has a spouse member")
        if self.family_role == "Parent":
            existing_parents = Member.query.filter(
                Member.family_id == self.family_id,
                Member.family_role == "Parent",
                Member.id != self.id
            ).count()
            if existing_parents >= 2:
                raise ValueError("Family cannot have more than two parents")

    def __repr__(self):
        return f"<Member {self.name} of {self.samaj.name if self.samaj else 'Unknown Samaj'}>"

@event.listens_for(Member, 'before_insert')
@event.listens_for(Member, 'before_update')
def validate_member(mapper, connection, target):
    target.validate_family_role()

@event.listens_for(Member, 'after_insert')
def update_family_head(mapper, connection, target):
    if target.is_family_head:
        connection.execute(
            Family.__table__.update().
            where(Family.id == target.family_id).
            values(head_of_family_id=target.id)
        )
