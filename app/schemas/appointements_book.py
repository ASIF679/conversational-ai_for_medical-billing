# app/schemas/appointements_book.py

from pydantic import BaseModel, validator
from datetime import date, time
from uuid import UUID
from typing import Optional
from enum import Enum


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"
    no_show   = "no_show"


class AppointmentRequest(BaseModel):
    patient_id:       UUID
    doctor_id:        UUID
    appointment_date: date
    appointment_time: time
    reason:           Optional[str] = None

    @validator('appointment_time', pre=True)
    def strip_timezone_and_microseconds(cls, v):
        """
        Input:  "10:09:41.244Z"
        Output: time(10, 9, 0) → "10:09:00"
        """
        if isinstance(v, time):
            return v.replace(tzinfo=None, microsecond=0)
        return v

    @validator('appointment_date', pre=True)
    def validate_not_past(cls, v):
        from datetime import date as date_type
        if isinstance(v, date_type) and v < date_type.today():
            raise ValueError("Appointment date cannot be in the past")
        return v


class AppointmentResponse(BaseModel):
    appointment_id:   UUID
    patient_name:     str
    doctor_name:      str
    appointment_date: date
    appointment_time: time
    status:           AppointmentStatus
    reason:           Optional[str] = None

    class Config:
        from_attributes = True