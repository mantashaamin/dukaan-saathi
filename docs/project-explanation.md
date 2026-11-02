# Dukaan Saathi — Project Explanation

## 1. Project Overview

**Dukaan Saathi** is an AI-powered grocery-ordering assistant designed to simplify ordering at local Indian kirana stores using natural Hindi and Hinglish conversations.

Instead of requiring customers to manually type product names and quantities, the system aims to understand natural-language requests, extract structured order information and generate spoken confirmations.

### Example

A customer says:

"Bhaiya, ek kilo chawal, do kilo aloo aur 500 gram lehsun."

The system extracts a structured order:

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

The assistant then generates a confirmation response and converts it into audio using Gnani AI Timbre.

**Current status:** The project has a working typed-order demonstration with structured order parsing, contextual corrections, validation and generated Hindi voice responses. A conversational turn-taking classifier has also been implemented and evaluated. Live microphone-to-Prisma streaming remains incomplete.

## 2. Problem Statement

Many customers are comfortable communicating in Hindi or Hinglish but may find traditional text-based ordering interfaces inconvenient.

Kirana store orders frequently contain informal product names, different quantity formats, corrections and incomplete instructions. Processing these requests manually can become time-consuming and error-prone.

Dukaan Saathi aims to make grocery ordering more accessible by converting natural-language requests into structured order data that can be processed by software.

## 3. Core Technologies

### Gnani Prisma — Speech-to-Text (STT)

Speech-to-text converts spoken audio into written text.

**Purpose:** Convert customer speech into transcripts that can be processed by the order parser.

**Verified status:** File-based transcription using Gnani Prisma was tested successfully with a sample audio file. Streaming STT was also attempted, but the WebSocket connection handshake timed out. Live streaming integration is not currently working.

### LLM-Based Order Parser

A large language model interprets customer requests and converts them into structured order data.

**Implementation:** The Python module `server/order_parser.py` uses the Groq API with the `openai/gpt-oss-20b` model.

**Responsibilities:**
- Identify product names, quantities and units.
- Convert Hindi number words into numerical quantities.
- Normalize common unit variations.
- Handle product corrections and cancellations.
- Request clarification when customer intent is unclear.

### Pydantic — Data Validation

Pydantic validates the LLM-generated response against the expected data structure.

Each order item must contain:
- A product name.
- A positive quantity.
- A non-empty unit.

This catches malformed responses before the application processes them. However, structural validation does not guarantee that the model has correctly understood the customer's intention.

### Gnani Timbre — Text-to-Speech (TTS)

Text-to-speech converts written responses into audio.

**Purpose:** Generate spoken order confirmations and clarification responses.

**Verified status:** Hindi confirmation and clarification audio were generated successfully using Gnani AI Timbre and played through the browser interface.

### FastAPI — Backend

FastAPI handles communication between the frontend, order parser, validation layer and audio-generation functionality.

### HTML, CSS and JavaScript — Frontend

The browser interface allows users to enter order transcripts, view structured orders, submit corrections and listen to generated audio responses.

## 4. Current System Workflow

The current working demonstration follows this workflow:

1. The user enters a Hindi/Hinglish grocery order through the browser interface.
2. The frontend sends the transcript to the FastAPI backend.
3. The backend passes the transcript to the LLM-based order parser.
4. The LLM extracts products, quantities and units.
5. Pydantic validates the structured response.
6. The backend generates an order confirmation or clarification message.
7. Gnani AI Timbre converts the response into audio.
8. The browser displays the structured order and plays the generated audio.

The application also supports contextual order corrections through a separate correction endpoint.

**Current status:** Typed order processing, structured order preview, contextual correction and generated audio responses have been tested successfully.

The intended live voice workflow additionally requires microphone capture, streaming speech recognition and real-time conversational interaction. That complete workflow has not yet been verified.

## 5. Order Parsing and Contextual Corrections

The parser is designed to preserve quantities and units, normalize common unit variations and avoid inventing products or quantities.

### Example

Customer:

"Ek packet namak nahi, atta."

The intended interpretation is one packet of atta instead of namak, provided the replacement is clear.

The system supports:
- Replacing rejected products with corrected products.
- Handling repeated product entries.
- Normalizing common units.
- Recognizing clear order cancellations.
- Requesting clarification when information is insufficient.
- Applying corrections while preserving the existing order context.

Since LLM-generated outputs can still contain mistakes, the parser is evaluated against expected results using synthetic test cases.

## 6. Conversational Turn-Taking

A turn-taking classifier has been implemented to distinguish between different types of user responses during conversational interaction.

It classifies inputs into three actions:

### CONTINUE

Used when the user provides a simple acknowledgement or backchannel, such as:
- Haan
- Hmm
- Acha
- Ji
- Theek hai

### STOP_AND_CORRECT

Used when the user indicates that the current order or response needs correction.

Examples:
- "Ruko, aloo nahi, pyaz de do."
- "Nahi, quantity do kilo kar do."

### ASK_AGAIN

Used when the user's response is unclear or ambiguous and additional clarification is required.

This classification helps distinguish ordinary acknowledgements from genuine corrections and unclear responses.

**Current limitation:** The classifier has been tested using manually supplied synthetic text inputs. Automatic interruption detection during live audio playback and real-time audio ducking are not implemented.

## 7. Evaluation and Testing

The project uses separate synthetic datasets to evaluate order parsing and conversational turn-taking.

### 7.1 Order Parsing Evaluation

A dataset of 40 synthetic grocery-order test cases was created.

| Metric | Result |
|---|---:|
| Total test cases | 40 |
| Passed | 40 |
| Failed | 0 |
| Unresolved API errors | 0 |
| Pass rate | 100% |

The test cases cover:
- Different ordering patterns.
- Quantity extraction.
- Unit variations.
- Product corrections.
- Repeated product entries.
- Order cancellations.
- Clarification scenarios.

**Result:** 40/40 test cases passed on the current synthetic evaluation dataset.

This result demonstrates performance on the prepared test cases and should not be interpreted as guaranteed real-world accuracy.

### 7.2 Turn-Taking Evaluation

The turn-taking classifier was evaluated separately using synthetic development and independent holdout test cases.

| Evaluation | Correct classifications | Accuracy |
|---|---:|---:|
| Development set | 90/90 | 100% |
| Independent holdout set | 20/30 | 66.67% |
| Naive holdout baseline | 10/30 | 33.33% |

The holdout evaluation indicates that the classifier performs better than the naive baseline but still struggles with ambiguous conversational responses.

These results are based on synthetic text inputs and do not establish real-world voice-interaction accuracy.

## 8. Repository Structure

The project repository is organized into the following modules:

- `server/` — FastAPI backend, order parser, speech-to-text and text-to-speech modules.
- `turntaking/` — Conversational classification logic for acknowledgements, corrections and ambiguous responses.
- `eval/` — Synthetic test data, evaluation scripts and results.
- `web/` — Browser interface and client-side JavaScript.
- `docs/` — Project explanation, design notes, API documentation and evaluation results.
- `requirements.txt` — Python dependencies.
- `.env` — Local API credentials. This file must never be committed to GitHub.

## 9. Current Limitations

1. Live microphone-to-Prisma streaming has not been successfully integrated because the WebSocket handshake timed out.
2. The current working demonstration accepts typed transcripts instead of completing a live microphone-to-order workflow.
3. The turn-taking classifier has an independent synthetic holdout accuracy of 66.67%, indicating room for improvement.
4. Automatic interruption detection during live audio playback is not implemented.
5. Real-time audio ducking is not implemented.
6. Current evaluation is primarily based on synthetic test cases.
7. More testing is needed with real customer speech, background noise and corrections during spoken confirmation.

## 10. Future Development Priorities

1. Improve turn-taking classification, particularly for ambiguous conversational responses.
2. Expand evaluation datasets with more varied Hindi and Hinglish conversational examples.
3. Test the system with real-world customer speech and background noise.
4. Complete live microphone integration with Gnani Prisma if the streaming blocker can be resolved.
5. Implement real-time interruption detection and audio ducking.
6. Expand testing and improve the reliability of order parsing.
7. Complete the README, documentation and final demonstration.

## 11. How to Explain the Project in an Interview

"Dukaan Saathi is an AI-powered grocery-ordering assistant designed for local Indian kirana stores. It aims to let customers place orders naturally in Hindi or Hinglish.

We use an LLM-based parser to extract product names, quantities and units into structured JSON, Pydantic to validate the output, and Gnani AI Timbre to generate spoken order confirmations.

We have a working typed-order demonstration with contextual corrections and generated Hindi audio. We evaluated our parser on 40 synthetic test cases, achieving 40 out of 40 passes.

We also implemented a conversational turn-taking classifier that distinguishes acknowledgements, corrections and ambiguous responses. It achieved 66.67% accuracy on an independent synthetic holdout set.

Our next focus is improving conversational reliability and completing live microphone-to-Prisma integration."

---

**Project Name:** Dukaan Saathi  
**Challenge:** The Great Indian AI Internship Challenge  
**GitHub Repository:** https://github.com/mantashaamin/dukaan-saathi