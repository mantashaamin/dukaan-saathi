import re
import unicodedata

from turntaking.rules import BACKCHANNEL_WORDS, INTERRUPTION_WORDS


# Convert common Devanagari backchannels into canonical Romanized forms.
HINDI_BACKCHANNEL_MAP = {
    "हाँहाँ": "haan haan",
    "हांहां": "haan haan",
    "हाँ": "haan",
    "हां": "haan",
    "हम्म": "hmm",
    "हूँ": "hmm",
    "अच्छा अच्छा": "acha acha",
    "अच्छा": "acha",
    "जी": "ji",
    "ठीक है": "theek hai",
    "ठीकहै": "theek hai",
    "ओके": "ok",
}


# Convert Devanagari interruption cues into canonical Romanized forms.
HINDI_INTERRUPTION_MAP = {
    "रुको ज़रा": "ruko",
    "एक मिनट": "ek minute",
    "नहीं": "nahi",
    "नही": "nahi",
    "रुको": "ruko",
    "गलत": "galat",
    "रद्द": "cancel",
    "बदलो": "badlo",
    "हटा दो": "hata do",
    "जोड़ दो": "add kar do",
    "की जगह": "ki jagah",
    "बदल दो": "badal do",
    "कम कर दो": "kam kar do",
    "ज़्यादा कर दो": "zyada kar do",
    "मुझे नहीं पता": "mujhe nahi pata",
    "मुझे पता नहीं": "mujhe nahi pata",
    "समझ नहीं आया": "samajh nahi aaya",
    "कुछ समझ नहीं": "kuch samajh nahi",
    "हटा दीजिए": "hata do",
    "पता नहीं": "pata nahi",
    "कुछ समझ नहीं": "kuch samajh nahi",
}


BACKCHANNEL_TOKENS = {
    "haan",
    "hmm",
    "acha",
    "ji",
    "theek",
    "hai",
    "ok",
    "okay",
}


AMBIGUOUS_PHRASES = {
    "pata nahi",
    "mujhe nahi pata",
    "samajh nahi aaya",
    "abhi yaad nahi aa raha",
    "mujhe yaad nahi",
    "kuch samajh nahi",
}


def normalize_transcript(transcript: str) -> str:
    """Normalize Hindi and Romanized backchannels and interruption cues."""

    text = unicodedata.normalize(
        "NFKC",
        transcript.strip().lower(),
    )

    # Replace longer phrases before shorter phrases.
    for mapping in (
        HINDI_BACKCHANNEL_MAP,
        HINDI_INTERRUPTION_MAP,
    ):
        for hindi, romanized in sorted(
            mapping.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            text = text.replace(hindi, romanized)

    # Remove punctuation and normalize whitespace.
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_features(
    transcript: str,
    duration_seconds: float,
) -> dict:
    """
    Extract features from customer speech.

    Supports Devanagari Hindi and Romanized Hindi.
    Detects backchannels and explicit or contextual corrections.
    """

    text = normalize_transcript(transcript)
    words = re.findall(r"\b[\w]+\b", text)

    is_backchannel = (
        text in BACKCHANNEL_WORDS
        or (
            bool(words)
            and all(word in BACKCHANNEL_TOKENS for word in words)
        )
    )

    is_ambiguous = any(
        re.search(
            r"(?<!\w)" + re.escape(phrase) + r"(?!\w)",
            text,
        )
        for phrase in AMBIGUOUS_PHRASES
    )

    has_interruption_word = (
        any(
            re.search(
                r"(?<!\w)" + re.escape(phrase) + r"(?!\w)",
                text,
            )
            for phrase in INTERRUPTION_WORDS
        )
        and not is_ambiguous
    )

    duration = max(0.0, duration_seconds)

    return {
        "transcript": text,
        "raw_transcript": transcript,
        "duration_seconds": duration,
        "word_count": len(words),
        "character_count": len(text),
        "is_backchannel": is_backchannel,
        "has_interruption_word": has_interruption_word,
        "is_long_speech": duration > 1.0,
        "is_empty": not text,
    }