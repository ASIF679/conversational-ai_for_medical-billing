from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
import re


class EmailRequest(BaseModel):
    to_address:         str
    patient_full_name:  str
    appointment_date:   str        
    appointment_time:   str      
    doctor_name:        str
    location_name:      Optional[str] = None

    @validator('to_address')
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError("Email address is required")
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, v.strip()):
            raise ValueError(f"Invalid email format: {v}")
        return v.strip().lower()

    @validator('patient_full_name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Patient name is required")
        return v.strip()

    @validator('doctor_name')
    def validate_doctor(cls, v):
        if not v or not v.strip():
            raise ValueError("Doctor name is required")
        return v.strip()

    @validator('appointment_date')
    def validate_date(cls, v):
        if not v or not v.strip():
            raise ValueError("Appointment date is required")
        try:
            datetime.strptime(v.strip(), "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v.strip()

    @validator('appointment_time')
    def validate_time(cls, v):
        if not v or not v.strip():
            raise ValueError("Appointment time is required")
        # Handle HH:MM or HH:MM:SS
        clean = v.strip()[:5]
        try:
            datetime.strptime(clean, "%H:%M")
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
        return clean


class EmailResponse(BaseModel):
    success:    bool
    message:    str
    to_address: str