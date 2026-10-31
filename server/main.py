
import asyncio
import base64
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from server.order_parser import ParsedOrder, parse_order
from turntaking.classifier import turn_classifier
from turntaking.rules import TurnAction
from server.tts import synthesize_speech

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


def build_confirmation_text(order) -> str:
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
        f"Bhaiya, aapka order hai: "
        f"{', '.join(items_text)}. Sahi hai na?"
    )


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

    loop = asyncio.get_running_loop()

    try:
        order = await loop.run_in_executor(
            executor,
            parse_order,
            transcript,
        )

        confirmation_text = build_confirmation_text(order)

        if order.needs_clarification:
            return {
                "order": order.model_dump(),
                "confirmation_text": (
                    order.clarification_question
                    or "Bhaiya, kripya order thoda clear bataiye."
                ),
                "audio_base64": None,
            }

        audio = await loop.run_in_executor(
            executor,
            synthesize_speech,
            confirmation_text,
        )

        return {
            "order": order.model_dump(),
            "confirmation_text": confirmation_text,
            "audio_base64": base64.b64encode(audio).decode("utf-8"),
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

    action = turn_classifier.classify(
        transcript,
        request.duration_seconds,
    )

    if action == TurnAction.CONTINUE:
        return {
            "action": action.value,
            "order": request.current_order.model_dump(),
            "confirmation_text": None,
            "audio_base64": None,
        }

    if action == TurnAction.ASK_AGAIN:
        return {
            "action": action.value,
            "order": request.current_order.model_dump(),
            "confirmation_text": (
                "Bhaiya, aapne kya kaha? Kripya dobara bataiye."
            ),
            "audio_base64": None,
        }

    loop = asyncio.get_running_loop()

    try:
        updated_order = await loop.run_in_executor(
            executor,
            parse_order,
            transcript,
            request.current_order,
        )

        if updated_order.needs_clarification:
            return {
                "action": action.value,
                "order": updated_order.model_dump(),
                "confirmation_text": (
                    updated_order.clarification_question
                    or "Bhaiya, kripya correction thoda clear bataiye."
                ),
                "audio_base64": None,
            }

        confirmation_text = build_confirmation_text(updated_order)

        audio = await loop.run_in_executor(
            executor,
            synthesize_speech,
            confirmation_text,
        )

        return {
            "action": action.value,
            "order": updated_order.model_dump(),
            "confirmation_text": confirmation_text,
            "audio_base64": base64.b64encode(audio).decode("utf-8"),
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
