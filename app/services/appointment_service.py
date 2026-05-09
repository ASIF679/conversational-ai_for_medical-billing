import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from datetime import datetime, date, time
from app.models.appointment import Appointment
from app.models.doctors import Doctor
from app.models.patient import Patient
from app.models.availability import DoctorAvailability
from app.schemas.appointements_book import AppointmentRequest, AppointmentResponse
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)


def book_appointment(
    db: Session,
    request: AppointmentRequest
) -> AppointmentResponse:
    try:
        # ── Strip timezone safety net ─────────────────────────────
        clean_time = request.appointment_time.replace(tzinfo=None, microsecond=0)

        logger.info(
            f"Booking attempt: patient={request.patient_id} "
            f"doctor={request.doctor_id} "
            f"date={request.appointment_date} "
            f"time={clean_time}"
        )

        # ── Step 1: Validate patient exists ───────────────────────
        patient = db.query(Patient).filter(
            Patient.id == request.patient_id
        ).first()

        if not patient:
            logger.warning(f"Patient not found: {request.patient_id}")
            raise ServiceError(404, "Patient not found")

        # ── Step 2: Validate doctor exists and is active ──────────
        doctor = db.query(Doctor).filter(
            Doctor.id        == request.doctor_id,
            Doctor.is_active == True
        ).first()

        if not doctor:
            logger.warning(f"Doctor not found or inactive: {request.doctor_id}")
            raise ServiceError(404, "Doctor not found or inactive")

        # ── Step 3: Validate day is in doctor's schedule ──────────
        day_of_week = request.appointment_date.weekday()
        logger.info(f"Checking availability for day_of_week={day_of_week}")

        availability = db.query(DoctorAvailability).filter(
            DoctorAvailability.doctor_id   == request.doctor_id,
            DoctorAvailability.day_of_week == day_of_week
        ).first()

        if not availability:
            raise ServiceError(400,
                f"Dr. {doctor.full_name} is not available on "
                f"{request.appointment_date.strftime('%A')}. "
                f"Please choose a different day."
            )

        # ── Step 4: Validate time within window ───────────────────
        if not (availability.start_time <= clean_time <= availability.end_time):
            raise ServiceError(400,
                f"Dr. {doctor.full_name} is only available between "
                f"{availability.start_time.strftime('%I:%M %p')} and "
                f"{availability.end_time.strftime('%I:%M %p')}. "
                f"Please choose a time within this window."
            )

        # ── Step 5: Check double booking ──────────────────────────
        conflict = db.query(Appointment).filter(
            Appointment.doctor_id        == request.doctor_id,
            Appointment.appointment_date == request.appointment_date,
            Appointment.appointment_time == clean_time,
            Appointment.status.notin_(["cancelled", "no_show"])
        ).first()

        if conflict:
            logger.warning(
                f"Double booking attempt: doctor={request.doctor_id} "
                f"date={request.appointment_date} time={clean_time}"
            )
            raise ServiceError(409,
                "This time slot is already booked. "
                "Please choose a different time."
            )

        # ── Step 6: Create appointment ────────────────────────────
        appointment = Appointment(
            patient_id       = request.patient_id,
            doctor_id        = request.doctor_id,
            appointment_date = request.appointment_date,
            appointment_time = clean_time,
            reason           = request.reason,
            status           = "scheduled"
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        logger.info(f"Appointment created successfully: {appointment.id}")

        # ── Step 7: Return response ───────────────────────────────
        return AppointmentResponse(
            appointment_id   = appointment.id,
            patient_name     = patient.full_name,
            doctor_name      = doctor.full_name,
            appointment_date = appointment.appointment_date,
            appointment_time = appointment.appointment_time,
            status           = appointment.status,
            reason           = appointment.reason
        )

    except ServiceError:
        raise

    except OperationalError as e:
        db.rollback()
        logger.error(f"DB connection error: {str(e)}")
        raise ServiceError(503, "Database connection failed. Please try again.")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise ServiceError(500, "A database error occurred. Please try again.")

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in book_appointment: {str(e)}")
        raise ServiceError(500, "An unexpected error occurred. Please try again.")