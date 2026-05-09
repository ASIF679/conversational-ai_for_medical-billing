from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.database import get_db
from app.schemas.patient_details import PatientDetails
from app.models.patient import Patient
import traceback

router = APIRouter(prefix="/Patient_details", tags=["Appointments"])

@router.post("/patient_record")
def check_patient_details(request: PatientDetails, db: Session = Depends(get_db)):
    try:
        # Check if patient already exists
        existing_user = db.query(Patient).filter(
            Patient.email == request.email,
            Patient.full_name == request.full_name
        ).first()

        if existing_user:
            return {
                "message": "User already exists",
                "data": {
                    "id": str(existing_user.id),
                    "name": existing_user.full_name,
                    "email": existing_user.email,
                    "phone": existing_user.phone   
                }
            }

        # Create new patient
        new_patient = Patient(
            full_name=request.full_name,        
            email=request.email,
            phone=request.phone    
        )

        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

        return {
            "message": "Patient created successfully",
            "data": {
                "id": str(new_patient.id),
                "name": new_patient.full_name,
                "email": new_patient.email,
                "phone": new_patient.phone      
            }
        }

    except SQLAlchemyError as e:
        db.rollback()
        traceback.print_exc()  
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )

    except Exception as e:
        traceback.print_exc()  
        raise HTTPException(
            status_code=500,
            detail="Unexpected error"
        )