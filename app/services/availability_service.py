from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError, TimeoutError
from app.models.doctors import Doctor
from app.models.availability import DoctorAvailability
from app.schemas.availability import (
    DoctorAvailabilityRequest,
    DoctorAvailabilityResponse,
    AvailabilitySlot,
)
from app.services.errors import ServiceError
import logging

logger = logging.getLogger(__name__)


def get_doctor_availability(
    db: Session,
    request: DoctorAvailabilityRequest
) -> DoctorAvailabilityResponse:
    try:
        if not request.specialization or not request.specialization.strip():
            raise ServiceError(400, "Specialization is required")

        logger.info(f"Searching doctor for specialization: {request.specialization}")

        # ── Find Doctor ───────────────────────────────────────────
        doctor = (
            db.query(Doctor)
            .filter(
                Doctor.specialization.ilike(f"%{request.specialization}%"),
                Doctor.is_active == True
            )
            .first()
        )

        if not doctor:
            logger.warning(f"No doctor found for specialization: {request.specialization}")
            raise ServiceError(
                404,
                f"No active {request.specialization} doctor found. "
                f"Please try another specialization."
            )

        logger.info(f"Doctor found: {doctor.full_name} (ID: {doctor.id})")

        # ── Find Availability Slots ───────────────────────────────
        slots = (
            db.query(DoctorAvailability)
            .filter(DoctorAvailability.doctor_id == doctor.id)
            .order_by(DoctorAvailability.day_of_week) 
            .all()
        )

        if not slots:
            logger.warning(f"No availability slots for doctor: {doctor.full_name}")
            raise ServiceError(
                404,
                f"Dr. {doctor.full_name} has no availability scheduled. "
                f"Please try another doctor."
            )

        # ── Build Response ────────────────────────────────────────
        availability_slots = [
            AvailabilitySlot(
                day_of_week = slot.day_of_week,
                start_time  = slot.start_time,
                end_time    = slot.end_time,
            )
            for slot in slots
        ]

        logger.info(
            f"Returning {len(availability_slots)} slots "
            f"for Dr. {doctor.full_name}"
        )

        return DoctorAvailabilityResponse(
            doctor_id      = doctor.id,
            doctor_name    = doctor.full_name,
            specialization = doctor.specialization,
            availability   = availability_slots,
        )

    except ServiceError:
        raise

    except OperationalError as e:
        logger.error(f"DB connection error: {str(e)}")
        raise ServiceError(503, "Database connection failed. Please try again.")

    except TimeoutError as e:
        logger.error(f"DB timeout: {str(e)}")
        raise ServiceError(504, "Request timed out. Please try again.")

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise ServiceError(500, "A database error occurred. Please try again.")

    except Exception as e:
        logger.error(f"Unexpected error in get_doctor_availability: {str(e)}")
        raise ServiceError(500, "An unexpected error occurred. Please try again.")