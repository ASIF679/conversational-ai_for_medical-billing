# app/api_routes/appointment_book.py

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.appointements_book import AppointmentRequest, AppointmentResponse
from app.services.appointment_service import book_appointment
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/book", response_model=AppointmentResponse)
def create_appointment(
    request: AppointmentRequest,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"POST /appointments/book called")
        return book_appointment(db, request)

    except ServiceError as e:
        logger.warning(f"ServiceError: {e.code} - {e.message}")
        raise HTTPException(status_code=e.code, detail=e.message)  # ✅ e.code

    except Exception as e:
        logger.error(f"Unhandled error in create_appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")