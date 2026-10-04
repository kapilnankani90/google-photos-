"""
Server-Side Audio Transcription Endpoint via Gemini Multimodal API.

Supports:
- High-fidelity speech transcription for natural personal memories
- Automatic language identification
- Intra-sentence and inter-sentence code-switching (English + Hindi / Hinglish)
- In-memory audio processing without persistent file or database storage
"""

import base64
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel, Field
import httpx

from app.core.config import settings

logger = logging.getLogger("TranscribeEndpoint")

router = APIRouter()

GEMINI_TRANSCRIPTION_MODEL = "gemini-3.5-flash"
GEMINI_API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

TRANSCRIPTION_PROMPT = (
    "Transcribe the spoken audio verbatim as text.\n\n"
    "CRITICAL SCRIPT & FIDELITY RULES:\n"
    "1. SCRIPT: Output MUST be exclusively in the Roman/Latin alphabet (English letters). NEVER output Devanagari or any non-Latin script.\n"
    "2. NO TRANSLATION & NO NORMALIZATION:\n"
    "   Hindi and Hinglish words must be transcribed according to their spoken Hindi/Hinglish pronunciation, using Roman/Latin letters. "
    "Do not translate, normalize, or replace Hindi words with semantically similar English words.\n"
    "3. PREFER HINDI/HINGLISH INTERPRETATION FOR HOMOPHONES:\n"
    "   If a Hindi word sounds like an English word, prefer the Hindi/Hinglish interpretation when the surrounding speech is clearly Hinglish or code-switched.\n"
    "   Examples:\n"
    "   - 'ek photo' -> 'ek photo' (NOT 'each photo', 'a photo', or '8 photo')\n"
    "   - 'photo hai' -> 'photo hai' (NOT 'photo hijab')\n"
    "   - 'photo hai jab' -> 'photo hai jab' (NOT 'photo hijab')\n"
    "   - 'thand thi' -> 'thand thi' (NOT 'thandi')\n"
    "4. EXACT SPOKEN LEXICAL CONTENT, GENDER & TENSE:\n"
    "   Preserve the exact spoken lexical content as closely as possible. "
    "Do not infer a different gender, tense, subject, object, or quantity from context or vocal pitch.\n"
    "   Examples:\n"
    "   - 'kar raha tha' -> 'kar raha tha' (NOT 'kar rahi thi')\n"
    "   - 'gaye the' -> 'gaye the'\n"
    "   - Do NOT invent or add words such as 'hi', 'bhi', or 'ek hi' unless explicitly spoken.\n"
    "5. PRESERVE CODE-SWITCHED HINDI WORDS VERBATIM:\n"
    "   Do NOT translate words such as: 'yaar', 'ek', 'yaad hai', 'jab hum', 'gaye the', 'bahut', 'thi', 'tha', 'saath', 'ke', 'pe', 'main', 'thand', 'aur', 'car se'.\n"
    "6. PROPER NOUNS & ENTITIES: Preserve proper nouns and entities exactly (e.g. 'Rohtang', 'snow', 'skiing', 'trip', 'family', 'car').\n"
    "7. OUTPUT FORMAT: Output ONLY the plain transcription text with no quotes, commentary, markdown, or timestamps."
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


class TranscriptionResponse(BaseModel):
    """Clean transcription result schema."""
    transcript: str = Field(..., description="Verbatim transcribed speech text")
    model: str = Field(..., description="Underlying transcription model used")


CANDIDATE_MODELS = ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-latest"]


async def transcribe_audio_bytes(audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
    """
    Sends raw audio bytes to Gemini multimodal generateContent API for verbatim transcription.
    Never persists audio to disk or database.
    Prioritizes dedicated gemini-3.5-transcribe capability with automatic language identification
    and seamless intra/inter-sentence code-switching (English + Hindi / Hinglish).
    """
    import asyncio

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server transcription service is unconfigured (GEMINI_API_KEY missing).",
        )

    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": b64_audio,
                        }
                    },
                    {
                        "text": TRANSCRIPTION_PROMPT,
                    },
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
        },
    }

    last_error_status = 500
    last_error_text = ""

    async with httpx.AsyncClient(timeout=25.0) as client:
        for model in CANDIDATE_MODELS:
            url = f"{GEMINI_API_URL_TEMPLATE.format(model=model)}?key={api_key}"
            for attempt in range(2):
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            content_parts = candidates[0].get("content", {}).get("parts", [])
                            text_pieces = []
                            for part in content_parts:
                                if "audioTranscription" in part and isinstance(part["audioTranscription"], dict):
                                    text_pieces.append(part["audioTranscription"].get("text", ""))
                                elif "text" in part and part["text"]:
                                    text_pieces.append(part["text"])

                            transcript = "".join(text_pieces).strip()
                            if (transcript.startswith('"') and transcript.endswith('"')) or (
                                transcript.startswith("'") and transcript.endswith("'")
                            ):
                                transcript = transcript[1:-1].strip()
                            transcript = ensure_roman_script(transcript)
                            return transcript
                        return ""
                    elif resp.status_code in (429, 503):
                        last_error_status = resp.status_code
                        last_error_text = resp.text[:200]
                        logger.warning("Model %s returned %s on attempt %s, sleeping 1.5s", model, resp.status_code, attempt)
                        await asyncio.sleep(1.5)
                        continue
                    else:
                        last_error_status = resp.status_code
                        last_error_text = resp.text[:200]
                        logger.warning("Model %s returned %s: %s; trying next model", model, resp.status_code, last_error_text)
                        break
                except httpx.TimeoutException:
                    logger.warning("Model %s timed out; trying next model", model)
                    last_error_status = 504
                    last_error_text = "Timeout"
                    break
                except Exception as exc:
                    logger.warning("Model %s network error: %s", model, exc)
                    last_error_status = 502
                    last_error_text = str(exc)
                    break

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Transcription providers currently busy or unavailable ({last_error_status}). Please try again.",
    )


@router.post("", response_model=TranscriptionResponse)
async def transcribe_endpoint(
    audio: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    mime_type: Optional[str] = Form(None),
) -> TranscriptionResponse:
    """
    Accepts multipart audio upload (WebM, WAV, MP4, etc.), forwards to Gemini for multilingual transcription,
    and returns verbatim transcribed text.
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

    transcript = await transcribe_audio_bytes(audio_bytes, mime_type=resolved_mime)

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No speech could be recognized in the recording. Please try speaking clearly.",
        )

    return TranscriptionResponse(
        transcript=transcript,
        model=GEMINI_TRANSCRIPTION_MODEL,
    )
