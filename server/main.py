
import asyncio
import base64
import io
import os
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from gnani.stt import GnaniSTTStreamClient

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


# ==========================================
# GNANI PRISMA SPEECH-TO-TEXT
# ==========================================

async def transcribe_pcm_audio(audio_bytes: bytes) -> str:
    """
    Transcribe mono, signed 16-bit, 16 kHz PCM
    audio using Gnani Prisma.
    """

    if not os.getenv("GNANI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="GNANI_API_KEY is missing from the server environment.",
        )

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="No microphone audio was received.",
        )

    if len(audio_bytes) % 2 != 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid PCM audio payload. Expected 16-bit audio samples.",
        )

    audio_file = io.BytesIO(audio_bytes)

    try:
        async with GnaniSTTStreamClient(
            language_code="hi-IN",
            sample_rate=16000,
        ) as stream:

            events = await stream.stream_audio(
                audio_file,
                realtime_pace=False,
            )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gnani Prisma transcription failed: {exc}",
        ) from exc

    transcript_parts = [
        event.text.strip()
        for event in (events or [])
        if getattr(event, "text", None) and event.text.strip()
    ]

    transcript = " ".join(transcript_parts).strip()

    if not transcript:
        raise HTTPException(
            status_code=422,
            detail=(
                "Prisma did not detect clear speech. "
                "Please try recording again."
            ),
        )

    return transcript


# ==========================================
# TRANSCRIBE AUDIO WITHOUT CHANGING ORDER STATE
# ==========================================

@app.post("/api/transcribe")
async def transcribe_audio_only(request: Request):
    """
    Transcribe microphone audio without parsing
    a new order or resetting conversation state.
    """

    sample_rate = request.headers.get(
        "x-audio-sample-rate",
        "16000",
    )

    if sample_rate != "16000":
        raise HTTPException(
            status_code=400,
            detail="Audio must be sampled at 16000 Hz.",
        )

    audio_bytes = await request.body()

    if len(audio_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Recording is too large.",
        )

    transcript = await transcribe_pcm_audio(audio_bytes)

    return {
        "transcript": transcript,
    }


# ==========================================
# MICROPHONE ORDER ENDPOINT
# ==========================================

@app.post("/api/voice-order")
async def create_voice_order(request: Request):
    """
    Receive browser-recorded PCM audio,
    transcribe it using Prisma, and process
    the resulting order using the existing parser.
    """

    sample_rate = request.headers.get(
        "x-audio-sample-rate",
        "16000",
    )

    if sample_rate != "16000":
        raise HTTPException(
            status_code=400,
            detail="Audio must be sampled at 16000 Hz.",
        )

    audio_bytes = await request.body()

    if len(audio_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=(
                "Recording is too large. "
                "Please record a shorter clip."
            ),
        )

    transcript = await transcribe_pcm_audio(audio_bytes)

    order_result = await create_order(
        OrderRequest(transcript=transcript)
    )

    return {
        "transcript": transcript,
        **order_result,
    }


# ==========================================
# NORMAL TEXT ORDER ENDPOINT
# ==========================================

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

        # If clarification is required, speak the question.
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


# ==========================================
# CUSTOMER CORRECTION ENDPOINT
# ==========================================

@app.post("/api/order/correct")
async def correct_order(request: CorrectionRequest):

    transcript = request.transcript.strip()

    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Transcript cannot be empty.",
        )

    current_state = turn_engine.state_machine.state.value

    # Customer responds to a clarification.
    if current_state == "listening":

        try:
            turn_engine.clarification_received()

        except RuntimeError as exc:

            raise HTTPException(
                status_code=409,
                detail=str(exc),
            ) from exc

        action = TurnAction.STOP_AND_CORRECT

    # Customer interrupts while assistant is speaking.
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

        # Backchannel: continue existing audio.
        if action == TurnAction.CONTINUE:

            return {
                "action": action.value,
                "order": request.current_order.model_dump(),
                "confirmation_text": None,
                "audio_base64": None,
            }

        # Unclear speech: ask again.
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

        # Actual correction.
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

        # Parser needs clarification.
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

        # Speak the updated order.
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


# ==========================================
# SERVE FRONTEND
# ==========================================

# Keep this last so API routes are matched first.
app.mount(
    "/",
    StaticFiles(directory="web", html=True),
    name="web",
)

