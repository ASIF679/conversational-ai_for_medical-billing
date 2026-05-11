import io
import logging
import asyncio
import edge_tts
logger = logging.getLogger(__name__)

VOICE = "en-US-AvaMultilingualNeural"


async def text_to_speech(text: str) -> bytes:

    # ── Validate Raw Input ────────────────────────────────────────
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    # ── Clean Markdown Symbols ────────────────────────────────────
    clean_text = (
        text
        .replace("*", "")
        .replace("#", "")
        .replace("•", "")
        .replace("→", "")
        .replace("✅", "")
        .replace("❌", "")
        .replace("─", "")
        .replace("`", "")
        .replace("_", " ")
        .strip()
    )

    # ── Validate After Cleaning ───────────────────────────────────
    # This is the bug fix
    # If LLM reply was mostly markdown symbols
    # clean_text becomes "" and edge-tts returns 0 bytes silently
    if not clean_text:
        logger.error(
            f"Text became empty after cleaning. "
            f"Original: '{text[:100]}'"
        )
        raise ValueError(
            "Text became empty after removing markdown symbols. "
            "Nothing to convert to speech."
        )

    logger.info(
        f"TTS converting {len(clean_text)} chars | "
        f"voice={VOICE} | "
        f"preview='{clean_text[:50]}'"
    )

    try:
        audio_buffer = io.BytesIO()
        communicate  = edge_tts.Communicate(clean_text, VOICE)

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        audio_bytes = audio_buffer.getvalue()

        # ── Validate Output ───────────────────────────────────────
        if not audio_bytes:
            logger.error(
                f"Edge TTS returned 0 bytes for text: "
                f"'{clean_text[:100]}'"
            )
            raise RuntimeError(
                "Edge TTS returned empty audio. "
                "Check your internet connection."
            )

        logger.info(f"TTS generated {len(audio_bytes)} bytes")
        return audio_bytes

    except edge_tts.exceptions.NoAudioReceived:
        logger.error(f"Edge TTS NoAudioReceived for: '{clean_text[:50]}'")
        raise RuntimeError(
            "No audio received from Edge TTS. "
            "Check your internet connection."
        )

    except RuntimeError:
        raise

    except Exception as e:
        logger.error(f"TTS unexpected error: {str(e)}")
        raise RuntimeError(f"Text to speech failed: {str(e)}")


def text_to_speech_sync(text: str) -> bytes:
    """Synchronous wrapper for use in non-async contexts."""
    return asyncio.run(text_to_speech(text))