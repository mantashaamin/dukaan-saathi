# 🛒 Dukaan Saathi
### AI-Powered Voice Ordering Assistant for Indian Kirana Stores

Dukaan Saathi is an AI-powered grocery-ordering assistant designed to simplify order-taking at local Indian kirana stores.

It enables customers to place grocery orders using natural Hindi and Hinglish speech. The application converts spoken requests into structured grocery orders, validates product information, generates spoken confirmations, and supports contextual voice-based corrections.

Built as part of the **Great Indian AI Internship Challenge by Gnani AI**.

**Live Demo:** https://dukaan-saathi-q6lu.onrender.com  
**API Documentation:** https://dukaan-saathi-q6lu.onrender.com/docs  
**GitHub:** https://github.com/mantashaamin/dukaan-saathi

---

## 💡 Problem Statement

Traditional digital ordering systems often require customers to type product names, quantities, and units.

This can be inconvenient for customers and shopkeepers who are more comfortable communicating in Hindi or Hinglish.

Everyday kirana orders also contain informal product names, quantity variations, incomplete instructions, and corrections.

Dukaan Saathi explores how conversational AI and voice technologies can make this process more natural and accessible.

## ✨ Key Features

- **Hindi/Hinglish voice ordering:** Capture grocery requests through the browser microphone.
- **Speech recognition:** Convert recorded speech into text using Gnani AI Prisma.
- **Intelligent order parsing:** Extract product names, quantities, and units using an LLM.
- **Structured order generation:** Convert informal requests into structured JSON.
- **Order validation:** Validate extracted information using Pydantic.
- **Voice confirmations:** Generate spoken Hindi/Hinglish responses using Gnani AI Timbre.
- **Contextual corrections:** Modify existing orders using the previous order context.
- **Turn-taking classification:** Classify customer responses into `CONTINUE`, `STOP_AND_CORRECT`, and `ASK_AGAIN`.
- **Typed correction fallback:** Allow corrections through text when needed.

## 🧠 Example

**Customer voice input:**

"Bhaiya, ek kilo chawal, do kilo aloo aur 500 gram lehsun."

**Illustrative structured output:**

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

The application displays the structured order and generates a spoken confirmation using Gnani AI Timbre.

## 🏗️ System Architecture

The current recorded-audio workflow follows this pipeline:

```text
Customer Speaks in Hindi / Hinglish
                 |
                 v
       Browser Microphone
                 |
                 v
       Recorded Audio Input
                 |
                 v
          FastAPI Backend
                 |
                 v
       Gnani Prisma (STT)
                 |
                 v
       LLM-Based Order Parser
                 |
                 v
       Pydantic Validation
                 |
                 v
    Structured Order / Clarification
                 |
                 v
       Gnani Timbre (TTS)
                 |
                 v
       Spoken Confirmation
```

### Contextual Correction Workflow

```text
Existing Structured Order
          |
          v
Customer Triggers Correction
          |
          v
Correction Audio Recording
          |
          v
Gnani Prisma Transcription
          |
          v
LLM + Existing Order Context
          |
          v
Updated Structured Order
          |
          v
Gnani Timbre Confirmation
```

The turn-taking module classifies customer responses and supports correction and clarification decisions.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Speech-to-Text | Gnani AI Prisma v2.5 |
| Text-to-Speech | Gnani AI Timbre v2.5 |
| Language Understanding | Groq API – `openai/gpt-oss-20b` |
| Data Validation | Pydantic |
| Frontend | HTML, CSS, JavaScript |
| Audio Processing | Web Audio API |
| Testing | Pytest, synthetic evaluation datasets |
| Deployment | Render |

## 🤖 Gnani AI Integration

### Gnani AI Prisma – Speech-to-Text

Gnani Prisma v2.5 is integrated into the recorded-audio workflow.

The browser captures microphone audio, converts it into the required audio format, and sends it to the backend for transcription.

The transcription is then passed to the order-parsing pipeline.

### Gnani AI Timbre – Text-to-Speech

Gnani Timbre v2.5 converts generated Hindi/Hinglish order confirmations and correction responses into speech.

The generated audio is returned to the browser and played as part of the interaction.

**Integration distinction:** The current application uses recorded audio submissions. Continuous Prisma WebSocket streaming is not implemented.

## 📊 Evaluation and Testing

### Order Parser

Evaluated using 40 synthetic grocery-order test cases.

| Metric | Result |
|---|---:|
| Total test cases | 40 |
| Passed | 40 |
| Failed | 0 |
| Pass rate | 100% |

### Turn-Taking Classifier

| Evaluation | Result |
|---|---:|
| Synthetic development set | 90/90 (100%) |
| Initial holdout evaluation | 20/30 (66.67%) |
| Naive baseline on initial holdout | 10/30 (33.33%) |

The initial holdout results were subsequently used for diagnosis and tuning, so they should not be interpreted as an untouched final test result.

### Automated Tests

- 32 automated tests pass.
- Tests cover order processing, validation, and turn-taking behaviour.

### Speech Recognition Testing

Speech recognition was also evaluated separately using small audio test samples. Results varied across speakers and recording conditions, highlighting the need for more real-world Hindi/Hinglish audio evaluation.

**Note:** Synthetic text evaluation results do not represent production accuracy or real-world speech recognition accuracy.

## 📁 Project Structure

```text
dukaan-saathi/
│
├── docs/
│   ├── api-notes.md
│   ├── design.md
│   ├── project-explanation.md
│   └── results.md
│
├── eval/
│
├── server/
│
├── turntaking/
│
├── web/
│
├── Dukaan_Saathi_One_Page_Solution_Pitch.pdf
├── requirements.txt
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/mantashaamin/dukaan-saathi.git
cd dukaan-saathi
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

**macOS / Linux**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure the required API credentials.

```env
GNANI_API_KEY=your_gnani_api_key
GROQ_API_KEY=your_groq_api_key
```

Never commit your `.env` file or expose API credentials publicly.

### 5. Start the backend

```bash
uvicorn server.main:app --reload
```

Open the application at:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

Refer to the project documentation for additional setup and API details.

## ⚠️ Current Limitations

- Continuous real-time Prisma WebSocket streaming is not implemented.
- The application uses recorded audio submissions rather than continuous streaming.
- The correction microphone is manually triggered.
- Automatic interruption detection and real-time audio ducking are not implemented.
- Turn-taking classification requires further evaluation, particularly for ambiguous conversational responses.
- Evaluation datasets are primarily synthetic and require broader real-world testing.

## 🚀 Future Improvements

- Complete continuous speech integration using Gnani Prisma streaming.
- Improve conversational turn-taking and interruption handling.
- Expand testing with real-world Hindi and Hinglish speech.
- Improve robustness in noisy shop environments.
- Introduce grocery catalogue matching and inventory integration.
- Explore billing and order-management capabilities.

## 📚 Documentation

Detailed technical documentation is available in the [`docs/`](docs/) directory:

- [Project Explanation](docs/project-explanation.md)
- [Design Documentation](docs/design.md)
- [API Notes](docs/api-notes.md)
- [Evaluation Results](docs/results.md)

## 🎯 Project Objective

Dukaan Saathi explores how conversational AI, language understanding, and voice technologies can simplify everyday grocery ordering for local Indian retailers.

By combining speech recognition, intelligent order extraction, structured validation, and spoken interaction, the project aims to make digital ordering more accessible to India's neighbourhood kirana stores.

---

**Built by Mantasha Parween | Silicon University**

**Great Indian AI Internship Challenge by Gnani AI**
