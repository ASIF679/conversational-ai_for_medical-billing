from sqlalchemy import Column, String, Date, Time, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ── Foreign Keys ──────────────────────────────────────────────
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id  = Column(UUID(as_uuid=True), ForeignKey("doctors.id"),  nullable=False)

    # ── Appointment Details ───────────────────────────────────────
    appointment_date = Column(Date,   nullable=False)    
    appointment_time = Column(Time,   nullable=False)   
    reason           = Column(Text,   nullable=True)
    notes            = Column(Text,   nullable=True)  

    status = Column(String, default="scheduled")

    # ── Audit ─────────────────────────────────────────────────────
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────────
    patient = relationship("Patient")
    doctor  = relationship("Doctor", back_populates="appointments")