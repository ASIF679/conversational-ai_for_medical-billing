# app/schemas/chat.py

from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

# ── Updated Schema — session_id optional from frontend ────────────

class ChatRequest(BaseModel):
    session_id:   Optional[str] = None     # None on first message
    user_message: str                       # always required

    @validator('user_message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatResponse(BaseModel):
    session_id:      str           # frontend stores this and sends back
    response:        str
    conversation_id: Optional[str]    = None
    created_at:      Optional[datetime] = None