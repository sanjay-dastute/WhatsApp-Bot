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
    if session and session["step"] >= 12:
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
                email=data["email"]
            )
            db.add(member)
            db.commit()
            del whatsapp_service.current_sessions[phone_number]
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    whatsapp_service.send_message(phone_number, response)
    return {"success": True}
