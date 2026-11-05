import re
import unicodedata

from turntaking.rules import BACKCHANNEL_WORDS, INTERRUPTION_WORDS


# Hindi backchannels -> canonical Romanized forms.
HINDI_BACKCHANNEL_MAP = {
    "हाँ हाँ": "haan haan",
    "हां हां": "haan haan",
    "हाँहाँ": "haan haan",
    "हांहां": "haan haan",
    "हाँ": "haan",
    "हां": "haan",
    "हम्म": "hmm",
    "हूँ": "hmm",
    "हूं": "hmm",
    "अच्छा अच्छा": "acha acha",
    "अच्छा": "acha",
    "अच्छी": "acha",
    "जी": "ji",
    "ठीक है": "theek hai",
    "ठीकहै": "theek hai",
    "ओके": "ok",
    "बिल्कुल": "bilkul",
    "बिलकुल": "bilkul",
    "सही है": "sahi hai",
}

# Hindi corrections and interruption phrases.
HINDI_INTERRUPTION_MAP = {
    "रुको ज़रा": "ruko zara",
    "रुको जरा": "ruko zara",
    "रुकना ज़रा": "rukna zara",
    "रुकना जरा": "rukna zara",
    "रुक जाओ": "ruk jao",
    "रुकिए": "ruko",
    "रुको": "ruko",
    "एक मिनट": "ek minute",
    "एक मिनिट": "ek minute",
    "नहीं": "nahi",
    "नही": "nahi",
    "गलत": "galat",
    "रद्द": "cancel",
    "कैंसल": "cancel",
    "बदलो": "badlo",
    "बदल दो": "badal do",
    "बदल दीजिए": "badal do",
    "हटा दो": "hata do",
    "हटा दीजिए": "hata do",
    "जोड़ दो": "add kar do",
    "जोड़ दीजिए": "add kar do",
    "की जगह": "ki jagah",
    "के बदले": "ki jagah",
    "कम कर दो": "kam kar do",
    "कम कर दीजिए": "kam kar do",
    "आधी कर दो": "aadhi kar do",
    "आधा कर दो": "aadha kar do",
    "ज़्यादा कर दो": "zyada kar do",
    "ज्यादा कर दो": "zyada kar do",
    "ज्यादा कर दीजिए": "zyada kar do",
    "मत डालिए": "mat daliye",
    "मत डालना": "mat dalna",
    "नहीं चाहिए": "nahi chahiye",
    "एक आइटम और जोड़ना है": "ek item aur add karna hai",
    "एक चीज़ और जोड़नी है": "ek cheez aur add karni hai",
    "इस ऑर्डर में एक बदलाव है": "is order mein ek change hai",
    "इस ऑर्डर में बदलाव है": "is order mein ek change hai",
    "मुझे नहीं पता": "mujhe nahi pata",
    "मुझे पता नहीं": "mujhe nahi pata",
    "पता नहीं": "pata nahi",
    "समझ नहीं आया": "samajh nahi aaya",
    "समझ में नहीं आया": "samajh nahi aaya",
    "कुछ समझ नहीं": "kuch samajh nahi",
    "चीनी": "cheeni",
    "चिनी": "chini",
    "मुझे याद नहीं आ रहा": "mujhe yaad nahi aa raha",
}

# Romanized spelling variations -> canonical forms.
ROMAN_ALIASES = {
    "achha": "acha",
    "accha": "acha",
    "acchha": "acha",
    "bilkul": "bilkul",
    "bilkul": "bilkul",
    "rukna zara": "rukna zara",
    "rukna jara": "rukna zara",
    "ruko jara": "ruko zara",
    "ek min": "ek minute",
    "aadhi karna": "aadhi kar do",
    "aadha karna": "aadha kar do",
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
    "bilkul",
    "sahi",
}

AMBIGUOUS_PHRASES = {
    "pata nahi",
    "mujhe nahi pata",
    "samajh nahi aaya",
    "abhi yaad nahi aa raha",
    "mujhe yaad nahi",
    "mujhe yaad nahi aa raha",
    "kuch samajh nahi",
    "shayad woh wala",
    "woh kaun sa tha",
    "umm kaunsa item tha",
    "i am not sure",
}

# Extra contextual correction phrases.
CONTEXTUAL_CORRECTION_PHRASES = {
    "rukna zara",
    "ruko zara",
    "quantity aadhi kar do",
    "quantity aadha kar do",
    "aadhi kar do",
    "aadha kar do",
    "add karna hai",
    "ek item aur add karna hai",
    "ek cheez aur add karni hai",
    "is order mein ek change hai",
    "order mein ek change hai",
    "mat daliye",
    "mat dalna",
    "nahi chahiye",
    "tel nahi chahiye",
    "chini mat daliye",
    "cheeni mat daliye",
}


def _clean_unicode_punctuation(text: str) -> str:
    """Remove punctuation while preserving Unicode letters and marks."""

    result = []

    for char in text:
        category = unicodedata.category(char)

        if category.startswith(("L", "M", "N")) or char.isspace():
            result.append(char)
        else:
            result.append(" ")

    return "".join(result)


def _replace_phrases(text: str, mapping: dict) -> str:
    """Replace complete phrases, longest phrases first."""

    for original, replacement in sorted(
        mapping.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        pattern = (
            r"(?<!\w)"
            + re.escape(original)
            + r"(?!\w)"
        )
        text = re.sub(pattern, replacement, text)

    return text


def normalize_transcript(transcript: str) -> str:
    """Normalize Devanagari Hindi and Romanized Hindi."""

    if not transcript:
        return ""

    text = unicodedata.normalize(
        "NFKC",
        transcript.strip().lower(),
    )

    text = unicodedata.normalize("NFC", text)

    # Preserve Devanagari vowel signs and combining marks.
    text = _clean_unicode_punctuation(text)
    text = re.sub(r"\s+", " ", text).strip()

    # Convert Devanagari phrases into canonical Romanized forms.
    text = _replace_phrases(text, HINDI_BACKCHANNEL_MAP)
    text = _replace_phrases(text, HINDI_INTERRUPTION_MAP)

    # Normalize Romanized spelling variations.
    text = _replace_phrases(text, ROMAN_ALIASES)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def _contains_phrase(text: str, phrases: set) -> bool:
    """Check whether text contains any complete phrase."""

    for phrase in phrases:
        pattern = (
            r"(?<!\w)"
            + re.escape(phrase)
            + r"(?!\w)"
        )

        if re.search(pattern, text):
            return True

    return False


def extract_features(
    transcript: str,
    duration_seconds: float,
) -> dict:
    """Extract backchannel, ambiguity and interruption features."""

    text = normalize_transcript(transcript)

    words = re.findall(r"\b[\w]+\b", text)

    is_backchannel = (
        bool(words)
        and all(
            word in BACKCHANNEL_TOKENS
            for word in words
        )
    )

    is_ambiguous = _contains_phrase(
        text,
        AMBIGUOUS_PHRASES,
    )

    has_interruption_word = (
        _contains_phrase(text, INTERRUPTION_WORDS)
        or _contains_phrase(
            text,
            CONTEXTUAL_CORRECTION_PHRASES,
        )
    )

    # Ambiguous phrases must not be treated as corrections.
    if is_ambiguous:
        has_interruption_word = False

    duration = max(0.0, float(duration_seconds))

    return {
        "transcript": text,
        "raw_transcript": transcript,
        "duration_seconds": duration,
        "word_count": len(words),
        "character_count": len(text),
        "is_backchannel": is_backchannel,
        "is_ambiguous": is_ambiguous,
        "has_interruption_word": has_interruption_word,
        "is_long_speech": duration > 1.0,
        "is_empty": not text,
    }