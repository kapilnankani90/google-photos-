"""
Focused tests for D2 transcription script normalization layer.

Verifies:
1. Pure Latin input remains unchanged.
2. Devanagari input becomes Roman.
3. Arabic/Urdu-script input becomes Roman.
4. Mixed Latin + Devanagari input preserves Latin portions.
5. Mixed Latin + Arabic/Urdu input preserves Latin portions.
6. Output contains no Devanagari, Arabic, or Urdu characters after normalization.
"""

from app.api.v1.endpoints.transcribe import ensure_roman_script, NON_LATIN_SCRIPT_CHECK


def test_pure_latin_unchanged():
    """1. Pure Latin input remains unchanged."""
    text = "photo of family trip to Goa beach at sunset"
    assert ensure_roman_script(text) == text


def test_devanagari_becomes_roman():
    """2. Devanagari input becomes Roman."""
    text = "मुझे याद है एक फैमिली ट्रिप था हम बीच पर थे सनसेट के टाइम पर"
    result = ensure_roman_script(text)
    assert not NON_LATIN_SCRIPT_CHECK.search(result)
    assert "family" in result and "trip" in result and "sunset" in result and "beach" in result


def test_arabic_urdu_becomes_roman():
    """3. Arabic/Urdu-script input becomes Roman (actual production failure case)."""
    text = "مجھے یاد ہے ایک فیملی ٹرپ تھا ہم بیچ پر تھے سنسٹ کے ٹائم پر"
    result = ensure_roman_script(text)
    assert not NON_LATIN_SCRIPT_CHECK.search(result)
    assert result == "mujhe yaad hai ek family trip tha hum beach par the sunset ke time par"


def test_mixed_latin_devanagari_preserves_latin():
    """4. Mixed Latin + Devanagari input preserves Latin portions."""
    text = "photo of Rohtang trip में snow skiing"
    result = ensure_roman_script(text)
    assert not NON_LATIN_SCRIPT_CHECK.search(result)
    assert result == "photo of Rohtang trip mein snow skiing"


def test_mixed_latin_arabic_urdu_preserves_latin():
    """5. Mixed Latin + Arabic/Urdu input preserves Latin portions."""
    text = "photo of Goa beach میں sunset ke time par"
    result = ensure_roman_script(text)
    assert not NON_LATIN_SCRIPT_CHECK.search(result)
    assert result == "photo of Goa beach mein sunset ke time par"


def test_output_contains_no_devanagari_or_arabic_script():
    """6. Output contains no Devanagari, Arabic, or Urdu characters after normalization."""
    samples = [
        "photo of family trip to Goa beach at sunset",
        "मुझे याद है एक फैमिली ट्रिप था",
        "مجھے یاد ہے ایک فیملی ٹرپ تھا ہم بیچ پر تھے سنسٹ کے ٹائم پر",
        "photo of Rohtang trip में snow skiing",
        "photo of Goa beach میں sunset ke time par",
    ]
    for sample in samples:
        norm = ensure_roman_script(sample)
        assert not NON_LATIN_SCRIPT_CHECK.search(norm), f"Residual non-Latin found in: {norm}"
