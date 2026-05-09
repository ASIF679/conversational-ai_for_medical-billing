# Conversational AI for Medical Billing

An Automated Multi-Agent Conversational AI System for Medical Billing and Customer Support.

This project is designed to automate healthcare customer support operations including:

- Patient interaction handling
- Appointment booking
- Medical billing workflow automation
- AI-powered conversational support
- Automated email notifications
- Multi-agent orchestration for healthcare operations

The system is built using FastAPI, LangChain, PostgreSQL, SQLAlchemy, and Groq LLMs.

---

# Features

- AI-powered conversational medical support
- Multi-agent workflow architecture
- Appointment scheduling support
- Automated email sending
- REST API with FastAPI
- Database migrations using Alembic
- PostgreSQL integration
- Modular and scalable backend structure

---

# Tech Stack

## Core Backend
- FastAPI
- Uvicorn

## Database
- PostgreSQL
- SQLAlchemy
- Alembic

## AI Stack
- LangChain
- LangChain Community
- LangChain Groq
- Groq LLM API

## Utilities
- Pydantic
- APScheduler
- HTTPX
- Python Dotenv

---

# Project Structure

```bash
conversational-ai-for-medical-billing/
├── app/
│   ├── api_routes/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── tools/
│   └── main.py
├── migrations/
│   └── versions/
├── venv/
├── requirements.txt
├── alembic.ini
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/your-username/conversational-ai-for-medical-billing.git
```

```bash
cd conversational-ai-for-medical-billing
```

---

# Create Virtual Environment

## Windows

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```

## Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the root directory.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost/dbname

GROQ_API_KEY=your_groq_api_key

SMTP_EMAIL=your_email
SMTP_PASSWORD=your_password
```

---

# Apply Database Migrations

```bash
alembic upgrade head
```

---

# Run Application

```bash
uvicorn app.main:app --reload
```

---

# API Documentation

After running the server:

Swagger Docs:

```bash
http://127.0.0.1:8000/docs
```

ReDoc:

```bash
http://127.0.0.1:8000/redoc
```

---

# Requirements

```txt
# Core Backend
fastapi==0.110.0
uvicorn[standard]==0.29.0

# Database
sqlalchemy==2.0.29
psycopg2-binary==2.9.9

# Config & Validation
pydantic==2.6.4
python-dotenv==1.0.1
email-validator==2.1.1

# AI Stack
langchain==0.1.16
langchain-community==0.0.32
langchain-groq==0.1.3
langchain-core==0.1.53
groq==0.37.1
langchain-text-splitters==0.0.2

# HTTP / Utils
httpx==0.27.0

# Scheduler
apscheduler==3.10.4

# Database Migration
alembic==1.13.1
```

---

# Future Improvements

- Voice AI Integration
- Real-time Call Handling
- RAG-based Medical Knowledge Retrieval
- Multi-language Support
- Insurance Claim Automation
- Dashboard & Analytics
- HIPAA-compliant deployment

---

# License

This project is licensed under the MIT License.

---

# Author

Asif Nawaz  
AI & Machine Learning Engineer