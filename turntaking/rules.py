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
    # Explicit interruptions
    "ruko",
    "ruk jao",
    "nahi",
    "ek minute",
    "wait",
    "galat",
    "cancel",
    "badlo",

    # Contextual order corrections
    "hata do",
    "add kar do",
    "ki jagah",
    "change karni hai",
    "order mein correction",
    "quantity change",
    "quantity badlo",
    "badal do",
    "kam kar do",
    "zyada kar do",
    "replace",
    "instead",
}


def classify_interruption(
    transcript: str,
    duration_seconds: float,
) -> TurnAction:
    """
    Classify customer speech during assistant playback.

    Short backchannels continue playback.
    Explicit or contextual corrections stop playback.
    Uncertain speech asks the customer to repeat.
    """

    from turntaking.features import extract_features

    features = extract_features(transcript, duration_seconds)

    if features["is_empty"]:
        return TurnAction.ASK_AGAIN

    if (
        features["is_backchannel"]
        and features["duration_seconds"] <= 1.0
    ):
        return TurnAction.CONTINUE

    if features["has_interruption_word"]:
        return TurnAction.STOP_AND_CORRECT

    return TurnAction.ASK_AGAIN