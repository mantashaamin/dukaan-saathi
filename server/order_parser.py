
import json
import os

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"


class OrderItem(BaseModel):
    name: str = Field(min_length=1)
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
    """Parse, normalize, and validate the LLM's JSON response."""
    data = json.loads(response_text)

    if not isinstance(data, dict):
        raise ValueError("The model response must be a JSON object.")

    items = data.get("items", [])

    if not isinstance(items, list):
        raise ValueError("'items' must be a JSON list.")

    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Each order item must be a JSON object.")

        if "unit" in item:
            item["unit"] = normalize_unit(item["unit"])

    return ParsedOrder.model_validate(data)


def parse_order(
    transcript: str,
    current_order: ParsedOrder | None = None,
) -> ParsedOrder:
    """Convert a Hinglish kirana order into structured data."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from .env")

    transcript = transcript.strip()

    if not transcript:
        raise ValueError("Transcript cannot be empty.")

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
- - CRITICAL CORRECTION RULE:
  When a customer clearly replaces an existing item X with a new item Y,
  and does not state a new quantity or unit, ALWAYS inherit X's existing
  quantity and unit from current_order for Y.
  Example:
  Current order: 2 kg aloo, 1 kg tamatar.
  Customer: "Tamatar nahi, pyaz de do."
  Updated order: 2 kg aloo, 1 kg pyaz.
  Do not ask for Y's quantity when X has a known quantity and unit.
  Preserve all unrelated existing items.
  Only ask for clarification if the replacement itself is ambiguous.
- Preserve X's quantity and unit for Y when new ones are not stated.
- Example: "Ek packet namak nahi, atta" means one packet of atta only.
- Never keep a rejected item when a clear replacement is stated.
- For countable items such as eggs, use unit "piece".
- Never return a null or empty unit. If the unit cannot be determined,
  set needs_clarification to true and ask a short question.
- If the customer clearly cancels the entire order, such as
  "nahi rehne do", "order cancel karo", or "sab rehne do",
  return an empty items list and set needs_clarification to true.
- Apply cancellation only when the whole order is clearly cancelled.

- The user message contains a JSON object with:
  "current_order" and "customer_message".
- If current_order is provided, treat it as the order currently being
  confirmed by the assistant.
- Interpret customer_message as a possible correction to current_order.
- Return the COMPLETE updated order, not just the changed items.
- Preserve all existing items unless the customer removes or replaces them.
- If the customer replaces an item, remove the old item and add the
  replacement. Preserve its quantity and unit unless new values are stated.
- If the customer changes a quantity, update that item's quantity.
- If the customer adds an item, retain existing items and add the new one.
- If the customer's correction is ambiguous, set needs_clarification
  to true and ask a short question in Hindi.
- If current_order is null, treat customer_message as a new order.

- Return valid JSON only. Do not include Markdown fences or extra text.
"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
    {"role": "system", "content": prompt},
    {
        "role": "user",
        "content": json.dumps(
            {
                "current_order": (
                    current_order.model_dump()
                    if current_order is not None
                    else None
                ),
                "customer_message": transcript,
            },
            ensure_ascii=False,
        ),
    },
],
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

        if not isinstance(content, str) or not content.strip():
            raise ValueError("Groq returned an empty response.")

        return parse_order_response(content)

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Groq returned HTTP {exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc

    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Groq network request failed: {exc}"
        ) from exc

    except (KeyError, IndexError, TypeError, json.JSONDecodeError,
            ValidationError, ValueError) as exc:
        raise RuntimeError(
            f"Could not parse Groq order response "
            f"({type(exc).__name__}): {exc}"
        ) from exc
