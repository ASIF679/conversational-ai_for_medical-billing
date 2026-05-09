import logging
import smtplib
import socket
from datetime import datetime
from email.message import EmailMessage
from app.core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
    APPOINTMENT_LOCATION_NAME,
)
from app.services.email_template import render_booking_confirmation
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)


def _validate_smtp_config() -> None:
    if not SMTP_HOST:
        raise ServiceError(500, "SMTP_HOST is not configured")
    if not SMTP_FROM_EMAIL:
        raise ServiceError(500, "SMTP_FROM_EMAIL is not configured")
    if not SMTP_USER:
        raise ServiceError(500, "SMTP_USER is not configured")

    password = (SMTP_PASSWORD or "").strip().strip('"').strip("'")
    if not password:
        raise ServiceError(
            500,
            "SMTP_PASSWORD is not configured. "
            "Create a Google App Password: "
            "Account → Security → 2-Step Verification → App Passwords"
        )
    return password


def _build_appointment_datetime(date_str: str, time_str: str) -> datetime:
    try:
        return datetime.strptime(
            f"{date_str} {time_str}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError as e:
        raise ServiceError(
            400,
            f"Invalid date or time format: {str(e)}"
        )


# ── Core Email Sender ─────────────────────────────────────────────
def _send_email(
    to_address: str,
    subject:    str,
    body:       str
) -> None:
    password = _validate_smtp_config()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = SMTP_FROM_EMAIL
    msg["To"]      = to_address
    msg.set_content(body)

    try:
        logger.info(f"Connecting to SMTP: {SMTP_HOST}:{SMTP_PORT}")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, password)
            server.send_message(msg)

            logger.info(f"Email sent successfully to: {to_address}")

    # ── Specific SMTP Errors ──────────────────────────────────────
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed")
        raise ServiceError(
            401,
            "Email authentication failed. "
            "Check your SMTP credentials or App Password."
        )

    except smtplib.SMTPRecipientsRefused:
        logger.error(f"Recipient refused: {to_address}")
        raise ServiceError(
            400,
            f"Email address {to_address} was refused by the mail server. "
            "Please check the email address."
        )

    except smtplib.SMTPSenderRefused:
        logger.error(f"Sender refused: {SMTP_FROM_EMAIL}")
        raise ServiceError(
            500,
            "Sender email was refused. Check SMTP_FROM_EMAIL configuration."
        )

    except smtplib.SMTPDataError as e:
        logger.error(f"SMTP data error: {str(e)}")
        raise ServiceError(
            500,
            "Email server rejected the message content."
        )

    except smtplib.SMTPConnectError:
        logger.error(f"Could not connect to SMTP server: {SMTP_HOST}:{SMTP_PORT}")
        raise ServiceError(
            503,
            "Cannot connect to email server. Please try again."
        )

    except smtplib.SMTPServerDisconnected:
        logger.error("SMTP server disconnected unexpectedly")
        raise ServiceError(
            503,
            "Email server disconnected. Please try again."
        )

    except socket.timeout:
        logger.error(f"SMTP connection timed out: {SMTP_HOST}:{SMTP_PORT}")
        raise ServiceError(
            504,
            "Email server timed out. Please try again."
        )

    except socket.gaierror:
        logger.error(f"DNS resolution failed for SMTP host: {SMTP_HOST}")
        raise ServiceError(
            503,
            "Cannot reach email server. Check network connection."
        )

    except Exception as e:
        logger.error(f"Unexpected email error: {str(e)}")
        raise ServiceError(
            500,
            f"Unexpected error sending email: {str(e)}"
        )


# ── Main Service Function ─────────────────────────────────────────
def send_booking_confirmation(
    to_address:        str,
    patient_full_name: str,
    appointment_date:  str,
    appointment_time:  str,
    doctor_name:       str,
    location_name:     str = None,
) -> dict:
    try:
        logger.info(
            f"Sending confirmation email to: {to_address} "
            f"for patient: {patient_full_name}"
        )

        # ── Build datetime ────────────────────────────────────────
        appointment_dt = _build_appointment_datetime(
            appointment_date,
            appointment_time
        )

        # ── Render template ───────────────────────────────────────
        loc  = location_name or APPOINTMENT_LOCATION_NAME or "Our Clinic"
        body = render_booking_confirmation(
            client_full_name          = patient_full_name,
            appointment_dt            = appointment_dt,
            appointment_location_name = loc,
            doctor_name               = doctor_name,
        )

        subject = (
            f"Appointment Confirmation — "
            f"{appointment_dt.strftime('%B %d, %Y')} "
            f"at {appointment_dt.strftime('%I:%M %p')}"
        )

        # ── Send ──────────────────────────────────────────────────
        _send_email(to_address, subject, body)

        logger.info(f"Confirmation email delivered to: {to_address}")

        return {
            "success":    True,
            "message":    f"Confirmation email sent to {to_address}",
            "to_address": to_address
        }

    except ServiceError:
        raise

    except Exception as e:
        logger.error(f"Unexpected error in send_booking_confirmation: {str(e)}")
        raise ServiceError(500, f"Failed to send confirmation email: {str(e)}")