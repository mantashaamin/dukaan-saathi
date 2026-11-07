# Dukaan Saathi — Project Explanation

## 1. Project Overview

**Dukaan Saathi** is an AI-powered voice assistant designed to make grocery ordering easier for local Indian kirana stores.

It allows users to communicate naturally in Hindi and Hinglish, converts their requests into structured grocery orders, and generates spoken confirmations.

The project was developed as part of the **Great Indian AI Internship Challenge by Gnani AI**.

**Live Application:** https://dukaan-saathi-q6lu.onrender.com  
**GitHub Repository:** https://github.com/mantashaamin/dukaan-saathi  
**API Documentation:** https://dukaan-saathi-q6lu.onrender.com/docs

## 2. Problem Statement

Traditional digital ordering systems often require customers to type product names, quantities and other details manually.

For many local grocery stores, customers are more comfortable communicating through natural conversation.

However, conversational orders introduce challenges:

- Informal Hindi and Hinglish expressions.
- Different ways of expressing quantities.
- Repeated products and corrections.
- Incomplete or ambiguous instructions.
- The need to confirm orders verbally.

Dukaan Saathi addresses these challenges by combining speech processing, language models, structured validation and speech generation.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| FastAPI | Backend API |
| Groq API | LLM inference |
| GPT-OSS-20B | Structured order extraction |
| Gnani Prisma | Speech-to-text |
| Gnani Timbre | Hindi text-to-speech |
| Pydantic | Structured data validation |
| HTML, CSS, JavaScript | Browser interface |
| Web Audio API | Microphone audio capture and processing |
| Pytest | Automated testing |
| Render | Application deployment |

## 4. System Architecture

The application follows a browser-to-backend architecture.

### Main workflow

1. The browser captures the customer's voice.
2. Audio is converted into mono, signed 16-bit PCM at 16 kHz.
3. The backend sends the audio to Gnani Prisma for transcription.
4. The resulting Hindi/Hinglish transcript is passed to the LLM order parser.
5. The parser extracts product names, quantities and units.
6. Pydantic validates the structured order.
7. The backend generates a confirmation or clarification message.
8. Gnani Timbre generates Hindi speech.
9. The browser displays the structured order and plays the generated response.

### Architecture summary

Browser microphone → FastAPI → Gnani Prisma → LLM parser → Pydantic validation → Gnani Timbre → Browser audio and order preview.

## 5. Major Components

### 5.1 Gnani Prisma — Speech-to-Text

Prisma converts customer audio into text.

The backend supports audio transcription through the `/api/transcribe` and `/api/voice-order` workflows.

Audio is prepared in the expected mono 16 kHz PCM format.

Transcription quality is dependent on recording duration, clarity and speaker variation.

### 5.2 LLM-Based Order Parser

The parser is implemented in `server/order_parser.py`.

It uses Groq inference with `openai/gpt-oss-20b` to interpret Hindi/Hinglish requests.

Its responsibilities include:

- Extracting grocery product names.
- Identifying quantities and units.
- Understanding Hindi number words.
- Normalizing common unit variations.
- Handling corrections and cancellations.
- Requesting clarification when required.

Example request:

"Bhaiya, ek kilo chawal, do kilo aloo aur 500 gram lehsun."

Example structured output:

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

### 5.3 Pydantic — Validation

Pydantic validates the LLM response before the application uses it.

It checks the expected structure and required fields, helping prevent malformed model output from being treated as a valid order.

### 5.4 Gnani Timbre — Text-to-Speech

Timbre converts generated confirmation messages into spoken Hindi audio.

It is used for order read-backs and clarification responses.

### 5.5 Contextual Correction System

Customers may change an order after the initial request.

For example:

"Ek kilo namak nahi, atta kar do."

The correction workflow preserves the existing order context instead of treating the correction as an entirely new order.

The application supports a separate correction microphone and a typed correction fallback.

### 5.6 Turn-Taking Engine

The turn-taking engine classifies customer responses into three actions:

| Action | Meaning |
|---|---|
| CONTINUE | Recognized acknowledgement; preserve the existing response |
| STOP_AND_CORRECT | A correction or interruption needs processing |
| ASK_AGAIN | The response is unclear and needs clarification |

The classifier uses Hindi/Hinglish normalization, phrase matching and contextual rules.

It is integrated into the backend correction workflow.

**Current scope:** The classifier is implemented and tested, but continuous automatic interruption detection and real-time audio ducking are not implemented.

## 6. API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Health check |
| `/api/order` | POST | Process a text transcript into an order |
| `/api/voice-order` | POST | Process microphone audio as a voice order |
| `/api/transcribe` | POST | Transcribe audio without creating a new order |
| `/api/order/correct` | POST | Apply a contextual order correction |

Interactive API documentation is available at `/docs`.

## 7. Evaluation Summary

### Order parsing

- 40 synthetic test cases.
- 40 passed.
- 100% pass rate on the prepared dataset.

### Turn-taking

- 90/90 synthetic development examples passed.
- Initial independent holdout baseline: 66.67%.
- Final regression set: 30/30 after rule improvements.
- 32 automated tests passed.

The final regression set reuses examples that informed debugging and must not be described as independent test performance.

### Speech recognition

- Five-sample initial evaluation: 5/5 successful.
- Five-sample WER: 11.32%.
- Separate 30-speaker evaluation: 6/30 successful.
- Six-sample silence-padding experiment: 2/6 successful.

See `results.md` for detailed metrics and limitations.

## 8. Repository Structure

```text
dukaan-saathi/
├── server/
│   ├── main.py
│   ├── order_parser.py
│   └── ...
├── turntaking/
│   ├── classifier.py
│   ├── features.py
│   ├── rules.py
│   └── test_normalization.py
├── eval/
│   ├── test_orders.json
│   ├── run_eval.py
│   ├── run_turn_eval.py
│   ├── run_holdout_turn_eval.py
│   └── results/
├── web/
│   └── index.html
├── docs/
│   ├── project-explanation.md
│   ├── design.md
│   └── results.md
├── requirements.txt
├── README.md
└── .gitignore
```

## 9. Running the Application

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local `.env` file with the required API credentials:

```env
GNANI_API_KEY=your_gnani_api_key
GROQ_API_KEY=your_groq_api_key
```

Start the FastAPI server:

```bash
uvicorn server.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Never commit `.env` or private API credentials.

## 10. Current Limitations

- Prisma transcription performance varies significantly across short recordings and speakers.
- The initial holdout turn-taking evaluation exposed generalization gaps.
- The final regression result does not establish independent real-world accuracy.
- Continuous automatic interruption detection is not implemented.
- Real-time audio ducking is not implemented.
- More diverse real-world audio evaluation is needed.

## 11. Conclusion

Dukaan Saathi demonstrates how speech technology, LLM-based extraction and structured validation can work together to simplify grocery ordering in Hindi and Hinglish.

The project combines a working voice-order workflow, contextual corrections, generated spoken confirmations and a rule-based turn-taking component.

It also documents the limitations identified during testing, providing a clear foundation for future improvements.