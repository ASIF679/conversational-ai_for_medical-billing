from datetime import datetime

BOOKING_CONFIRMATION_BODY = """Dear {ClientFirstName},

This email confirms your upcoming appointment at {AppointmentLocationName}.

Appointment Details:
─────────────────────────────
Doctor  : {DoctorName}
Date    : {AppointmentDate}
Time    : {AppointmentStartTime}
Location: {AppointmentLocationName}
─────────────────────────────

Please note our cancellation policy requires at least 24 hours notice.
To cancel or reschedule please contact us as soon as possible.

We look forward to seeing you!

Warm regards,
MedCare Team
"""


def _first_name(full_name: str) -> str:
    if not full_name or not full_name.strip():
        return "Patient"
    return full_name.strip().split()[0]


def render_booking_confirmation(
    client_full_name:          str,
    appointment_dt:            datetime,
    appointment_location_name: str,
    doctor_name:               str = "Your Doctor",     # ✅ added
) -> str:
    time_str = appointment_dt.strftime("%I:%M %p").lstrip("0")

    return BOOKING_CONFIRMATION_BODY.format(
        ClientFirstName          = _first_name(client_full_name),
        DoctorName               = doctor_name,             # ✅ added
        AppointmentDate          = appointment_dt.strftime("%B %d, %Y"),
        AppointmentStartTime     = time_str,
        AppointmentLocationName  = appointment_location_name,
    )