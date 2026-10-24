
import json
import os

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"


class OrderItem(BaseModel):
    name: str
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1)

class ParsedOrder(BaseModel):
    items: list[OrderItem]
    needs_clarification: bool = False
    clarification_question: str | None = None

def normalize_unit(unit: str) -> str:
    """Standardize common unit abbreviations."""
    aliases = {
        "l": "litre",
        "liter": "litre",
        "liters": "litre",
        "litres": "litre",
        "pcs": "piece",
        "pc": "piece",
        "pieces": "piece",
        "kgs": "kg",
        "kilogram": "kg",
        "kilograms": "kg",
        "grams": "g",
        "gram": "g",
    }
    if not isinstance(unit, str):
        return ""
    cleaned = unit.strip().lower()
    return aliases.get(cleaned, cleaned)

def parse_order_response(response_text: str) -> ParsedOrder:
    """Validate and normalize an LLM JSON response."""
    data = json.loads(response_text)

    for item in data.get("items", []):
        if "unit" in item:
            item["unit"] = normalize_unit(item["unit"])

    return ParsedOrder.model_validate(data)


def parse_order(transcript: str) -> ParsedOrder:
    """Convert a Hinglish kirana-order transcript into structured data."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from .env")

    if not transcript.strip():
        raise ValueError("Transcript cannot be empty")

    prompt = """
You extract kirana-store orders from Hindi or Hinglish transcripts.

Return only a JSON object with this schema:
{
  "items": [
    {"name": "chaawal", "quantity": 1, "unit": "kg"}
  ],
  "needs_clarification": false,
  "clarification_question": null
}

Rules:
- Preserve the quantities and units the customer actually stated.
- Convert Hindi number words into numbers.
- Normalize common units such as kilo to kg and gram to g.
- Do not invent prices, quantities, or items.
- If a quantity may apply to multiple items and the wording is unclear,
  set needs_clarification to true and ask a short question in Hindi.
- If the order is unclear, do not silently guess.
- Item names may be written in Hindi or commonly used Hinglish.
- Treat phrases like "X nahi, Y" as a correction: remove X and replace it with Y.
- Preserve X's quantity and unit for Y when the customer does not state new ones.
- Example: "Ek packet namak nahi, atta" means one packet of atta only.
- Never keep the rejected item when a clear replacement is stated.
- For countable items such as eggs, use unit "piece".
- Never return a null or empty unit. If the unit cannot be determined, set needs_clarification to true and ask a short question.
"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": transcript},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0,
    }

    try:
        response = httpx.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=45.0,
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return parse_order_response(content)

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Groq returned HTTP {exc.response.status_code}: "
            f"{exc.response.text}"
    ) from exc
    except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError,
            ValidationError) as exc:
        raise RuntimeError(
            f"Could not parse the OpenRouter order response: {exc}"
        ) from exc
