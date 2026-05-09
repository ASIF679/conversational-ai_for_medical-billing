import json
import logging
from contextlib import contextmanager
from langchain_core.tools import tool
from app.db.database import SessionLocal
from app.schemas.appointements_book import AppointmentRequest
from app.services.appointment_service import book_appointment
from app.services.errors import ServiceError
logger = logging.getLogger(__name__)


# ── Safe DB Session ───────────────────────────────────────────────
@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"DB session error: {str(e)}")
        raise
    finally:
        db.close()


# ── Tool ──────────────────────────────────────────────────────────
@tool
def book_appointment_tool(
    patient_id:       str,
    doctor_id:        str,
    appointment_date: str,
    appointment_time: str,
    reason:           str,
) -> str:
    """
    Book a confirmed appointment for a patient.

    ONLY call this tool after:
    - You have patient_id from register_or_get_patient tool
    - You have doctor_id from check_availability_by_specialization tool
    - Patient has confirmed the exact date and time
    - You have the reason for the visit

    Args:
        patient_id:       UUID string from patient tool
        doctor_id:        UUID string from availability tool
        appointment_date: Format YYYY-MM-DD  e.g. "2026-05-11"
        appointment_time: Format HH:MM       e.g. "11:00"
        reason:           Reason for visit   e.g. "Chest pain"

    Returns JSON with appointment details or error message.
    """

    # ── Validate All Inputs Present ───────────────────────────────
    missing = []
    if not patient_id:       missing.append("patient_id")
    if not doctor_id:        missing.append("doctor_id")
    if not appointment_date: missing.append("appointment_date")
    if not appointment_time: missing.append("appointment_time")
    if not reason:           missing.append("reason")

    if missing:
        msg = f"Missing required fields: {', '.join(missing)}"
        logger.warning(f"book_appointment_tool called with missing fields: {missing}")
        return json.dumps({
            "error":          msg,
            "say_to_patient": f"I still need: {', '.join(missing)} to complete the booking.",
            "success":        False
        })

    logger.info(
        f"book_appointment_tool called: "
        f"patient={patient_id} doctor={doctor_id} "
        f"date={appointment_date} time={appointment_time}"
    )

    with get_db_session() as db:
        try:
            # ── Build Request ─────────────────────────────────────
            req = AppointmentRequest(
                patient_id       = patient_id,
                doctor_id        = doctor_id,
                appointment_date = appointment_date,
                appointment_time = appointment_time,
                reason           = reason
            )

            # ── Call Service ──────────────────────────────────────
            result = book_appointment(db, req)

            logger.info(f"Appointment booked successfully: {result.appointment_id}")

            return json.dumps({
                "success":          True,
                "appointment_id":   str(result.appointment_id),
                "patient_name":     result.patient_name,
                "doctor_name":      result.doctor_name,
                "appointment_date": str(result.appointment_date),
                "appointment_time": str(result.appointment_time),
                "status":           result.status,
                "reason":           result.reason,

                # ✅ Bot says this to patient
                "say_to_patient": (
                    f"Your appointment is confirmed!\n"
                    f"Doctor : {result.doctor_name}\n"
                    f"Date   : {result.appointment_date}\n"
                    f"Time   : {result.appointment_time}\n"
                    f"Status : {result.status}\n"
                    f"A confirmation email will be sent shortly."
                )
            })

        # ── Known Errors ──────────────────────────────────────────
        except ServiceError as e:
            logger.warning(f"ServiceError in book_appointment_tool: {e.code} - {e.message}")

            if e.code == 404:
                patient_msg = e.message
            elif e.code == 400:
                patient_msg = e.message
            elif e.code == 409:
                patient_msg = (
                    "That time slot is already taken. "
                    "Would you like to choose a different time?"
                )
            elif e.code == 503:
                patient_msg = "We are experiencing technical issues. Please try again."
            else:
                patient_msg = "Something went wrong with the booking. Please try again."

            return json.dumps({
                "error":          e.message,
                "code":           e.code,
                "say_to_patient": patient_msg,
                "success":        False
            })

        # ── Unknown Errors ────────────────────────────────────────
        except Exception as e:
            logger.error(f"Unexpected error in book_appointment_tool: {str(e)}")
            return json.dumps({
                "error":          "Unexpected error occurred",
                "say_to_patient": "Sorry, the booking failed unexpectedly. Please try again.",
                "success":        False
            })