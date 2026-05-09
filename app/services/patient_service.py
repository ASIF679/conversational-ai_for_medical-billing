import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app.models.patient import Patient
from app.schemas.patient_details import PatientDetails, PatientAPIResponse, PatientResponse
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)


def get_or_create_patient(
    db: Session,
    request: PatientDetails
) -> PatientAPIResponse:
    try:
        # ── Step 1: Check by phone first (most reliable identifier) ──
        existing_patient = db.query(Patient).filter(
            Patient.phone == request.phone
        ).first()

        # ── Step 2: If not found by phone, check by email ─────────────
        if not existing_patient and request.email:
            existing_patient = db.query(Patient).filter(
                Patient.email == request.email
            ).first()

        # ── Step 3: Patient exists — return their details ─────────────
        if existing_patient:
            logger.info(
                f"Existing patient found: "
                f"{existing_patient.full_name} (ID: {existing_patient.id})"
            )
            return PatientAPIResponse(
                message = "Patient already exists",
                is_new  = False,
                data    = PatientResponse(
                    id        = str(existing_patient.id),
                    full_name = existing_patient.full_name,
                    email     = existing_patient.email,
                    phone     = existing_patient.phone
                )
            )

        # ── Step 4: New patient — create record ───────────────────────
        logger.info(f"Creating new patient: {request.full_name}")

        new_patient = Patient(
            full_name = request.full_name,
            email     = request.email,
            phone     = request.phone
        )

        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

        logger.info(
            f"New patient created: "
            f"{new_patient.full_name} (ID: {new_patient.id})"
        )

        return PatientAPIResponse(
            message = "Patient created successfully",
            is_new  = True,
            data    = PatientResponse(
                id        = str(new_patient.id),
                full_name = new_patient.full_name,
                email     = new_patient.email,
                phone     = new_patient.phone
            )
        )

    except ServiceError:
        raise

    except OperationalError as e:
        db.rollback()
        logger.error(f"DB connection error in patient service: {str(e)}")
        raise ServiceError(503, "Database connection failed. Please try again.")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in patient service: {str(e)}")
        raise ServiceError(500, "A database error occurred. Please try again.")

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in patient service: {str(e)}")
        raise ServiceError(500, "An unexpected error occurred. Please try again.")