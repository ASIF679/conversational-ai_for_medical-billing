import os
import uuid
import logging
import tempfile
from groq import Groq
from app.core.config import GROQ_API_KEY
from app.services.errors import ServiceError

logger = logging.getLogger(__name__)

# Whisper model
WHISPER_MODEL = "whisper-large-v3-turbo"

# Supported audio formats
SUPPORTED_FORMATS = {
    "audio/wav":  ".wav",
    "audio/webm": ".webm",
    "audio/mp3":  ".mp3",
    "audio/mpeg": ".mp3",
    "audio/ogg":  ".ogg",
    "audio/m4a":  ".m4a",
}


def speech_to_text(
    audio_bytes: bytes,
    content_type: str = "audio/wav",
    language: str = "en"
) -> str:
    # ── Validate Input ────────────────────────────────────────────
    if not audio_bytes:
        raise ServiceError(400, "No audio data received")

    if len(audio_bytes) < 1000:
        raise ServiceError(400, "Audio too short. Please speak longer.")

    if not GROQ_API_KEY:
        raise ServiceError(500, "Groq API key not configured")

    # ── Get File Extension ────────────────────────────────────────
    extension = SUPPORTED_FORMATS.get(content_type, ".wav")
    logger.info(
        f"STT processing {len(audio_bytes)} bytes "
        f"type={content_type} model={WHISPER_MODEL}"
    )

    # ── Save To Temp File ─────────────────────────────────────────
    temp_path = None
    try:
        # Create temp file with correct extension
        temp_fd, temp_path = tempfile.mkstemp(suffix=extension)
        os.close(temp_fd)

        with open(temp_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"Temp audio saved: {temp_path}")

        # ── Send To Groq Whisper ──────────────────────────────────
        client = Groq(api_key=GROQ_API_KEY)

        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model    = WHISPER_MODEL,
                file     = audio_file,
                language = language,
            )

        transcript = transcription.text.strip()

        if not transcript:
            raise ServiceError(400, "Could not understand audio. Please speak clearly.")

        logger.info(f"STT transcript: {transcript}")
        return transcript

    except ServiceError:
        raise

    except Exception as e:
        error_str = str(e).lower()
        logger.error(f"STT error: {str(e)}")

        if "invalid file" in error_str or "format" in error_str:
            raise ServiceError(
                400,
                "Audio format not supported. Please try again."
            )
        if "rate limit" in error_str:
            raise ServiceError(
                429,
                "Too many requests. Please wait a moment."
            )
        if "api key" in error_str or "auth" in error_str:
            raise ServiceError(
                401,
                "STT service authentication failed."
            )
        raise ServiceError(500, f"Speech recognition failed: {str(e)}")

    finally:
        # ── Always Delete Temp File ───────────────────────────────
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.info(f"Temp file deleted: {temp_path}")
            except Exception as e:
                logger.warning(f"Could not delete temp file: {str(e)}")