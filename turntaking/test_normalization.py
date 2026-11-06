
import pytest

from turntaking.features import (
    normalize_transcript,
    extract_features,
)
from turntaking.rules import classify_interruption


@pytest.mark.parametrize(
    "original, expected",
    [
        ("हाँ", "haan"),
        ("हाँ हाँ", "haan haan"),
        ("अच्छा", "acha"),
        ("ठीक है", "theek hai"),
        ("रुको ज़रा", "ruko zara"),
        ("एक मिनट", "ek minute"),
        ("नहीं", "nahi"),
        ("हटा दो", "hata do"),
        ("ज्यादा कर दो", "zyada kar do"),
        ("मुझे नहीं पता", "mujhe nahi pata"),
        ("achha", "acha"),
        ("accha", "acha"),
        ("haan haan", "haan haan"),
    ],
)
def test_transcript_normalization(original, expected):
    assert normalize_transcript(original) == expected


@pytest.mark.parametrize(
    "transcript, expected",
    [
        ("हाँ", "continue"),
        ("हाँ हाँ", "continue"),
        ("अच्छा", "continue"),
        ("ठीक है", "continue"),
        ("haan bilkul", "continue"),
        ("haan sahi hai", "continue"),

        # New conversational backchannel cases
        ("achha samajh gaya", "continue"),
        ("जी बताइए", "continue"),
        ("haan aage bolo", "continue"),
        ("ठीक ठीक", "continue"),
        ("अच्छा जी, बोलिए", "continue"),
        ("haan sun raha hoon", "continue"),

        # Existing correction cases
        ("रुको ज़रा", "stop_and_correct"),
        ("एक मिनट", "stop_and_correct"),
        ("चीनी मत डालिए", "stop_and_correct"),
        ("quantity aadhi kar do", "stop_and_correct"),
        ("bhai ek item aur add karna hai", "stop_and_correct"),
        ("is order mein ek change hai", "stop_and_correct"),

        # Ambiguous cases
        ("मुझे नहीं पता", "ask_again"),
        ("मुझे याद नहीं आ रहा", "ask_again"),
        ("pata nahi", "ask_again"),
        ("", "ask_again"),
    ],
)
def test_turn_classification(transcript, expected):
    result = classify_interruption(transcript, 0.8)
    assert result.value == expected


def test_empty_transcript_features():
    result = extract_features("", 0.0)

    assert result["is_empty"] is True
    assert result["is_backchannel"] is False


def test_ambiguous_phrase_is_not_correction():
    result = extract_features("मुझे नहीं पता", 0.8)

    assert result["is_ambiguous"] is True
    assert result["has_interruption_word"] is False


def test_backchannel_is_not_interruption():
    result = extract_features("हाँ हाँ", 0.8)

    assert result["is_backchannel"] is True
    assert result["has_interruption_word"] is False
