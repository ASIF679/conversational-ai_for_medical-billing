from pydantic import BaseModel, validator
from typing import Optional
import re

class PatientDetails(BaseModel):
    full_name: str
    email:     Optional[str] = None
    phone:     str

    @validator('full_name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Full name cannot be empty")
        if len(v.strip()) < 2:
            raise ValueError("Full name is too short")
        return v.strip().title()       # "ali khan" → "Ali Khan"

    @validator('phone')
    def validate_phone(cls, v):
        if not v or not v.strip():
            raise ValueError("Phone number is required")
        # Remove spaces and dashes for clean storage
        cleaned = re.sub(r'[\s\-]', '', v.strip())
        if len(cleaned) < 10:
            raise ValueError("Phone number is too short")
        return cleaned

    @validator('email')
    def validate_email(cls, v):
        if v is None:
            return v
        if not v.strip():
            return None
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.strip().lower()       # "ALI@GMAIL.COM" → "ali@gmail.com"


class PatientResponse(BaseModel):
    id:         str
    full_name:  str
    email:      Optional[str] = None
    phone:      str


class PatientAPIResponse(BaseModel):
    message:    str
    is_new:     bool
    data:       PatientResponse