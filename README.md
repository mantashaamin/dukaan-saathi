# 🛒 Dukaan Saathi
### AI-Powered Grocery Ordering Assistant for Indian Kirana Stores

Dukaan Saathi is an AI-powered grocery-ordering assistant designed to simplify ordering at local Indian kirana stores. It aims to understand natural Hindi and Hinglish requests, convert them into structured grocery orders, handle contextual corrections, and generate spoken confirmations using Gnani AI Timbre.

Built as part of the **Great Indian AI Internship Challenge by Gnani AI**.

---

## 💡 Problem Statement

Traditional digital ordering systems often require customers to type product names and quantities. This can be inconvenient for customers who are more comfortable communicating in Hindi or Hinglish.

Kirana orders also frequently contain informal product names, quantity variations, incomplete instructions and corrections.

Dukaan Saathi explores how conversational AI can make this ordering process more natural and accessible.

## ✨ Features

- **Natural-language order parsing:** Extracts product names, quantities and units from Hindi/Hinglish requests.
- **Structured order generation:** Converts informal requests into structured JSON.
- **Contextual corrections:** Supports modifying existing orders without restarting the entire process.
- **Order validation:** Uses Pydantic to validate structured order data.
- **Voice responses:** Uses Gnani AI Timbre to generate spoken Hindi confirmations and clarification messages.
- **Conversational turn-taking:** Classifies responses into CONTINUE, STOP_AND_CORRECT and ASK_AGAIN.
- **Clarification handling:** Requests additional information when an order is unclear.

## 🧠 Example

**Customer input:**

"Bhaiya, ek kilo chawal, do kilo aloo aur 500 gram lehsun."

**Structured output:**

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

The system generates a confirmation message and converts it into audio using Gnani AI Timbre.

## 🏗️ Architecture

The current working demonstration follows this pipeline:

```text
Customer enters Hindi/Hinglish order
              |
              v
       Browser Interface
              |
              v
         FastAPI Backend
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
       Gnani AI Timbre
              |
              v
      Generated Audio Response
```

The conversational turn-taking module separately classifies user responses and supports correction and clarification workflows.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Language understanding | Groq API, openai/gpt-oss-20b |
| Data validation | Pydantic |
| Speech-to-text exploration | Gnani AI Prisma |
| Text-to-speech | Gnani AI Timbre |
| Frontend | HTML, CSS, JavaScript |
| Testing | Python, synthetic evaluation datasets |

## 🤖 Gnani AI Integration

### Gnani AI Timbre — Text-to-Speech

Integrated to convert generated Hindi confirmation and clarification messages into audio.

The integration has been tested successfully in the working browser demonstration.

### Gnani AI Prisma — Speech-to-Text

File-based transcription was tested successfully using a sample audio file.

Live streaming integration was attempted, but the WebSocket handshake timed out. Therefore, live microphone-to-Prisma streaming is not currently available in the working demonstration.

## 📊 Evaluation Results

### Order Parser

Evaluated using 40 synthetic grocery-order test cases.

| Metric | Result |
|---|---:|
| Total test cases | 40 |
| Passed | 40 |
| Failed | 0 |
| Unresolved API errors | 0 |
| Pass rate | 100% |

### Turn-Taking Classifier

Evaluated using synthetic development and independent holdout datasets.

| Evaluation | Result |
|---|---:|
| Development set | 90/90 (100%) |
| Independent holdout set | 20/30 (66.67%) |
| Naive holdout baseline | 10/30 (33.33%) |

The holdout results indicate that ambiguous conversational responses remain an area for improvement.

*These results are based on synthetic text test cases and do not represent real-world speech recognition accuracy.*

## 📁 Project Structure

```text
dukaan-saathi/
│
├── server/
│   ├── main.py
│   └── order_parser.py
│
├── turntaking/
│
├── eval/
│
├── web/
│   └── index.html
│
├── docs/
│   ├── api-notes.md
│   ├── design.md
│   ├── project-explanation.md
│   └── results.md
│
├── requirements.txt
├── .gitignore
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

The backend runs at:

`http://127.0.0.1:8000`

### 6. Start the frontend

Open another terminal:

```bash
cd web
python -m http.server 5501
```

Open the application:

`http://localhost:5501`

## ⚠️ Current Limitations

- The working demonstration accepts typed transcripts rather than live microphone input.
- Live microphone-to-Prisma streaming is incomplete.
- Automatic real-time interruption detection is not implemented.
- Real-time audio ducking is not implemented.
- Turn-taking classification needs improvement, particularly for ambiguous inputs.
- Evaluation is primarily based on synthetic test cases.

## 🚀 Future Improvements

- Complete live microphone integration using Gnani AI Prisma.
- Improve conversational turn-taking and interruption handling.
- Expand testing with real-world Hindi and Hinglish speech.
- Improve robustness in noisy environments.
- Develop a more complete grocery-order management workflow.

## 📚 Documentation

Detailed project documentation is available in the [`docs/`](docs/) directory:

- [Project Explanation](docs/project-explanation.md)
- [Design Documentation](docs/design.md)
- [API Notes](docs/api-notes.md)
- [Evaluation Results](docs/results.md)

## 🎯 Project Objective

Dukaan Saathi explores how conversational AI and voice technologies can simplify everyday grocery ordering for local Indian retailers.

By combining language understanding, structured data processing and voice-based interaction, the project aims to make digital ordering more accessible to small businesses.

---

**Built for the Great Indian AI Internship Challenge by Gnani AI.**

GitHub: https://github.com/mantashaamin/dukaan-saathi