
from turntaking.classifier import TurnTakingClassifier
from turntaking.rules import TurnAction
from turntaking.state import TurnTakingStateMachine


class TurnTakingEngine:
    """
    Coordinates interruption classification and assistant state changes.
    """

    def __init__(self):
        self.classifier = TurnTakingClassifier()
        self.state_machine = TurnTakingStateMachine()

    def start_speaking(self):
        self.state_machine.start_speaking()

    def handle_customer_speech(
        self,
        transcript: str,
        duration_seconds: float,
    ) -> dict:
        """
        Temporarily duck the assistant, classify customer speech,
        and apply the resulting turn-taking action.
        """

        if self.state_machine.state.value != "speaking":
            raise RuntimeError(
                "The assistant must be speaking before an interruption "
                "can be handled."
            )

        self.state_machine.detect_customer_speech()

        action = self.classifier.classify(
            transcript=transcript,
            duration_seconds=duration_seconds,
        )

        new_state = self.state_machine.apply_action(action)

        return {
            "action": action.value,
            "state": new_state.value,
            "transcript": transcript,
        }

    def correction_received(self):
        self.state_machine.correction_received()

    def clarification_received(self):
        """Accept the customer's response after ASK_AGAIN."""
        self.state_machine.clarification_received()

    def confirm_order(self):
        self.state_machine.confirm_order()

    def reset(self):
        self.state_machine.reset()


# Shared engine instance.
turn_engine = TurnTakingEngine()
