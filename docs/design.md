# Dukaan Saathi — System Design

## 1. Design Goals

The system was designed around five primary goals:

1. Make grocery ordering accessible through Hindi and Hinglish.
2. Convert informal requests into structured and validated order data.
3. Support corrections without losing the existing order context.
4. Generate natural spoken confirmations.
5. Distinguish acknowledgements from corrections and unclear responses.

## 2. Architecture

The application uses a browser-based frontend connected to a FastAPI backend.

### Component flow

```text
                 CUSTOMER
                    |
                    v
          Browser Interface
          /               \
    Microphone          Typed Input
         |                  |
         v                  |
    Audio Processing        |
    Mono PCM, 16 kHz        |
         |                  |
         v                  v
            FastAPI Backend
                    |
          +---------+----------+
          |                    |
          v                    v
      Gnani Prisma         Text Transcript
          |                    |
          +---------+----------+
                    |
                    v
             LLM Order Parser
               Groq API
                    |
                    v
            Pydantic Validation
                    |
          +---------+----------+
          |                    |
          v                    v
    Order Confirmation    Clarification
          |                    |
          +---------+----------+
                    |
                    v
               Gnani Timbre
                    |
                    v
             Browser Audio
                    |
                    v
             Order Preview
```

## 3. Backend Design

FastAPI coordinates the application components and exposes the HTTP endpoints.

### Main responsibilities

- Accept voice and text requests.
- Validate audio format and request payloads.
- Invoke Prisma transcription.
- Pass transcripts to the order parser.
- Validate structured model output.
- Preserve conversation state during corrections.
- Generate confirmation audio through Timbre.
- Return structured responses to the frontend.

## 4. Audio Processing Design

The browser microphone workflow prepares audio in a consistent format before sending it to the backend.

**Expected audio format:**

| Property | Value |
|---|---|
| Channels | Mono |
| Sample rate | 16,000 Hz |
| Encoding | Signed 16-bit PCM |

The backend validates the sample rate and checks the audio payload before transcription.

The transcription-only endpoint is separated from new-order processing so that correction speech can be transcribed without resetting the existing conversation state.

## 5. Order Parser Design

The order parser uses an LLM to convert conversational requests into structured data.

### Input

A Hindi/Hinglish transcript.

### Processing

1. Identify product references.
2. Extract quantities.
3. Extract units.
4. Normalize quantity and unit expressions.
5. Identify corrections or cancellations.
6. Determine whether clarification is necessary.
7. Return structured output.

### Validation

Pydantic checks the resulting structure before it is used by the application.

The parser is evaluated against a 40-case synthetic dataset.

## 6. Contextual Correction Design

A correction must be applied to the existing order rather than starting a new order.

### Correction workflow

```text
Existing Order
      |
      v
Customer Gives Correction
      |
      v
Transcribe Correction
      |
      v
Pass Existing Order Context
      |
      v
LLM Correction Parsing
      |
      v
Validate Updated Order
      |
      v
Generate Updated Confirmation
      |
      v
Play Confirmation Audio
```

The correction workflow supports a separate microphone control and a typed fallback.

This keeps correction processing separate from initial order creation.

## 7. Turn-Taking Engine Design

The turn-taking engine addresses a common voice-assistant problem: not every user utterance during a spoken response is an interruption.

For example:

- "Haan haan" is generally an acknowledgement.
- "Ruko, namak nahi, atta" indicates a correction.
- "Mujhe nahi pata" may require clarification.

### Three possible decisions

| Decision | Meaning | Intended action |
|---|---|---|
| CONTINUE | Acknowledgement | Preserve the current response |
| STOP_AND_CORRECT | Correction or interruption | Process the updated instruction |
| ASK_AGAIN | Unclear response | Ask the customer to repeat |

### Classification pipeline

```text
Customer Transcript
        |
        v
Text Normalization
        |
        v
Feature Extraction
        |
        v
Rule-Based Classification
        |
        +-------------------+
        |         |         |
        v         v         v
     CONTINUE   STOP       ASK_AGAIN
                AND
              CORRECT
```

### Feature and rule design

The implementation uses:

- Devanagari and Romanized Hindi/Hinglish normalization.
- Backchannel phrase recognition.
- Explicit interruption and correction cues.
- Contextual phrase matching.
- Speech-duration information.
- A conservative fallback for ambiguous responses.

The implementation is rule-based. It should not be described as a trained machine-learning classifier.

## 8. Conversation State Management

The backend uses a turn-taking state machine to track the interaction.

The relevant states include:

- IDLE — waiting for a new interaction.
- LISTENING — waiting for a customer response.
- SPEAKING — assistant confirmation is being generated or delivered.
- CORRECTING — applying an order correction.
- CONFIRMED — order confirmation completed.

The turn-taking engine is integrated with the backend correction workflow.

**Implementation boundary:** The application does not currently implement continuous voice activity detection that automatically detects interruptions and ducks the assistant's audio in real time. The correction microphone is user-triggered.

## 9. API Design

| Endpoint | Responsibility |
|---|---|
| `GET /health` | Verify backend availability |
| `POST /api/order` | Create a new order from text |
| `POST /api/voice-order` | Process a voice order |
| `POST /api/transcribe` | Transcribe audio without resetting order state |
| `POST /api/order/correct` | Apply a correction to an existing order |

The separation between transcription and order creation is intentional: correction audio should not accidentally create a new order.

## 10. Design Decisions

### Why FastAPI?

FastAPI provides a lightweight asynchronous backend and clear API contracts for the browser interface.

### Why an LLM-based parser?

Natural grocery requests contain variations in wording, product names, quantities and corrections. An LLM can interpret these expressions and return structured data.

### Why Pydantic?

LLM responses must be validated before being treated as application data. Pydantic provides a clear schema-validation layer.

### Why separate correction handling?

A correction modifies an existing order. Treating it as a new order risks losing previously selected items and quantities.

### Why a rule-based turn-taking classifier?

A compact rule-based implementation was chosen because its decisions can be inspected, tested and explained. It also allows targeted handling of common Hindi/Hinglish conversational phrases.

### Why separate transcription from order parsing?

Transcription and order interpretation are distinct responsibilities. Keeping them separate makes the API easier to test and prevents correction transcription from resetting conversation state.

## 11. Reliability and Error Handling

The backend checks:

- Missing API credentials.
- Empty audio payloads.
- Incorrect sample rates.
- Invalid PCM payload sizes.
- Oversized recordings.
- Transcription failures.
- Empty or unclear transcripts.
- Invalid order data.
- Invalid conversation-state transitions.

Errors are returned through HTTP responses rather than silently generating an order from invalid input.

## 12. Testing Strategy

The project uses several independent evaluation layers:

1. Synthetic order parser evaluation.
2. Synthetic turn-taking development evaluation.
3. Initial turn-taking holdout evaluation.
4. Regression testing after rule improvements.
5. IndicVoices audio transcription evaluation.
6. Automated pytest tests.
7. Manual testing of the deployed voice-order and correction workflow.

The datasets and results are maintained separately so that development performance is not confused with independent evaluation.

## 13. Known Design Limitations

- Rule-based turn-taking depends on the phrase coverage and normalization rules.
- Synthetic text tests cannot fully reproduce natural conversational behaviour.
- Prisma recognition varies across short utterances and different speakers.
- The current correction interaction is user-triggered rather than continuously detected.
- Automatic audio ducking and interruption detection remain future work.

## 14. Future Design Improvements

- Expand the independent Hindi/Hinglish test corpus.
- Evaluate more accents, speakers and background conditions.
- Improve recognition of short acknowledgements.
- Explore continuous voice activity detection.
- Add automatic interruption handling and audio ducking.
- Evaluate the complete workflow with more real-world recordings.