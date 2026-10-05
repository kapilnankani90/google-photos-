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
import re
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

# ---------------------------------------------------------------------------
# Script Normalization & Transliteration Layer (Devanagari + Arabic/Urdu -> Roman)
# ---------------------------------------------------------------------------

URDU_TO_ROMAN_WORD_MAP = {
    # English loanwords frequently used in memories
    'فیملی': 'family',
    'ٹرپ': 'trip',
    'بیچ': 'beach',
    'سنسٹ': 'sunset',
    'ٹائم': 'time',
    'فوٹو': 'photo',
    'فوٹوز': 'photos',
    'تصویر': 'tasveer',
    'تصویریں': 'tasveerein',
    'تصویروں': 'tasveeron',
    'کار': 'car',
    'سنو': 'snow',
    'سکینگ': 'skiing',
    'اسکینگ': 'skiing',
    'برتھڈے': 'birthday',
    'برتھ ڈے': 'birthday',
    'پارٹی': 'party',
    'کیک': 'cake',
    'ہوٹل': 'hotel',
    'ریسٹورنٹ': 'restaurant',
    'کیفے': 'cafe',
    'روڈ': 'road',
    'فلائٹ': 'flight',
    'پلین': 'plane',
    'ائیرپورٹ': 'airport',
    'ایئرپورٹ': 'airport',
    'ٹرین': 'train',
    'سٹیشن': 'station',
    'اسٹیشن': 'station',
    'پارک': 'park',
    'گارڈن': 'garden',
    'پکنک': 'picnic',
    'کیمپس': 'campus',
    'کالج': 'college',
    'سکول': 'school',
    'آفس': 'office',
    'مندر': 'mandir',
    'ٹیمپل': 'temple',
    'چرچ': 'church',
    'مسجد': 'masjid',
    'ڈنر': 'dinner',
    'لنچ': 'lunch',
    'بریکفاسٹ': 'breakfast',
    'بریک فاسٹ': 'breakfast',
    'کافی': 'coffee',
    'چائے': 'chai',
    'سلفی': 'selfie',
    'سیلفی': 'selfie',
    'ویڈیو': 'video',
    'کیمرہ': 'camera',
    'موبائل': 'mobile',
    'فون': 'phone',
    'فرینڈز': 'friends',
    'فرینڈ': 'friend',
    'دوست': 'friends',
    'دوستوں': 'doston',
    'ریڈ': 'red',
    'بلیو': 'blue',
    'گرین': 'green',
    'ییلو': 'yellow',
    'وائٹ': 'white',
    'بلیک': 'black',
    'پنک': 'pink',
    'ڈاگ': 'dog',
    'کیٹ': 'cat',
    'ڈریس': 'dress',
    'شرٹ': 'shirt',
    # Places
    'گوا': 'Goa',
    'منالی': 'Manali',
    'شملہ': 'Shimla',
    'کشمیر': 'Kashmir',
    'دہلی': 'Delhi',
    'ممبئی': 'Mumbai',
    'جے پور': 'Jaipur',
    'روہتانگ': 'Rohtang',
    'روہتنگ': 'Rohtang',
    'لداخ': 'Ladakh',
    # Common Hindi / Urdu / Hinglish lexical vocabulary
    'مجھے': 'mujhe',
    'مجھ': 'mujh',
    'یاد': 'yaad',
    'ہے': 'hai',
    'ہیں': 'hain',
    'ہوں': 'hoon',
    'ہو': 'ho',
    'ایک': 'ek',
    'تھا': 'tha',
    'تھی': 'thi',
    'تھے': 'the',
    'تھیں': 'theen',
    'ہم': 'hum',
    'ہمیں': 'humein',
    'ہمارا': 'hamara',
    'ہماری': 'hamari',
    'ہمارے': 'hamare',
    'پر': 'par',
    'پہ': 'pe',
    'پے': 'pe',
    'کے': 'ke',
    'کی': 'ki',
    'کا': 'ka',
    'کو': 'ko',
    'سے': 'se',
    'میں': 'mein',
    'ساتھ': 'saath',
    'اور': 'aur',
    'یا': 'ya',
    'لیکن': 'lekin',
    'بہت': 'bahut',
    'زیادہ': 'zyada',
    'اچھا': 'achha',
    'اچھی': 'achhi',
    'اچھے': 'achhe',
    'بڑا': 'bada',
    'بڑی': 'badi',
    'بڑے': 'bade',
    'چھوٹا': 'chhota',
    'چھوٹی': 'chhoti',
    'چھوٹے': 'chhote',
    'یار': 'yaar',
    'بھائی': 'bhai',
    'بہن': 'behan',
    'ممی': 'mummy',
    'امی': 'ammi',
    'پاپا': 'papa',
    'ابو': 'abbu',
    'بچے': 'bachhe',
    'بچہ': 'bachha',
    'لوگ': 'log',
    'لوگوں': 'logon',
    'سب': 'sab',
    'سارے': 'saare',
    'ساری': 'saari',
    'سارا': 'saara',
    'یہ': 'yeh',
    'وہ': 'woh',
    'اس': 'is',
    'ان': 'un',
    'اسکا': 'uska',
    'اسکی': 'uski',
    'اسکے': 'uske',
    'انکا': 'unka',
    'انکی': 'unki',
    'انکے': 'unke',
    'اپنا': 'apna',
    'अपनी': 'apni',
    'اپنی': 'apni',
    'اپنے': 'apne',
    'میرا': 'mera',
    'میری': 'meri',
    'میرے': 'mere',
    'تیرا': 'tera',
    'تیری': 'teri',
    'تیرے': 'tere',
    'آپ': 'aap',
    'آپکا': 'aapka',
    'آپکی': 'aapki',
    'آپکے': 'aapke',
    'جب': 'jab',
    'تب': 'tab',
    'کب': 'kab',
    'کہاں': 'kahan',
    'یہاں': 'yahan',
    'وہاں': 'wahan',
    'کچھ': 'kuch',
    'کوئی': 'koi',
    'کیا': 'kya',
    'کیوں': 'kyun',
    'کون': 'kaun',
    'کیسے': 'kaise',
    'کتنا': 'kitna',
    'کر': 'kar',
    'کرنا': 'karna',
    'کرتے': 'karte',
    'کرتی': 'karti',
    'کرتا': 'karta',
    'رہا': 'raha',
    'رہی': 'rahi',
    'رہے': 'rahe',
    'گیا': 'gaya',
    'گئی': 'gayi',
    'گئے': 'gaye',
    'گۓ': 'gaye',
    'آیا': 'aaya',
    'آئی': 'aayi',
    'آئے': 'aaye',
    'آۓ': 'aaye',
    'دیکھا': 'dekha',
    'دیکھی': 'dekhi',
    'دیکھے': 'dekhe',
    'ٹھنڈ': 'thand',
    'سردی': 'sardi',
    'گرمی': 'garmi',
    'بارش': 'barish',
    'صبح': 'subah',
    'شام': 'shaam',
    'رات': 'raat',
    'دن': 'din',
    'بھی': 'bhi',
    'ہی': 'hi',
    'صرف': 'sirf',
    'پہلے': 'pehle',
    'بعد': 'baad',
    'پاس': 'paas',
    'دور': 'door',
    'اندر': 'andar',
    'باہر': 'bahar',
    'اوپر': 'upar',
    'نیچے': 'neeche',
    'پہاڑ': 'pahad',
    'پہاڑوں': 'pahadon',
    'سمندر': 'samundar',
    'دریا': 'darya',
    'ندی': 'nadi',
    'پانی': 'pani',
    'کھانا': 'khana',
    'برف': 'barf',
    'شاید': 'shayad',
    'لگتا': 'lagta',
    'سال': 'saal',
}

DEVANAGARI_TO_ROMAN_WORD_MAP = {
    # English loanwords
    'फैमिली': 'family',
    'ट्रिप': 'trip',
    'बीच': 'beach',
    'सनसेट': 'sunset',
    'टाइम': 'time',
    'फोटो': 'photo',
    'फ़ोटो': 'photo',
    'फोटोज़': 'photos',
    'फ़ोटोज़': 'photos',
    'कार': 'car',
    'स्नो': 'snow',
    'स्कीइंग': 'skiing',
    'पार्टी': 'party',
    'होटल': 'hotel',
    'फ्रेंड्स': 'friends',
    'फ्रेंड': 'friend',
    'बर्थडे': 'birthday',
    'रोहतांग': 'Rohtang',
    'मनाली': 'Manali',
    'गोवा': 'Goa',
    'दिल्ली': 'Delhi',
    'मुंबई': 'Mumbai',
    # Common Hinglish words
    'मुझे': 'mujhe',
    'याद': 'yaad',
    'है': 'hai',
    'हैं': 'hain',
    'एक': 'ek',
    'था': 'tha',
    'थी': 'thi',
    'थे': 'the',
    'हम': 'hum',
    'पर': 'par',
    'पे': 'pe',
    'के': 'ke',
    'का': 'ka',
    'की': 'ki',
    'को': 'ko',
    'से': 'se',
    'में': 'mein',
    'साथ': 'saath',
    'और': 'aur',
    'बहुत': 'bahut',
    'अच्छा': 'achha',
    'अच्छी': 'achhi',
    'अच्छे': 'achhe',
    'ठंड': 'thand',
    'गर्मी': 'garmi',
    'बारिश': 'barish',
}

URDU_DIGRAPHS = [
    ('بھ', 'bh'), ('پھ', 'ph'), ('تھ', 'th'), ('ٹھ', 'th'),
    ('جھ', 'jh'), ('چھ', 'chh'), ('دھ', 'dh'), ('ڈھ', 'dh'),
    ('کھ', 'kh'), ('گھ', 'gh'), ('ڑھ', 'rh'), ('ئے', 'e'),
]

URDU_CHAR_MAP = {
    'ا': 'a', 'آ': 'aa', 'أ': 'a', 'إ': 'i', 'ء': '',
    'ب': 'b', 'پ': 'p', 'ت': 't', 'ٹ': 't', 'ث': 's',
    'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh',
    'د': 'd', 'ڈ': 'd', 'ذ': 'z', 'ر': 'r', 'ڑ': 'r', 'ز': 'z', 'ژ': 'zh',
    'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'z', 'ط': 't', 'ظ': 'z',
    'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q', 'ک': 'k', 'گ': 'g',
    'ل': 'l', 'م': 'm', 'ن': 'n', 'ں': 'n', 'و': 'o', 'ؤ': 'o',
    'ہ': 'h', 'ۂ': 'h', 'ۃ': 't', 'ھ': 'h',
    'ی': 'i', 'ئ': 'e', 'ے': 'e',
    '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
}

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

ARABIC_PUNCTUATION_MAP = {
    '۔': '.', '،': ',', '؟': '?', '؛': ';', '٪': '%',
}

ARABIC_DIACRITICS = set('\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0670')

ARABIC_WORD_REGEX = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+')
DEVANAGARI_WORD_REGEX = re.compile(r'[\u0900-\u097F]+')

NON_LATIN_SCRIPT_CHECK = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u0900-\u097F]')


def _transliterate_urdu_chars(word: str) -> str:
    """Character/digraph fallback transliterator for Urdu/Arabic tokens."""
    res = word
    for dg, repl in URDU_DIGRAPHS:
        res = res.replace(dg, repl)
    out = []
    for ch in res:
        if ch in ARABIC_DIACRITICS:
            continue
        out.append(URDU_CHAR_MAP.get(ch, ''))
    return ''.join(out)


def _transliterate_urdu_word(word: str) -> str:
    """Transliterates a single Arabic/Urdu word to Roman script."""
    if word in URDU_TO_ROMAN_WORD_MAP:
        return URDU_TO_ROMAN_WORD_MAP[word]
    clean_word = ''.join(c for c in word if c not in ARABIC_DIACRITICS)
    if clean_word in URDU_TO_ROMAN_WORD_MAP:
        return URDU_TO_ROMAN_WORD_MAP[clean_word]
    return _transliterate_urdu_chars(clean_word)


def _transliterate_devanagari_word(word: str) -> str:
    """Transliterates a single Devanagari word to Roman script."""
    if word in DEVANAGARI_TO_ROMAN_WORD_MAP:
        return DEVANAGARI_TO_ROMAN_WORD_MAP[word]
    return ''.join(DEVANAGARI_TO_ROMAN_MAP.get(ch, ch) for ch in word)


def ensure_roman_script(text: str) -> str:
    """
    Guarantees any Devanagari or Arabic/Urdu script is converted to Roman Hinglish.
    Preserves Latin portions untouched and ensures no non-Latin script characters remain.
    """
    if not NON_LATIN_SCRIPT_CHECK.search(text):
        return text

    # Replace Arabic punctuation marks
    for ch, repl in ARABIC_PUNCTUATION_MAP.items():
        if ch in text:
            text = text.replace(ch, repl)

    # Transliterate Arabic/Urdu words
    text = ARABIC_WORD_REGEX.sub(lambda m: _transliterate_urdu_word(m.group(0)), text)
    # Transliterate Devanagari words
    text = DEVANAGARI_WORD_REGEX.sub(lambda m: _transliterate_devanagari_word(m.group(0)), text)

    # Residual cleanup safety: ensure no stray non-Latin characters remain
    if NON_LATIN_SCRIPT_CHECK.search(text):
        text = ''.join(
            DEVANAGARI_TO_ROMAN_MAP.get(ch, URDU_CHAR_MAP.get(ch, ch))
            for ch in text
        )

    return re.sub(r' +', ' ', text).strip()


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
