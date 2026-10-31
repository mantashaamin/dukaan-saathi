
import re

from turntaking.rules import BACKCHANNEL_WORDS, INTERRUPTION_WORDS


def extract_features(transcript: str, duration_seconds: float) -> dict:
    """
    Extract basic features from a customer's speech.
    These features will help the turn-taking engine
    distinguish acknowledgements from interruptions.
    """

    text = transcript.strip().lower()

    words = re.findall(r"\b[\w]+\b", text)

    is_backchannel = text in BACKCHANNEL_WORDS

    has_interruption_word = any(
        phrase in text
        for phrase in INTERRUPTION_WORDS
    )

    return {
        "transcript": text,
        "duration_seconds": max(0.0, duration_seconds),
        "word_count": len(words),
        "character_count": len(text),
        "is_backchannel": is_backchannel,
        "has_interruption_word": has_interruption_word,
        "is_long_speech": duration_seconds > 1.0,
        "is_empty": not text,
    }
