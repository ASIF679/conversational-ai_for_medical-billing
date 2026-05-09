# app/tools/patient_tool.py

import json
import logging
from contextlib import contextmanager
from langchain_core.tools import tool
from app.db.database import SessionLocal
from app.schemas.patient_details import PatientDetails
from app.services.patient_service import get_or_create_patient
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
def get_or_create_patient_tool(
    full_name: str,
    phone:     str,
    email:     str = "",
) -> str:
    """
    Register a new patient or retrieve an existing one.

    Use this tool after collecting patient details from conversation.
    Always collect phone number first — it is required.
    Email is optional but recommended for confirmation emails.

    Call this tool when you have:
    - Patient full name
    - Patient phone number
    - Patient email (if provided)

    Returns patient_id which is REQUIRED for book_appointment_tool.

    Args:
        full_name: Patient full name  e.g. "Ali Khan"
        phone:     Phone number       e.g. "03011111111"
        email:     Email address      e.g. "ali@gmail.com" (optional)
    """

    # ── Validate Required Fields ──────────────────────────────────
    missing = []
    if not full_name or not full_name.strip(): missing.append("full_name")
    if not phone     or not phone.strip():     missing.append("phone")

    if missing:
        logger.warning(f"Patient tool missing fields: {missing}")
        return json.dumps({
            "error":          f"Missing required fields: {', '.join(missing)}",
            "say_to_patient": f"Could you please provide your {' and '.join(missing)}?",
            "success":        False
        })

    logger.info(f"get_or_create_patient_tool called: name={full_name} phone={phone}")

    with get_db_session() as db:
        try:
            # ── Build Request ─────────────────────────────────────
            req = PatientDetails(
                full_name = full_name,
                phone     = phone,
                email     = email if email else None
            )

            # ── Call Service ──────────────────────────────────────
            result = get_or_create_patient(db, req)

            logger.info(
                f"Patient {'created' if result.is_new else 'found'}: "
                f"{result.data.full_name} (ID: {result.data.id})"
            )

            # ── Different message for new vs existing patient ─────
            if result.is_new:
                patient_msg = (
                    f"Welcome {result.data.full_name}! "
                    f"I have created your patient record."
                )
            else:
                patient_msg = (
                    f"Welcome back {result.data.full_name}! "
                    f"I found your existing record."
                )

            return json.dumps({
                "success":    True,
                "is_new":     result.is_new,

                # ── These go to book_appointment_tool ─────────────
                "patient_id":    result.data.id,
                "patient_name":  result.data.full_name,
                "patient_email": result.data.email,
                "patient_phone": result.data.phone,

                # ── Bot says this to patient ──────────────────────
                "say_to_patient": patient_msg
            })

        # ── Known Errors ──────────────────────────────────────────
        except ServiceError as e:
            logger.warning(f"ServiceError in patient tool: {e.code} - {e.message}")

            if e.code == 503:
                patient_msg = "We are experiencing technical issues. Please try again."
            else:
                patient_msg = "Something went wrong. Please try again."

            return json.dumps({
                "error":          e.message,
                "code":           e.code,
                "say_to_patient": patient_msg,
                "success":        False
            })

        # ── Unknown Errors ────────────────────────────────────────
        except Exception as e:
            logger.error(f"Unexpected error in patient tool: {str(e)}")
            return json.dumps({
                "error":          "Unexpected error occurred",
                "say_to_patient": "Sorry, something went wrong. Please try again.",
                "success":        False
            })