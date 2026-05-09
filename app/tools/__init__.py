from app.tools.appointment_booking import book_appointment_tool
from app.tools.availibility import (
    check_availability_by_specialization,
)

CHAT_TOOLS = [
    check_availability_by_specialization,
    book_appointment_tool,
]

__all__ = [
    "check_availability_by_specialization",
    "check_availability_by_doctor_name",
    "book_appointment_tool",
    "CHAT_TOOLS",
]
