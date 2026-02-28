import logging

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


class BookingRequest(BaseModel):
    firstname: str
    lastname: str
    email: str
    phone: str
    service: str
    provider_name: str
    provider_phone: str | None = None
    provider_email: str | None = None
    date: str | None = None
    time: str | None = None


@router.post("/book")
async def book(req: BookingRequest):
    """
    Booking endpoint for Indian market.
    Returns WhatsApp link and contact information for manual inquiry.
    No automated payment or card provisioning.
    """
    logger.info(f"Booking request for {req.firstname} {req.lastname} - {req.service}")
    
    # Generate WhatsApp pre-filled message
    whatsapp_message = (
        f"Hi, I'm interested in {req.service}. "
        f"My name is {req.firstname} {req.lastname}. "
    )
    if req.date and req.time:
        whatsapp_message += f"I'd like to schedule for {req.date} at {req.time}. "
    whatsapp_message += "Could you please share your pricing and availability?"
    
    response = {
        "status": "success",
        "booking_type": "inquiry",
        "contact_methods": {
            "whatsapp": {
                "available": bool(req.provider_phone),
                "phone": req.provider_phone,
                "message": whatsapp_message,
                "link": f"https://wa.me/{req.provider_phone.replace('+', '').replace(' ', '')}?text={whatsapp_message}" if req.provider_phone else None
            },
            "phone": {
                "available": bool(req.provider_phone),
                "number": req.provider_phone
            },
            "email": {
                "available": bool(req.provider_email),
                "address": req.provider_email
            }
        }
    }
    
    return response
