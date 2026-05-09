from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

class Doctor(Base):
    __tablename__ = "doctors"
    
    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name      = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    phone          = Column(String, nullable=True)
    email          = Column(String, unique=True, nullable=True)
    is_active      = Column(Boolean, default=True)

    availability   = relationship(       
        "DoctorAvailability",
        back_populates="doctor",
        lazy="joined"
    )
    appointments   = relationship(              
        "Appointment",
        back_populates="doctor"
    )