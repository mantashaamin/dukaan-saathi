
import asyncio
import base64
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from server.order_parser import ParsedOrder, parse_order
from server.tts import synthesize_speech
from turntaking.engine import turn_engine
from turntaking.rules import TurnAction


app = FastAPI(title="Dukaan Saathi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5501",
        "http://localhost:5501",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=2)


class OrderRequest(BaseModel):
    transcript: str = Field(min_length=1)


class CorrectionRequest(BaseModel):
    transcript: str = Field(min_length=1)
    current_order: ParsedOrder
    duration_seconds: float = Field(default=1.5, ge=0)


def build_confirmation_text(order: ParsedOrder) -> str:
    if not order.items:
        return (
            "Bhaiya, aapka order khaali hai. "
            "Kya aap order cancel karna chahte hain?"
        )

    items_text = []

    for item in order.items:
        quantity = float(item.quantity)

        quantity_text = (
            str(int(quantity))
            if quantity.is_integer()
            else str(quantity)
        )

        items_text.append(
            f"{quantity_text} {item.unit} {item.name}"
        )

    return (
        "Bhaiya, aapka order hai: "
        f"{', '.join(items_text)}. Sahi hai na?"
    )


async def generate_audio(text: str) -> str:
    """Generate TTS audio and return base64-encoded MP3."""
    loop = asyncio.get_running_loop()

    audio = await loop.run_in_executor(
        executor,
        synthesize_speech,
        text,
    )

    return base64.b64encode(audio).decode("utf-8")


def clarification_text(order: ParsedOrder, fallback: str) -> str:
    return order.clarification_question or fallback


@app.get("/health")
async def health_check():
    return {
        "status": "running",
        "project": "Dukaan Saathi",
    }


@app.post("/api/order")
async def create_order(request: OrderRequest):
    transcript = request.transcript.strip()

    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty.",
        )

    try:
        loop = asyncio.get_running_loop()

        order = await loop.run_in_executor(
            executor,
            parse_order,
            transcript,
        )

        # Start a fresh conversation state.
        turn_engine.reset()

        # If the parser needs clarification, speak that question.
        if order.needs_clarification:
            text = clarification_text(
                order,
                "Bhaiya, kripya order thoda clear bataiye.",
            )

            turn_engine.state_machine.start_listening()
            audio_base64 = await generate_audio(text)

            return {
                "action": "ask_again",
                "order": order.model_dump(),
                "confirmation_text": text,
                "audio_base64": audio_base64,
            }

        # Normal order confirmation.
        text = build_confirmation_text(order)
        audio_base64 = await generate_audio(text)

        turn_engine.start_speaking()

        return {
            "action": "confirm_order",
            "order": order.model_dump(),
            "confirmation_text": text,
            "audio_base64": audio_base64,
        }

    except (RuntimeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@app.post("/api/order/correct")
async def correct_order(request: CorrectionRequest):
    transcript = request.transcript.strip()

    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty.",
        )

    current_state = turn_engine.state_machine.state.value

    # Customer is responding to a previous clarification.
    if current_state == "listening":
        try:
            turn_engine.clarification_received()
        except RuntimeError as exc:
            raise HTTPException(
                status_code=409,
                detail=str(exc),
            ) from exc

        action = TurnAction.STOP_AND_CORRECT

    # Customer interrupts while the assistant is speaking.
    elif current_state == "speaking":
        try:
            result = turn_engine.handle_customer_speech(
                transcript=transcript,
                duration_seconds=request.duration_seconds,
            )
        except RuntimeError as exc:
            raise HTTPException(
                status_code=409,
                detail=str(exc),
            ) from exc

        action = TurnAction(result["action"])

        # Backchannel: preserve and resume the existing audio.
        if action == TurnAction.CONTINUE:
            return {
                "action": action.value,
                "order": request.current_order.model_dump(),
                "confirmation_text": None,
                "audio_base64": None,
            }

        # Unclear speech: generate a NEW clarification voice response.
        if action == TurnAction.ASK_AGAIN:
            text = (
                "Bhaiya, aapne kya kaha? "
                "Kripya dobara bataiye."
            )

            turn_engine.state_machine.start_listening()
            audio_base64 = await generate_audio(text)

            return {
                "action": action.value,
                "order": request.current_order.model_dump(),
                "confirmation_text": text,
                "audio_base64": audio_base64,
            }

        # Actual correction: move into correction processing.
        try:
            turn_engine.correction_received()
        except RuntimeError as exc:
            raise HTTPException(
                status_code=409,
                detail=str(exc),
            ) from exc

    else:
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot process customer speech in "
                f"{current_state} state."
            ),
        )

    try:
        loop = asyncio.get_running_loop()

        updated_order = await loop.run_in_executor(
            executor,
            parse_order,
            transcript,
            request.current_order,
        )

        # Parser needs more information before updating the order.
        if updated_order.needs_clarification:
            text = clarification_text(
                updated_order,
                "Bhaiya, kripya correction thoda clear bataiye.",
            )

            turn_engine.state_machine.start_listening()
            audio_base64 = await generate_audio(text)

            return {
                "action": action.value,
                "order": updated_order.model_dump(),
                "confirmation_text": text,
                "audio_base64": audio_base64,
            }

        # Speak the updated order, not the original order.
        text = build_confirmation_text(updated_order)
        audio_base64 = await generate_audio(text)

        turn_engine.start_speaking()

        return {
            "action": action.value,
            "order": updated_order.model_dump(),
            "confirmation_text": text,
            "audio_base64": audio_base64,
        }

    except (RuntimeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# Keep this last so API routes are matched before static files.
app.mount(
    "/",
    StaticFiles(directory="web", html=True),
    name="web",
)
