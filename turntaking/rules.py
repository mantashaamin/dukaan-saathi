from enum import Enum


class TurnAction(str, Enum):
    CONTINUE = "continue"
    STOP_AND_CORRECT = "stop_and_correct"
    ASK_AGAIN = "ask_again"


# Short acknowledgements that should not interrupt playback.
BACKCHANNEL_WORDS = {
    "haan",
    "hmm",
    "acha",
    "ji",
    "theek hai",
    "ok",
    "okay",
    "haan bilkul",
    "haan sahi hai",
}


# Explicit interruption and correction phrases.
INTERRUPTION_WORDS = {
    # Direct interruptions
    "ruko",
    "ruk jao",
    "rukna zara",
    "ruko zara",
    "ek minute",
    "wait",
    "galat",
    "cancel",
    "nahi",
    "badlo",

    # Removing or replacing products
    "hata do",
    "hata dijiye",
    "add kar do",
    "add karna hai",
    "ki jagah",
    "badal do",
    "replace",
    "instead",

    # Quantity changes
    "quantity change",
    "quantity badlo",
    "quantity aadhi kar do",
    "quantity aadha kar do",
    "aadhi kar do",
    "aadha kar do",
    "kam kar do",
    "zyada kar do",

    # Contextual order corrections
    "change karni hai",
    "order mein correction",
    "is order mein ek change hai",
    "order mein ek change hai",
    "ek item aur add karna hai",
    "ek cheez aur add karni hai",

    # Negative product instructions
    "mat daliye",
    "mat dalna",
    "nahi chahiye",
    "cheeni mat daliye",
    "chini mat daliye",
}


def classify_interruption(
    transcript: str,
    duration_seconds: float,
) -> TurnAction:
    """
    Classify customer speech during assistant playback.

    Ambiguous statements ask for clarification.
    Short backchannels allow playback to continue.
    Explicit or contextual corrections stop playback.
    """

    from turntaking.features import extract_features

    features = extract_features(
        transcript,
        duration_seconds,
    )

    if features["is_empty"]:
        return TurnAction.ASK_AGAIN

    # Ambiguity takes priority over correction keywords.
    if features["is_ambiguous"]:
        return TurnAction.ASK_AGAIN

    if (
        features["is_backchannel"]
        and features["duration_seconds"] <= 1.0
    ):
        return TurnAction.CONTINUE

    if features["has_interruption_word"]:
        return TurnAction.STOP_AND_CORRECT

    return TurnAction.ASK_AGAIN