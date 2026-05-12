import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROOT_ENV = PROJECT_ROOT / ".env"
MIGRATIONS_ENV = PROJECT_ROOT / "migrations" / ".env"

if ROOT_ENV.exists():
    load_dotenv(dotenv_path=ROOT_ENV)
elif MIGRATIONS_ENV.exists():
    load_dotenv(dotenv_path=MIGRATIONS_ENV)
else:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Groq (Llama) — supports GROQ_API_KEY or API_KEY in .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
MODEL_NAME_FROM_GEMINI=os.getenv("MODEL_NAME_FROM_GEMINI","gemini-2.0-flash")

# Email (SMTP)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
APPOINTMENT_LOCATION_NAME = os.getenv("APPOINTMENT_LOCATION_NAME", "Main Hospital")


