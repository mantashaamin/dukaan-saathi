
from enum import Enum
from turntaking.rules import TurnAction


class AssistantState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PARSING = "parsing"
    SPEAKING = "speaking"
    DUCKED = "ducked"
    CORRECTING = "correcting"
    CONFIRMED = "confirmed"


class TurnTakingStateMachine:
    """Manage the assistant's conversational states."""

    def __init__(self):
        self.state = AssistantState.IDLE

    def start_listening(self):
        self.state = AssistantState.LISTENING

    def start_parsing(self):
        self.state = AssistantState.PARSING

    def start_speaking(self):
        self.state = AssistantState.SPEAKING

    def detect_customer_speech(self):
        """Temporarily duck playback while evaluating an interruption."""
        if self.state == AssistantState.SPEAKING:
            self.state = AssistantState.DUCKED

    def apply_action(self, action: TurnAction):
        """Apply the classifier's decision after customer speech."""

        if self.state != AssistantState.DUCKED:
            raise RuntimeError(
                "Customer speech can only be classified in DUCKED state."
            )

        if action == TurnAction.CONTINUE:
            self.state = AssistantState.SPEAKING

        elif action == TurnAction.STOP_AND_CORRECT:
            self.state = AssistantState.CORRECTING

        elif action == TurnAction.ASK_AGAIN:
            self.state = AssistantState.LISTENING

        return self.state

    def correction_received(self):
        if self.state != AssistantState.CORRECTING:
            raise RuntimeError("Assistant is not waiting for a correction.")

        self.state = AssistantState.PARSING

    def clarification_received(self):
        """Move to parsing when the customer answers a repeat request."""
        if self.state != AssistantState.LISTENING:
            raise RuntimeError(
                "Assistant is not waiting for a clarification."
            )

        self.state = AssistantState.PARSING

    def confirm_order(self):
        self.state = AssistantState.CONFIRMED

    def reset(self):
        self.state = AssistantState.IDLE


# Shared state machine instance.
turn_state = TurnTakingStateMachine()
