
from enum import Enum


class TurnAction(str, Enum):
    CONTINUE = "continue"
    STOP_AND_CORRECT = "stop_and_correct"
    ASK_AGAIN = "ask_again"


BACKCHANNEL_WORDS = {
    "haan",
    "hmm",
    "acha",
    "ji",
    "theek hai",
    "ok",
    "okay",
}

INTERRUPTION_WORDS = {
    "ruko",
    "nahi",
    "ek minute",
    "wait",
    "galat",
    "cancel",
    "badlo",
}


def classify_interruption(
    transcript: str,
    duration_seconds: float,
) -> TurnAction:
    """
    Classify customer speech during assistant playback
    using extracted speech features.
    """

    # Import here to avoid a circular import.
    from turntaking.features import extract_features

    features = extract_features(transcript, duration_seconds)

    # No usable speech detected.
    if features["is_empty"]:
        return TurnAction.ASK_AGAIN

    # Short acknowledgements should not interrupt playback.
    if (
        features["is_backchannel"]
        and features["duration_seconds"] <= 1.0
    ):
        return TurnAction.CONTINUE

    # Explicit correction or interruption.
    if features["has_interruption_word"]:
        return TurnAction.STOP_AND_CORRECT

    # Longer speech is likely a genuine interruption.
    if features["is_long_speech"]:
        return TurnAction.STOP_AND_CORRECT

    # Uncertain speech: ask the customer to repeat.
    return TurnAction.ASK_AGAIN
