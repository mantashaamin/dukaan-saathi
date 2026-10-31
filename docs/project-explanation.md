# Dukaan Saathi — Project Explanation

## 1. Project Overview

**Dukaan Saathi** is a voice-based assistant designed to help customers place grocery orders at local kirana stores using natural Hindi and Hinglish speech.

Instead of requiring customers to type product names and quantities, the assistant aims to let them speak naturally. It converts speech into text, extracts a structured order, and reads the order back for confirmation.

### Example

A customer says:

"Bhaiya, ek kilo chawal, do kilo aloo aur 500 gram lehsun."

The system should extract an order similar to:

```json
{
  "items": [
    {"name": "chawal", "quantity": 1, "unit": "kg"},
    {"name": "aloo", "quantity": 2, "unit": "kg"},
    {"name": "lehsun", "quantity": 500, "unit": "g"}
  ],
  "needs_clarification": false,
  "clarification_question": null
}
```

The assistant then generates a spoken confirmation of the parsed order.

The project currently has a working typed-order demonstration. Live microphone-to-Prisma streaming and intelligent turn-taking remain under development.

## 2. Problem Statement

Many customers are comfortable speaking in Hindi or Hinglish but may find a text-based ordering interface inconvenient. Kirana orders can also contain informal product names, quantities, corrections, and incomplete instructions.

Dukaan Saathi aims to make ordering more natural while converting customer requests into structured data that software can process.

## 3. Core Technologies

### Gnani Prisma — Speech-to-Text (STT)

Speech-to-text converts spoken audio into written text.

**Purpose:** Convert a customer's Hindi/Hinglish voice input into a transcript that the order parser can process.

**Verified status:** File-based transcription using Gnani Prisma was tested successfully with a sample audio file. Streaming STT was attempted, but the WebSocket connection handshake timed out. True streaming integration is not yet working.

### LLM-based Order Parser

A large language model interprets the transcript and converts it into structured order data.

**Implementation:** The Python module `server/order_parser.py` uses the Groq API with the `openai/gpt-oss-20b` model.

**Purpose:**
- Identify product names, quantities, and units.
- Convert Hindi number words into numerical quantities.
- Normalize common unit variations.
- Handle product corrections and cancellations.
- Request clarification when the customer's intent is unclear.

### Pydantic — Data Validation

Pydantic validates the model's response against the expected data structure.

Each order item must contain a product name, a positive quantity, and a non-empty unit.

This catches malformed responses before the application uses them. Validation does not guarantee that the model has interpreted the customer's intention correctly.

### Gnani Timbre — Text-to-Speech (TTS)

Text-to-speech converts written text into audio.

**Purpose:** Read the interpreted order back to the customer so they can verify it.

**Verified status:** Hindi confirmation audio was generated successfully using Gnani Timbre and played back successfully.

## 4. Current System Workflow

The typed-order demonstration currently follows this workflow:

1. The user enters a Hindi/Hinglish order in the browser interface.
2. The browser sends the transcript to the FastAPI backend.
3. The backend passes the transcript to the order parser.
4. The LLM extracts products, quantities, and units.
5. Pydantic validates the structured response.
6. The backend builds a confirmation sentence.
7. Gnani Timbre generates the confirmation audio.
8. The browser displays the structured order and provides an audio player.

**Current status:** This typed-order workflow has been tested successfully, including order preview and generated audio.

The intended live voice workflow additionally requires microphone capture, speech recognition, and intelligent turn-taking. That complete workflow has not yet been verified.

## 5. Order Parsing and Corrections

The parser is designed to preserve quantities and units, normalize common unit variations, and avoid inventing products or quantities.

For example:

"Ek packet namak nahi, atta."

The intended interpretation is one packet of atta, not namak, provided the replacement is clear.

The parser also includes rules for:
- Replacing rejected products with corrected products.
- Handling repeated product entries.
- Normalizing units.
- Recognizing clear order cancellations.
- Requesting clarification when information is insufficient.

Because an LLM can still make mistakes, its outputs are evaluated against expected results using synthetic test cases.

## 6. Evaluation

We created a dataset of 40 synthetic grocery-order test cases.

The evaluation compares predicted items and clarification decisions against expected outputs. Repeated entries for the same product and unit are combined before item comparison.

**Latest recorded evaluation:**

- Total test cases: 40
- Passed: 40
- Failed: 0
- Unresolved API errors: 0

**Result: 40/40 passed on the current synthetic test set.**

The test set covers different ordering patterns, quantities, unit variations, corrections, repeated items, and cancellation cases.

This result demonstrates that the parser passed the current test cases. It should not be interpreted as a guarantee of 100% real-world accuracy.

## 7. Repository Structure

- `server/` — FastAPI backend, order parser, STT and TTS modules.
- `turntaking/` — Logic intended to distinguish acknowledgements from interruptions and corrections.
- `eval/` — Synthetic test data, evaluation scripts, and results.
- `web/` — Browser interface and client-side JavaScript.
- `docs/` — Project explanation, design notes, API documentation, and results.
- `requirements.txt` — Python dependencies.
- `.env` — Local API credentials; must never be committed to GitHub.

The FastAPI backend exposes the order-processing API and serves the browser interface.

## 8. Current Limitations

1. Streaming STT has not been successfully integrated because the Prisma WebSocket handshake timed out.
2. The current working demonstration accepts typed transcripts rather than completing a live microphone-to-order workflow.
3. Intelligent turn-taking and interruption handling are still pending.
4. The parser's 40/40 result comes from synthetic test cases and does not establish real-world accuracy.
5. More testing is needed with real customer speech, background noise, and corrections during spoken confirmation.

## 9. Next Development Priorities

1. Implement turn-taking rules and distinguish acknowledgements from genuine corrections.
2. Build and test the backchannel-versus-correction test set.
3. Implement simulated interruption handling, including user speech beginning while confirmation audio is playing.
4. Compare naive interruption handling with the smarter turn-taking approach.
5. Integrate live microphone functionality if the streaming blocker can be resolved without delaying the core demonstration.
6. Complete the evaluation, update the README, and prepare the final demonstration.

## 10. How to Explain the Project in an Interview

"Dukaan Saathi is a voice-first grocery-ordering assistant for local kirana stores. It is designed to let customers place orders naturally in Hindi or Hinglish. We use speech-to-text to obtain a transcript, an LLM-based parser to extract products and quantities into structured JSON, and text-to-speech to read the order back for confirmation. We have successfully tested file-based transcription, Hindi speech generation, and a 40-case synthetic parser evaluation. We also have a working typed-order demonstration. Our next focus is intelligent turn-taking, which will help the assistant distinguish between simple acknowledgements and actual corrections or interruptions."s