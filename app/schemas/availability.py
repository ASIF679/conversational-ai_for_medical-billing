from pydantic import BaseModel
from typing import Optional
from typing import List
from datetime import time
from uuid import UUID

class DoctorAvailabilityRequest(BaseModel):
    specialization:str


class AvailabilitySlot(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time

class DoctorAvailabilityResponse(BaseModel):
    doctor_id: UUID
    doctor_name: str
    specialization: str
    availability: List[AvailabilitySlot]
