# Dukaan Saathi — System Design and Technical Decisions

## 1. Project Overview

Dukaan Saathi is an AI-powered voice assistant designed for Indian kirana stores. It allows shopkeepers to place grocery orders naturally using Hindi and Hinglish.

The system converts spoken requests into structured grocery orders, validates the extracted information, and provides spoken confirmations.

A key technical challenge is conversational turn-taking: distinguishing between a customer's acknowledgement and an actual correction while an order is being read back.

The project uses Gnani AI's Prisma Speech-to-Text and Timbre Text-to-Speech services alongside an LLM-based order parser.

---

## 2. System Architecture

The application follows a client-server architecture.

### High-level workflow

1. The browser captures the user's voice through the microphone.
2. Audio is sent to the FastAPI backend.
3. Gnani Prisma converts speech into text.
4. The transcript is passed to the LLM-based order parser.
5. The parser extracts product names, quantities and units.
6. Pydantic validates the structured output.
7. The frontend displays the order.
8. Gnani Timbre generates a spoken confirmation.
9. If the user wants to correct an order, the correction is transcribed and processed using the existing order context.
10. The updated order is returned with a new spoken confirmation.

### Architecture diagram

```text
          Shopkeeper
              |
              v
       Browser Interface
        (Microphone)
              |
              v
         FastAPI Backend
              |
              v
        Gnani Prisma STT
              |
              v
        Speech Transcript
              |
              v
        LLM Order Parser
              |
              v
       Pydantic Validation
              |
              v
       Structured Order
              |
        +-----+------+
        |            |
        v            v
   Order Preview   Gnani Timbre
                   Text-to-Speech
                        |
                        v
                 Voice Confirmation
                        |
                        v
                 User Correction
                        |
                        v
                 Correction API
                        |
                        v
              Context-aware Parsing
                        |
                        v
                 Updated Order
```

---

## 3. Technology Choices

| Component | Technology | Purpose |
|---|---|---|
| Backend | Python, FastAPI | API endpoints and application logic |
| Speech-to-Text | Gnani Prisma | Converts Hindi/Hinglish speech into text |
| Text-to-Speech | Gnani Timbre | Generates spoken confirmations |
| Language Model | Groq-hosted LLM | Extracts structured grocery orders |
| Validation | Pydantic | Validates structured order data |
| Frontend | HTML, CSS, JavaScript | User interface and microphone interaction |
| Audio Processing | Web Audio API | Captures and processes microphone audio |
| Testing | Pytest | Automated testing |
| Deployment | Render | Hosts the application |

The backend handles API credentials and external service requests. Sensitive API keys are stored in environment variables rather than exposed to browser-side JavaScript.

---

## 4. Order Parsing Design

### Objective

Convert natural Hindi and Hinglish grocery-order requests into structured data that can be processed by the application.

### Example input

```text
Do kilo chawal, ek packet namak aur paanch Parle-G de do.
```

### Expected structured output

```json
{
  "items": [
    {
      "name": "chawal",
      "quantity": 2,
      "unit": "kg"
    },
    {
      "name": "namak",
      "quantity": 1,
      "unit": "packet"
    },
    {
      "name": "Parle-G",
      "quantity": 5,
      "unit": "packet"
    }
  ]
}
```

### Design decisions

- The LLM interprets natural-language grocery requests.
- Product names, quantities and units are extracted into structured fields.
- Pydantic validates the returned data.
- Common unit variations are normalized.
- Repeated product entries are handled during evaluation.
- Ambiguous requests can be flagged for clarification.
- Corrections are applied to the existing order instead of treating every correction as an entirely new order.

### Reliability

The parser was evaluated against 40 synthetic grocery-order examples. All 40 passed the prepared evaluation.

This result measures performance on the prepared dataset, not guaranteed accuracy on unseen real-world orders.

---

## 5. Turn-Taking Engine Design

### Problem

During spoken order confirmation, a customer may respond with:

- An acknowledgement: "Haan haan."
- A correction: "Ruko, namak nahi."
- An uncertain response: "Mujhe nahi pata."

A naive voice assistant may stop speaking whenever it detects customer speech. This can unnecessarily interrupt confirmations when the customer is simply acknowledging the order.

Dukaan Saathi uses a rule-based turn-taking engine to distinguish these situations.

### Three possible decisions

| Decision | Meaning | Intended action |
|---|---|---|
| CONTINUE | Customer acknowledgement | Continue the confirmation |
| STOP_AND_CORRECT | Customer wants to change something | Process the correction |
| ASK_AGAIN | Speech is ambiguous or unclear | Request clarification |

### Decision flow

```text
       Customer Transcript
                |
                v
       Transcript Normalization
                |
                v
         Feature Extraction
                |
                v
        Rule-based Classification
                |
        +-------+--------+
        |       |        |
        v       v        v
     CONTINUE  STOP    ASK_AGAIN
        |       |        |
        v       v        v
     Continue  Apply   Request
     Speech   Correction Clarification
```

### Why rule-based classification?

A rule-based approach was selected because:

- The number of clearly defined conversational categories is small.
- Common Hindi and Hinglish acknowledgement and correction expressions can be identified using phrase-based rules.
- The behaviour is interpretable and easy to debug.
- It avoids introducing an ML model before enough representative labelled audio data is available.

The current turn-taking engine should therefore be described as rule-based, not as a trained machine-learning classifier.

---

## 6. Hindi and Hinglish Transcript Normalization

Speech recognition may produce different written forms of the same conversational expression.

For example:

- अच्छा
- achha
- accha

These expressions may represent the same acknowledgement.

To handle such variations, the system normalizes transcripts before extracting features.

### Normalization steps

1. Convert text into a consistent case.
2. Remove unnecessary punctuation and extra whitespace.
3. Preserve meaningful Devanagari characters and combining marks.
4. Normalize frequently used Romanized Hindi variants.
5. Convert supported Hindi expressions into consistent normalized forms.

### Examples

| Original transcript | Normalized transcript |
|---|---|
| हाँ | haan |
| हाँ हाँ | haan haan |
| अच्छा | acha |
| achha | acha |
| accha | acha |
| ठीक है | theek hai |
| रुको ज़रा | ruko zara |
| मुझे नहीं पता | mujhe nahi pata |

A Unicode-aware cleanup approach is used so that Devanagari vowel signs and combining marks are not accidentally removed.

---

## 7. Feature Extraction and Classification Rules

The feature extraction module identifies useful characteristics of a transcript before classification.

The current implementation considers:

- Whether the transcript is empty.
- Whether it resembles a known backchannel.
- Whether it contains interruption or correction cues.
- Whether it represents an ambiguous expression.
- The normalized transcript.

### Backchannel examples

- haan
- haan haan
- acha
- theek hai
- haan bilkul
- haan sahi hai
- haan aage bolo
- जी बताइए

These expressions generally indicate acknowledgement or willingness to continue.

### Correction examples

- ruko zara
- ek minute
- cheeni mat daliye
- quantity aadhi kar do
- ek item aur add karna hai
- is order mein ek change hai

These expressions indicate a possible change to the current order.

### Ambiguous examples

- mujhe nahi pata
- pata nahi
- mujhe yaad nahi aa raha
- ek minute, sochne do

These expressions require contextual handling because they do not necessarily represent a direct order correction.

### Important design consideration

The classification rules must avoid treating every occurrence of words such as "nahi" or "minute" as a correction.

For example:

- "Cheeni mat daliye" is a correction.
- "Mujhe nahi pata" is ambiguous.
- "Ek minute, sochne do" is a request for time to think.

The rules therefore consider phrases and contextual exceptions rather than relying exclusively on individual keywords.

---

## 8. Context-aware Order Corrections

A correction should modify the existing order instead of creating an unrelated new order.

### Example

Original order:

```text
Do kilo chawal aur ek packet namak.
```

Customer correction:

```text
Namak nahi, cheeni kar do.
```

Expected updated order:

```json
{
  "items": [
    {
      "name": "chawal",
      "quantity": 2,
      "unit": "kg"
    },
    {
      "name": "cheeni",
      "quantity": 1,
      "unit": "packet"
    }
  ]
}
```

### Correction workflow

1. Receive the correction transcript.
2. Retrieve the existing order context.
3. Pass the transcript and existing order to the correction parser.
4. Generate the updated structured order.
5. Validate the updated order.
6. Return the updated order to the frontend.
7. Generate a new spoken confirmation through Timbre.

This preserves the relationship between the original order and the customer's correction.

---

## 9. API Design

The FastAPI backend exposes the following main endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Health check |
| `/api/order` | POST | Process an order transcript |
| `/api/voice-order` | POST | Process a voice order |
| `/api/transcribe` | POST | Transcribe correction audio |
| `/api/order/correct` | POST | Apply a correction to an existing order |

The correction workflow separates transcription from correction processing. This allows the application to transcribe a correction and then pass the resulting text to the order correction logic.

---

## 10. Testing Strategy

The project uses automated unit tests and synthetic evaluation datasets.

### Automated tests

Pytest is used to test:

- Transcript normalization.
- Hindi and Romanized Hindi variants.
- Backchannel recognition.
- Correction recognition.
- Ambiguous transcript handling.
- Empty transcript handling.
- Turn-taking classification.

### Evaluation datasets

Separate datasets are used for different evaluation purposes:

| Dataset | Purpose |
|---|---|
| Order parser dataset | Evaluate structured grocery-order extraction |
| Turn-taking development dataset | Develop and refine classification rules |
| Original holdout dataset | Preserve an earlier generalization baseline |
| Independent evaluation dataset | Examine behaviour on additional unseen-style examples |
| Audio datasets | Planned evaluation using real speech recordings |

Results from development datasets must not be presented as independent generalization performance.

---

## 11. Current Implementation Status

### Implemented

- FastAPI backend.
- Browser microphone capture.
- Gnani Prisma speech transcription.
- LLM-based grocery-order extraction.
- Pydantic order validation.
- Gnani Timbre spoken confirmation.
- Context-aware order corrections.
- Hindi and Hinglish transcript normalization.
- Rule-based turn-taking classification.
- Automated pytest coverage.
- Render deployment.

### Not yet implemented

- Continuous automatic interruption detection during assistant playback.
- Automatic real-time audio ducking.
- A complete streaming speech turn-taking loop.
- A trained ML-based turn-taking classifier.

The current correction workflow uses a separate user-triggered correction microphone. It should not be described as continuous automatic interruption detection.

---

## 12. Future Improvements

1. Evaluate the turn-taking engine using real Hindi and Hinglish speech recordings.
2. Introduce different speakers, speaking styles and background noise into audio evaluation.
3. Measure transcription errors and their effect on classification.
4. Improve contextual handling of short and ambiguous conversational expressions.
5. Explore automatic speech activity detection and real-time audio ducking.
6. Investigate a lightweight ML classifier if sufficient representative labelled data becomes available.
7. Improve order parsing for product aliases, regional expressions and complex quantity corrections.

---

## 13. Key Design Principle

Dukaan Saathi is designed around a simple but important principle:

**A voice assistant should understand not only what a customer says, but also whether the customer is agreeing, correcting, or asking for clarification.**

Reliable order extraction, contextual corrections and conversational turn-taking are therefore treated as connected parts of the same grocery-ordering experience.