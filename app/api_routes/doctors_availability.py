from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.availability import DoctorAvailabilityRequest, DoctorAvailabilityResponse
from app.services.availability_service import get_doctor_availability as get_availability_svc
from app.services.errors import ServiceError

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("/availability")
def get_doctor_availability(
    request: DoctorAvailabilityRequest,
    db: Session = Depends(get_db),
) -> DoctorAvailabilityResponse:
    try:
        return get_availability_svc(db, request)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
