import json
import logging
from langchain_core.tools import tool
from app.services.email_service import send_booking_confirmation
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)


@tool
def send_confirmation_email_tool(
    patient_email:    str,
    patient_name:     str,
    doctor_name:      str,
    appointment_date: str,
    appointment_time: str,
) -> str:
    """
    Send appointment confirmation email to patient.

    Call this IMMEDIATELY after book_appointment_tool succeeds.
    Never skip this step — patient needs email confirmation.

    Args:
        patient_email:    Patient email address e.g. "ali@gmail.com"
        patient_name:     Patient full name     e.g. "Ali Khan"
        doctor_name:      Doctor full name      e.g. "Dr. Sara Ahmed"
        appointment_date: Format YYYY-MM-DD     e.g. "2026-05-13"
        appointment_time: Format HH:MM          e.g. "14:00"
    """

    missing = []
    if not patient_email:    missing.append("patient_email")
    if not patient_name:     missing.append("patient_name")
    if not doctor_name:      missing.append("doctor_name")
    if not appointment_date: missing.append("appointment_date")
    if not appointment_time: missing.append("appointment_time")

    if missing:
        logger.warning(f"Email tool missing fields: {missing}")
        return json.dumps({
            "success":        False,
            "error":          f"Missing fields: {', '.join(missing)}",
            "say_to_patient": "Appointment booked but confirmation email could not be sent."
        })

    logger.info(f"Sending confirmation email to: {patient_email}")

    try:
        result = send_booking_confirmation(
            to_address        = patient_email,
            patient_full_name = patient_name,
            appointment_date  = appointment_date,
            appointment_time  = appointment_time,
            doctor_name       = doctor_name,
        )

        logger.info(f"Email sent successfully to: {patient_email}")

        return json.dumps({
            "success":        True,
            "message":        result["message"],
            "say_to_patient": (
                f"A confirmation email has been sent to {patient_email}. "
                f"Please check your inbox."
            )
        })

    # ── Handle Every Error Type ───────────────────────────────────
    except ServiceError as e:
        logger.warning(f"ServiceError in email tool: {e.code} - {e.message}")

        # Map error codes to patient friendly messages
        patient_messages = {
            400: f"The email address {patient_email} appears to be invalid.",
            401: "Email service authentication failed. Please contact support.",
            503: "Email service is temporarily unavailable. Please try again.",
            504: "Email service timed out. Your appointment is confirmed but email was not sent.",
        }

        patient_msg = patient_messages.get(
            e.code,
            "Your appointment is confirmed but the confirmation email could not be sent."
        )

        return json.dumps({
            "success":        False,
            "error":          e.message,
            "code":           e.code,
            "say_to_patient": patient_msg
        })

    except Exception as e:
        logger.error(f"Unexpected error in email tool: {str(e)}")
        return json.dumps({
            "success":        False,
            "error":          str(e),
            "say_to_patient": (
                "Your appointment is confirmed! "
                "However, the confirmation email could not be sent. "
                "Please note down your appointment details."
            )
        })