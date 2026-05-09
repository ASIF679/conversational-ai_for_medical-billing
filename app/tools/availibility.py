import json
import logging
from contextlib import contextmanager
from langchain_core.tools import tool
from app.db.database import SessionLocal
from app.schemas.availability import DoctorAvailabilityRequest
from app.services.availability_service import get_doctor_availability
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)

DAY_MAP = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

# ── Safe DB Session ───────────────────────────────────────────────
@contextmanager
def get_db_session():
    """
    Context manager for DB session.
    Always closes session even if tool crashes.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"DB session error: {str(e)}")
        raise
    finally:
        db.close()


# ── Helper: Format Slots ──────────────────────────────────────────
def _format_slots(availability_slots) -> list:
    """
    Convert raw slots into human readable format for LLM.
    Input:  day_of_week=2, start_time=11:00, end_time=16:00
    Output: {"day": "Wednesday", "start": "11:00", "end": "16:00"}
    """
    slots = []
    for slot in availability_slots:
        day_name = DAY_MAP.get(slot.day_of_week, "Unknown")
        slots.append({
            "day":   day_name,
            "start": str(slot.start_time)[:5],    # "11:00:00" → "11:00"
            "end":   str(slot.end_time)[:5],       # "16:00:00" → "16:00"
        })
    return slots


# ── Helper: Build Patient Message ────────────────────────────────
def _build_patient_message(doctor_name: str, slots: list) -> str:
    """
    Build a clear message for the bot to say to the patient.
    Example: "Dr. Sara Ahmed is available on:
               Wednesday 11:00 to 16:00
               Friday 09:00 to 13:00
               Which day works for you?"
    """
    if not slots:
        return f"{doctor_name} has no availability at the moment."

    slot_lines = "\n".join(
        f"  • {s['day']} from {s['start']} to {s['end']}"
        for s in slots
    )
    return (
        f"{doctor_name} is available on:\n"
        f"{slot_lines}\n"
        f"Which day and time works best for you?"
    )


# ── Main Tool ─────────────────────────────────────────────────────
@tool
def check_availability_by_specialization(specialization: str) -> str:
    """
    Find a doctor by specialization and return their availability.

    Use this tool when:
    - Patient mentions a type of doctor they need
    - Patient asks about booking an appointment
    - Patient asks who is available

    Input examples:
    - "dermatologist"
    - "cardiologist"
    - "neurologist"
    - "general physician"

    Returns:
    - doctor_id    (required for book_appointment)
    - doctor_name  (required for book_appointment and email)
    - available days and times to show patient
    """

    # ── Validate Input ────────────────────────────────────────────
    if not specialization or not specialization.strip():
        return json.dumps({
            "error": "Specialization is required",
            "say_to_patient": "What type of doctor are you looking for?"
        })

    logger.info(f"Tool called: check_availability_by_specialization({specialization})")

    with get_db_session() as db:
        try:
            # ── Call Service ──────────────────────────────────────
            req    = DoctorAvailabilityRequest(specialization=specialization.strip())
            result = get_doctor_availability(db, req)

            # ── Format Response ───────────────────────────────────
            slots   = _format_slots(result.availability)
            message = _build_patient_message(result.doctor_name, slots)

            response = {
                # ── For booking tool ──────────────────────────────
                "doctor_id":      str(result.doctor_id),
                "doctor_name":    result.doctor_name,
                "specialization": result.specialization,

                # ── For patient ───────────────────────────────────
                "slots":          slots,
                "say_to_patient": message,

                # ── Status ────────────────────────────────────────
                "success": True
            }

            logger.info(
                f"Availability found for {result.doctor_name}: "
                f"{len(slots)} slots"
            )

            return json.dumps(response)

        # ── Handle Known Errors ───────────────────────────────────
        except ServiceError as e:
            logger.warning(f"ServiceError in availability tool: {e.message}")

            # Give bot a message it can say to patient
            if e.code == 404:
                patient_msg = (
                    f"Sorry, no {specialization} doctor is available right now. "
                    f"Would you like to try a different specialization?"
                )
            elif e.code == 400:
                patient_msg = "Could you please tell me what type of doctor you need?"
            elif e.code == 503:
                patient_msg = "We are experiencing technical issues. Please try again in a moment."
            else:
                patient_msg = "Something went wrong. Please try again."

            return json.dumps({
                "error":          e.message,
                "code":           e.code,
                "say_to_patient": patient_msg,
                "success":        False
            })

        # ── Handle Unexpected Errors ──────────────────────────────
        except Exception as e:
            logger.error(
                f"Unexpected error in check_availability_by_specialization: {str(e)}"
            )
            return json.dumps({
                "error":          "Unexpected error occurred",
                "say_to_patient": "Sorry, something went wrong. Please try again.",
                "success":        False
            })