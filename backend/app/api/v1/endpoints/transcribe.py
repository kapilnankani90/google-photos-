"""
Server-Side Audio Transcription Endpoint via Groq Speech-to-Text API.

Supports:
- High-fidelity speech transcription for natural personal memories
- Automatic language identification
- Intra-sentence and inter-sentence code-switching (English + Hindi / Hinglish)
- In-memory audio processing without persistent file or database storage
"""

import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel, Field
import httpx

from app.core.config import settings

logger = logging.getLogger("TranscribeEndpoint")

router = APIRouter()

GROQ_TRANSCRIPTION_MODEL = "whisper-large-v3"
GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

GROQ_WHISPER_PROMPT = (
    "Transcribe the spoken audio verbatim in Latin/Roman script. "
    "Preserve English, Hindi, and Hinglish speech exactly as spoken without translation or normalization. "
    "Do not translate Hindi to English. "
    "Examples: ek photo, photo hai jab, thand thi, kar raha tha, gaye the, bohot accha, saath mein."
)

DEVANAGARI_TO_ROMAN_MAP = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
    'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
    'ं': 'n', 'ँ': 'n', '्': '', '़': '', '।': '.', '॥': '.',
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
}


def ensure_roman_script(text: str) -> str:
    """Fallback safety: guarantees any stray Devanagari characters are converted to Roman Hinglish."""
    if not any('\u0900' <= ch <= '\u097f' for ch in text):
        return text
    return "".join(DEVANAGARI_TO_ROMAN_MAP.get(ch, ch) for ch in text)


def _determine_audio_filename(upload_filename: Optional[str], mime_type: str) -> str:
    """
    Selects an appropriate audio filename with extension for Groq Whisper.
    Groq validates audio file extensions (flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, webm).
    """
    if upload_filename and "." in upload_filename:
        ext = upload_filename.rsplit(".", 1)[-1].lower()
        if ext in {"webm", "m4a", "wav", "mp3", "mp4", "mpeg", "mpga", "ogg", "flac"}:
            return upload_filename

    mime_to_ext = {
        "audio/webm": "audio.webm",
        "audio/wav": "audio.wav",
        "audio/x-wav": "audio.wav",
        "audio/wave": "audio.wav",
        "audio/m4a": "audio.m4a",
        "audio/x-m4a": "audio.m4a",
        "audio/mp4": "audio.mp4",
        "audio/mpeg": "audio.mp3",
        "audio/mp3": "audio.mp3",
        "audio/ogg": "audio.ogg",
        "audio/flac": "audio.flac",
        "audio/x-flac": "audio.flac",
    }
    return mime_to_ext.get(mime_type.lower(), "audio.webm")


class TranscriptionResponse(BaseModel):
    """Clean transcription result schema."""
    transcript: str = Field(..., description="Verbatim transcribed speech text")
    model: str = Field(..., description="Underlying transcription model used")


async def transcribe_audio_bytes(
    audio_bytes: bytes,
    mime_type: str = "audio/webm",
    filename: Optional[str] = None,
) -> str:
    """
    Sends raw audio bytes to Groq Speech-to-Text API (whisper-large-v3) for verbatim transcription.
    Never persists audio to disk or database.
    Preserves automatic language identification and seamless Hinglish code-switching.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server transcription service is unconfigured (GROQ_API_KEY missing).",
        )

    audio_filename = _determine_audio_filename(filename, mime_type)
    files = {
        "file": (audio_filename, audio_bytes, mime_type),
    }
    data = {
        "model": GROQ_TRANSCRIPTION_MODEL,
        "temperature": "0.0",
        "response_format": "json",
        "prompt": GROQ_WHISPER_PROMPT,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    last_error_status = 500
    last_error_text = ""

    async with httpx.AsyncClient(timeout=25.0) as client:
        for attempt in range(2):
            try:
                resp = await client.post(
                    GROQ_TRANSCRIPTION_URL,
                    files=files,
                    data=data,
                    headers=headers,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    raw_text = result.get("text", "")
                    transcript = raw_text.strip()
                    if (transcript.startswith('"') and transcript.endswith('"')) or (
                        transcript.startswith("'") and transcript.endswith("'")
                    ):
                        transcript = transcript[1:-1].strip()
                    transcript = ensure_roman_script(transcript)
                    return transcript
                elif resp.status_code in (429, 503):
                    last_error_status = resp.status_code
                    last_error_text = resp.text[:200]
                    logger.warning(
                        "Groq transcription returned %s on attempt %s, sleeping 1.5s",
                        resp.status_code,
                        attempt,
                    )
                    if attempt == 0:
                        await asyncio.sleep(1.5)
                        continue
                    break
                else:
                    last_error_status = resp.status_code
                    last_error_text = resp.text[:200]
                    logger.warning(
                        "Groq transcription returned %s: %s",
                        resp.status_code,
                        last_error_text,
                    )
                    break
            except httpx.TimeoutException:
                logger.warning("Groq transcription request timed out on attempt %s", attempt)
                last_error_status = 504
                last_error_text = "Timeout"
                if attempt == 0:
                    await asyncio.sleep(1.0)
                    continue
                break
            except httpx.RequestError as exc:
                logger.warning("Groq transcription network error: %s", exc)
                last_error_status = 502
                last_error_text = str(exc)
                break
            except Exception as exc:
                logger.warning("Unexpected error during Groq transcription: %s", exc)
                last_error_status = 500
                last_error_text = str(exc)
                break

    if last_error_status == 429:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Transcription provider rate limit reached. Please wait a moment and try again.",
        )
    elif last_error_status == 503:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transcription provider is temporarily unavailable. Please try again shortly.",
        )
    elif last_error_status == 504:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Transcription provider timed out. Please try again.",
        )

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Transcription provider currently busy or unavailable ({last_error_status}). Please try again.",
    )


@router.post("", response_model=TranscriptionResponse)
async def transcribe_endpoint(
    audio: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    mime_type: Optional[str] = Form(None),
) -> TranscriptionResponse:
    """
    Accepts multipart audio upload (WebM, WAV, MP4, etc.), forwards to Groq Speech-to-Text
    (whisper-large-v3) for multilingual transcription, and returns verbatim transcribed text.
    """
    upload = audio or file
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio file provided. Send audio via 'audio' or 'file' multipart field.",
        )

    audio_bytes = await upload.read()
    if not audio_bytes or len(audio_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio recording was empty or too short. Please speak your memory and try again.",
        )

    # Determine mime-type
    resolved_mime = mime_type or upload.content_type or "audio/webm"
    if ";" in resolved_mime:
        # Strip codecs parameter (e.g. 'audio/webm;codecs=opus' -> 'audio/webm')
        resolved_mime = resolved_mime.split(";")[0].strip()

    transcript = await transcribe_audio_bytes(
        audio_bytes,
        mime_type=resolved_mime,
        filename=upload.filename,
    )

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No speech could be recognized in the recording. Please try speaking clearly.",
        )

    return TranscriptionResponse(
        transcript=transcript,
        model=GROQ_TRANSCRIPTION_MODEL,
    )
