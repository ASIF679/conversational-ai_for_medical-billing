import logging
from fastapi import APIRouter, HTTPException
from app.schemas.email_schema import EmailRequest, EmailResponse
from app.services.email_service import send_booking_confirmation
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["Email"])


@router.post("/send-confirmation", response_model=EmailResponse)
def send_confirmation_email(request: EmailRequest):
    try:
        logger.info(f"POST /email/send-confirmation → {request.to_address}")

        result = send_booking_confirmation(
            to_address        = request.to_address,
            patient_full_name = request.patient_full_name,
            appointment_date  = request.appointment_date,
            appointment_time  = request.appointment_time,
            doctor_name       = request.doctor_name,
            location_name     = request.location_name,
        )

        return EmailResponse(
            success    = True,
            message    = result["message"],
            to_address = result["to_address"]
        )

    except ServiceError as e:
        logger.warning(f"ServiceError sending email: {e.code} - {e.message}")
        raise HTTPException(status_code=e.code, detail=e.message)

    except Exception as e:
        logger.error(f"Unhandled error in send_confirmation_email: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send email")