# app/api_routes/chat.py

import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.conversationlogs import Conversation
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_orchestration import run_chat_turn

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

HISTORY_LIMIT = 10


# ── Load History ──────────────────────────────────────────────────
def _load_history(db: Session, session_id: str) -> list:
    rows = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())   # ✅ newest first
        .limit(HISTORY_LIMIT)
        .all()
    )
    rows = list(reversed(rows))                     # ✅ chronological order

    messages = []
    for row in rows:
        if row.user_message:
            messages.append(HumanMessage(content=row.user_message))
        if row.ai_response:
            messages.append(AIMessage(content=row.ai_response))

    logger.info(f"Loaded {len(messages)} messages for session: {session_id}")
    return messages


# ── Save Turn ─────────────────────────────────────────────────────
def _save_turn(
    db:           Session,
    session_id:   str,
    user_message: str,
    ai_response:  str,
) -> Conversation:
    row = Conversation(
        id           = uuid.uuid4(),
        session_id   = session_id,
        patient_id   = None,
        channel      = "web",
        user_message = user_message,
        ai_response  = ai_response,
        intent       = None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ── Chat Endpoint ─────────────────────────────────────────────────
@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db:      Session = Depends(get_db)
) -> ChatResponse:

    # First message → new session_id
    # Next messages → use session_id from previous response
    session_id = request.session_id or str(uuid.uuid4())

    logger.info(
        f"Chat | session={session_id} | "
        f"new={not bool(request.session_id)} | "
        f"message={request.user_message[:50]}"
    )

    history = _load_history(db, session_id)

    try:
        reply = run_chat_turn(
            user_message = request.user_message,
            chat_history = history,
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code = 500,
            detail      = "Chat service error. Please try again."
        )

    try:
        row = _save_turn(
            db           = db,
            session_id   = session_id,
            user_message = request.user_message,
            ai_response  = reply,
        )
        return ChatResponse(
            session_id      = session_id,
            response        = reply,
            conversation_id = str(row.id),
            created_at      = row.created_at,
        )

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB save failed: {str(e)}")
        # Still return reply to patient even if DB fails
        return ChatResponse(
            session_id = session_id,
            response   = reply,
        )