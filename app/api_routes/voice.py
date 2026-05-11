import uuid
import json
import logging
import asyncio
from typing import Optional

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends,
)
from fastapi.responses import Response
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from app.db.database import get_db
from app.models.conversationlogs import Conversation
from app.services.stt_service import speech_to_text
from app.services.tts_service import text_to_speech
from app.services.chat_orchestration import run_chat_turn
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["Voice"])

HISTORY_LIMIT = 10


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def _load_history(db: Session, session_id: str) -> list:
    """Load conversation history for session."""
    rows = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    rows = list(reversed(rows))

    messages = []
    for row in rows:
        if row.user_message:
            messages.append(HumanMessage(content=row.user_message))
        if row.ai_response:
            messages.append(AIMessage(content=row.ai_response))

    return messages


def _save_turn(
    db:           Session,
    session_id:   str,
    user_message: str,
    ai_response:  str,
) -> None:
    """Save conversation turn to database."""
    try:
        row = Conversation(
            id           = uuid.uuid4(),
            session_id   = session_id,
            patient_id   = None,
            channel      = "voice",
            user_message = user_message,
            ai_response  = ai_response,
            intent       = None,
        )
        db.add(row)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save conversation: {str(e)}")


# ══════════════════════════════════════════════════════════════════
# HTTP ENDPOINTS (for testing STT and TTS separately)
# ══════════════════════════════════════════════════════════════════

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
):
    """
    TEST ENDPOINT — STT only.
    Send audio file, get text back.
    Use this to test Whisper separately.
    """
    try:
        # Validate file
        if not audio.filename:
            raise HTTPException(400, "No file provided")

        audio_bytes = await audio.read()

        if not audio_bytes:
            raise HTTPException(400, "Empty audio file")

        logger.info(
            f"Transcribe request: "
            f"file={audio.filename} "
            f"size={len(audio_bytes)} bytes"
        )

        transcript = speech_to_text(
            audio_bytes  = audio_bytes,
            content_type = audio.content_type or "audio/wav",
        )

        return {
            "success":    True,
            "transcript": transcript
        }

    except ServiceError as e:
        raise HTTPException(status_code=e.code, detail=e.message)

    except Exception as e:
        logger.error(f"Transcribe error: {str(e)}")
        raise HTTPException(500, "Transcription failed. Please try again.")


@router.post("/speak")
async def speak_text(text: str = Form(...)):
    """
    TEST ENDPOINT — TTS only.
    Send text, get audio back.
    Use this to test Edge TTS separately.
    """
    try:
        if not text or not text.strip():
            raise HTTPException(400, "Text cannot be empty")

        logger.info(f"Speak request: {text[:50]}")

        audio_bytes = await text_to_speech(text)

        return Response(
            content      = audio_bytes,
            media_type   = "audio/mpeg",
            headers      = {
                "Content-Disposition": "inline; filename=response.mp3"
            }
        )

    except RuntimeError as e:
        raise HTTPException(500, str(e))

    except Exception as e:
        logger.error(f"Speak error: {str(e)}")
        raise HTTPException(500, "Text to speech failed. Please try again.")


@router.post("/chat-audio")
async def voice_chat_http(
    audio:      UploadFile = File(...),
    session_id: str        = Form(default=""),
    db:         Session    = Depends(get_db),
):
    """
    HTTP VOICE CHAT — full loop.
    Send audio → get audio back.
    Push to talk approach.
    Good for testing before WebSocket.
    """
    try:
        # ── Session ───────────────────────────────────────────────
        sid = session_id.strip() or str(uuid.uuid4())

        # ── Read Audio ────────────────────────────────────────────
        audio_bytes = await audio.read()

        if not audio_bytes:
            raise HTTPException(400, "No audio received")

        logger.info(
            f"Voice HTTP chat | session={sid} | "
            f"audio={len(audio_bytes)} bytes"
        )

        # ── STT ───────────────────────────────────────────────────
        try:
            transcript = speech_to_text(
                audio_bytes  = audio_bytes,
                content_type = audio.content_type or "audio/wav",
            )
        except ServiceError as e:
            raise HTTPException(status_code=e.code, detail=e.message)

        logger.info(f"Transcript: {transcript}")

        # ── Agent ─────────────────────────────────────────────────
        history = _load_history(db, sid)

        try:
            reply = run_chat_turn(
                user_message = transcript,
                chat_history = history,
            )
        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            reply = "I'm sorry, I had trouble processing that. Could you please repeat?"

        logger.info(f"Agent reply: {reply[:100]}")

        # ── Save To DB ────────────────────────────────────────────
        _save_turn(db, sid, transcript, reply)

        # ── TTS ───────────────────────────────────────────────────
        try:
            audio_response = await text_to_speech(reply)
        except RuntimeError as e:
            logger.error(f"TTS error: {str(e)}")
            raise HTTPException(500, "Failed to generate audio response")

        # ── Return Audio + Metadata In Headers ────────────────────
        return Response(
            content    = audio_response,
            media_type = "audio/mpeg",
            headers    = {
                "X-Session-Id":  sid,
                "X-Transcript":  transcript,
                "X-Reply-Text":  reply[:200],
                "Content-Disposition": "inline; filename=response.mp3"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Voice HTTP chat error: {str(e)}")
        raise HTTPException(500, "Voice chat failed. Please try again.")


# ══════════════════════════════════════════════════════════════════
# WEBSOCKET ENDPOINT — Real Time Voice
# ══════════════════════════════════════════════════════════════════

class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        self.active[session_id] = ws
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        self.active.pop(session_id, None)
        logger.info(f"WebSocket disconnected: {session_id}")

    async def send_json(self, session_id: str, data: dict):
        ws = self.active.get(session_id)
        if ws:
            await ws.send_json(data)

    async def send_audio(self, session_id: str, audio: bytes):
        ws = self.active.get(session_id)
        if ws:
            await ws.send_bytes(audio)


manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def voice_websocket(
    websocket:  WebSocket,
    session_id: str,
):
    """
    WebSocket Voice Chat — Real Time.

    Protocol:
      Client sends JSON:  {"type": "start"}           → call started
      Client sends bytes: <audio data>                 → patient spoke
      Client sends JSON:  {"type": "end"}              → call ended

      Server sends JSON:  {"type": "transcript", "text": "..."} → what patient said
      Server sends JSON:  {"type": "reply", "text": "..."}      → agent reply text
      Server sends bytes: <audio data>                           → agent voice
      Server sends JSON:  {"type": "error", "message": "..."}   → error occurred
      Server sends JSON:  {"type": "ready"}                      → ready for next input
    """

    await manager.connect(session_id, websocket)

    # Get DB session
    db = next(get_db())

    try:
        # ── Send Welcome Message ──────────────────────────────────
        history = _load_history(db, session_id)

        if not history:
            # New session — greet patient
            welcome = (
                "Hello! Welcome to MedCare Clinic. "
                "How can I help you today?"
            )
            welcome_audio = await text_to_speech(welcome)

            await manager.send_json(session_id, {
                "type": "reply",
                "text": welcome
            })
            await manager.send_audio(session_id, welcome_audio)
            _save_turn(db, session_id, "", welcome)

        await manager.send_json(session_id, {"type": "ready"})

        # ── Main Message Loop ─────────────────────────────────────
        while True:
            try:
                # Receive message from client
                message = await websocket.receive()

                # ── JSON Control Message ──────────────────────────
                if "text" in message:
                    data = json.loads(message["text"])
                    msg_type = data.get("type", "")

                    if msg_type == "end":
                        logger.info(f"Session ended: {session_id}")
                        break

                    elif msg_type == "ping":
                        await manager.send_json(session_id, {"type": "pong"})

                # ── Audio Data ────────────────────────────────────
                elif "bytes" in message:
                    audio_bytes = message["bytes"]

                    if not audio_bytes or len(audio_bytes) < 1000:
                        await manager.send_json(session_id, {
                            "type":    "error",
                            "message": "Audio too short. Please speak longer."
                        })
                        await manager.send_json(session_id, {"type": "ready"})
                        continue

                    logger.info(
                        f"WS audio received: "
                        f"session={session_id} "
                        f"size={len(audio_bytes)} bytes"
                    )

                    # ── STT ───────────────────────────────────────
                    try:
                        transcript = speech_to_text(
                            audio_bytes  = audio_bytes,
                            content_type = "audio/webm",
                        )
                    except ServiceError as e:
                        logger.warning(f"STT error: {e.message}")
                        await manager.send_json(session_id, {
                            "type":    "error",
                            "message": e.message
                        })
                        await manager.send_json(session_id, {"type": "ready"})
                        continue

                    # Send transcript to client
                    await manager.send_json(session_id, {
                        "type": "transcript",
                        "text": transcript
                    })

                    logger.info(f"WS transcript: {transcript}")

                    # ── Agent ─────────────────────────────────────
                    history = _load_history(db, session_id)

                    try:
                        reply = run_chat_turn(
                            user_message = transcript,
                            chat_history = history,
                        )
                    except Exception as e:
                        logger.error(f"Agent error: {str(e)}")
                        reply = (
                            "I'm sorry, I had trouble with that. "
                            "Could you please repeat?"
                        )

                    # Send reply text to client
                    await manager.send_json(session_id, {
                        "type": "reply",
                        "text": reply
                    })

                    logger.info(f"WS reply: {reply[:100]}")

                    # ── Save To DB ────────────────────────────────
                    _save_turn(db, session_id, transcript, reply)

                    # ── TTS ───────────────────────────────────────
                    try:
                        audio_response = await text_to_speech(reply)
                        await manager.send_audio(session_id, audio_response)
                    except RuntimeError as e:
                        logger.error(f"TTS error: {str(e)}")
                        await manager.send_json(session_id, {
                            "type":    "error",
                            "message": "Could not generate audio response."
                        })

                    # Signal ready for next input
                    await manager.send_json(session_id, {"type": "ready"})

            except WebSocketDisconnect:
                logger.info(f"WS client disconnected: {session_id}")
                break

            except Exception as e:
                logger.error(f"WS loop error: {str(e)}")
                try:
                    await manager.send_json(session_id, {
                        "type":    "error",
                        "message": "Something went wrong. Please try again."
                    })
                    await manager.send_json(session_id, {"type": "ready"})
                except Exception:
                    break

    except WebSocketDisconnect:
        logger.info(f"WS disconnected on connect: {session_id}")

    except Exception as e:
        logger.error(f"WS fatal error: {str(e)}")
        try:
            await manager.send_json(session_id, {
                "type":    "error",
                "message": "Connection error. Please refresh and try again."
            })
        except Exception:
            pass

    finally:
        manager.disconnect(session_id)
        db.close()
        logger.info(f"WS session cleaned up: {session_id}")