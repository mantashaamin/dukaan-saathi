
from turntaking.rules import TurnAction, classify_interruption


class TurnTakingClassifier:
    """
    Public interface for the turn-taking engine.

    Takes a customer's transcript and speech duration,
    then returns the appropriate turn-taking action.
    """

    def classify(
        self,
        transcript: str,
        duration_seconds: float,
    ) -> TurnAction:
        return classify_interruption(
            transcript=transcript,
            duration_seconds=duration_seconds,
        )


# Shared instance for use across the application.
turn_classifier = TurnTakingClassifier()
