from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..models.family import Samaj, Member
from ..services.whatsapp_service import WhatsAppService

router = APIRouter()
whatsapp_service = WhatsAppService()

@router.post("/webhook")
async def webhook(
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db)
):
    phone_number = From.replace("whatsapp:", "")
    response = whatsapp_service.handle_message(phone_number, Body)
    
    session = whatsapp_service.current_sessions.get(phone_number)
    if session and session["step"] >= 26:
        try:
            data = session["data"]
            samaj = db.query(Samaj).filter(Samaj.name == data["samaj"]).first()
            if not samaj:
                samaj = Samaj(name=data["samaj"])
                db.add(samaj)
                db.flush()

            member = Member(
                samaj_id=samaj.id,
                name=data["name"],
                gender=data["gender"],
                age=int(data["age"]),
                blood_group=data["blood_group"],
                mobile_1=data["mobile_1"],
                mobile_2=data["mobile_2"],
                education=data["education"],
                occupation=data["occupation"],
                marital_status=data["marital_status"],
                address=data["address"],
                email=data["email"],
                birth_date=data["birth_date"],
                anniversary_date=data.get("anniversary_date"),
                native_place=data["native_place"],
                current_city=data["current_city"],
                languages_known=data["languages_known"],
                skills=data["skills"],
                hobbies=data["hobbies"],
                emergency_contact=data["emergency_contact"],
                relationship_status=data["relationship_status"],
                family_role=data["family_role"],
                medical_conditions=data.get("medical_conditions"),
                dietary_preferences=data["dietary_preferences"],
                social_media_handles=data.get("social_media_handles"),
                profession_category=data["profession_category"],
                volunteer_interests=data.get("volunteer_interests")
            )
            db.add(member)
            db.commit()
            del whatsapp_service.current_sessions[phone_number]
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    whatsapp_service.send_message(phone_number, response)
    return {"success": True}
