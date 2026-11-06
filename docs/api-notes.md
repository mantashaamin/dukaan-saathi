# Gnani API Notes — Dukaan Saathi

This document records the Gnani AI APIs used in Dukaan Saathi, their configuration, verified behaviour, integration status and outstanding technical questions.

Documentation and test results are distinguished so that documented capabilities are not confused with features verified in our application.

---

## 1. Prisma v2.5 — Speech-to-Text (STT)

**Official documentation:**

https://docs.gnani.ai/api/STT/stt-websocket

### 1.1 WebSocket Endpoint

- Protocol: WebSocket Secure (WSS)
- Endpoint: `wss://api.vachana.ai/stt/v3/stream`
- Purpose: Real-time speech recognition.

### 1.2 Authentication

- Required header: `x-api-key-id`
- API credentials must remain on the backend.
- Load credentials from environment variables.
- Never expose API keys in browser JavaScript.
- Never commit `.env` files or credentials to GitHub.

### 1.3 Audio Format

The documented streaming interface expects:

- Input: Raw PCM binary frames.
- Encoding: Signed 16-bit little-endian.
- Channels: Mono.
- Supported sample rates include 8000, 16000, 44100 and 48000 Hz.
- Documented frame size: 1024 bytes.
- Audio frames must be sent at real-time cadence.

### 1.4 Server Events

| Event | Description |
|---|---|
| `connected` | WebSocket connection established |
| `processing` | Speech segment captured for transcription |
| `transcript` | Completed transcript and metadata |
| `error` | Error information |

### 1.5 Project Relevance

Prisma converts the shopkeeper's spoken grocery requests into text.

The resulting transcript is used by the order parser to extract product names, quantities and units.

The transcript can also be passed to the turn-taking logic when evaluating customer acknowledgements and corrections.

### 1.6 Current Integration Status

- File-based transcription: Successfully tested.
- Browser microphone recording: Integrated into the application.
- Backend audio submission: Working.
- Prisma transcription in the deployed voice-order workflow: Working.
- Continuous WebSocket streaming: Not yet successfully integrated.
- Earlier streaming attempts established a connection and processed audio but returned zero transcript segments.
- A separate WebSocket attempt encountered a connection-handshake timeout.

**Important:** The current application uses recorded audio submitted to the backend. It does not currently claim continuous real-time Prisma streaming.

---

## 2. Prisma Python SDK

**Official documentation:**

https://docs.gnani.ai/api/STT/stt-websocket

### 2.1 Installation

- Package: `gnani-vachana`
- Installation:

```bash
pip install gnani-vachana
```

- Documented Python requirement: Python 3.10 or newer.
- Project environment: Python 3.11.

### 2.2 Python Interface

The documented streaming interface includes:

```python
from gnani.stt import GnaniSTTStreamClient
```

The SDK supports asynchronous streaming and can pace audio frames in real time.

Transcript events contain completed speech segments.

The file-based test used a separate client:

```python
GnaniSTTClient
```

### 2.3 Audio File Requirements

- The documented streaming example uses raw PCM audio.
- Do not assume a WAV file can be sent directly through the streaming interface.
- Verify encoding, sample rate and channel configuration before testing.
- Our file-based SDK test successfully accepted a WAV file.

### 2.4 Language Configuration

Documented language options include:

- `hi-IN`
- `en-IN`

The documentation also describes code-mixed speech examples.

Actual transcription quality for Hindi/Hinglish grocery orders must be evaluated using representative recordings.

### 2.5 Outstanding Measurements

- Streaming transcription latency.
- Time to first partial transcript.
- Actual streaming credit consumption.
- Hinglish grocery-order transcription accuracy.
- Performance across speakers and regional accents.

---

## 3. Timbre v2.5 — Text-to-Speech (TTS)

**Official SDK documentation:**

https://github.com/Gnani-AI-Mintlify/Gnani-Vachana

### 3.1 Python SDK

- Package: `gnani-vachana`
- SDK interfaces include:

```python
from gnani.tts import GnaniTTSStreamClient, AudioConfig
```

- API credentials are supplied from the backend environment.
- The API key must never be exposed in frontend JavaScript.

### 3.2 Streaming Options

**SSE Streaming**

- Endpoint: `https://api.vachana.ai/api/v1/tts/sse`
- Streams audio chunks using Server-Sent Events.
- SDK client: `GnaniTTSStreamClient`
- Useful for testing generated speech and measuring time to first audio.

**Realtime WebSocket**

- Endpoint: `wss://api.vachana.ai/api/v1/tts`
- Supports real-time audio streaming.
- SDK client: `GnaniTTSRealtimeClient`
- Intended for low-latency interactive speech.

### 3.3 Timbre v2.5 Settings

- Model: `timbre-v2.5`
- Documented language options include `hi-IN` and `en-IN`.
- A voice must be specified.
- Audio output format is configurable through `AudioConfig`.

### 3.4 Audio Output

The SDK documentation describes support for:

- WAV
- MP3
- Raw PCM
- OGG/Opus

For the initial test, we used:

- Format: MP3
- Sample rate: 48,000 Hz
- Bitrate: 128 kbps

The returned audio bytes were saved as an MP3 file and played successfully.

The SDK also provides `synthesize_stream()` for chunk-by-chunk synthesis.

The SDK README states Python 3.9 or newer; this project uses Python 3.11.

### 3.5 Project Relevance

Timbre generates spoken confirmations after the LLM extracts and validates the grocery order.

It is also used to communicate updated order details after a contextual correction.

### 3.6 Current Integration Status

- Hindi speech synthesis: Successfully tested.
- MP3 audio generation: Successfully tested.
- Browser audio playback: Successfully tested.
- Spoken order confirmation: Integrated into the application.
- Spoken confirmation after contextual correction: Integrated.
- Continuous low-latency WebSocket TTS: Not claimed as an implemented feature.

---

## 4. File-Based STT Test — 18 October 2026

**Status: Successful**

| Parameter | Result |
|---|---|
| SDK client | `GnaniSTTClient` |
| Model returned | `gnani-prisma-v2.5` |
| Language | `hi-IN` |
| Input | `kirana-test.wav` |
| Audio format | WAV |
| Channels | Mono |
| Sample rate | 16 kHz |
| Encoding | Signed 16-bit PCM |
| Result | `success: True` |
| Transcription | Hindi