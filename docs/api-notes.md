
# Gnani API Notes

## 1. Prisma v2.5 — Speech-to-Text

Documentation:
https://docs.gnani.ai/api/STT/stt-websocket

### Endpoint
- Protocol: WebSocket Secure (WSS)
- URL: wss://api.vachana.ai/stt/v3/stream

### Authentication
- Required header: x-api-key-id
- The API key must remain on the backend.
- Load the key from an environment variable.
- Never commit secrets to Git.

### Audio format
- Input: raw PCM binary frames
- Encoding: signed 16-bit little-endian
- Channels: mono
- Supported sample rates include 8000, 16000, 44100 and 48000 Hz.
- Each binary frame: 1024 bytes.
- Frames must be sent at real-time cadence.

### Server events
- connected: connection established
- processing: speech segment captured for transcription
- transcript: completed transcript and metadata
- error: error information

### Project relevance
Prisma Realtime will receive the shopkeeper's live audio.
The backend will forward transcripts to the order parser
and turn-taking engine.

### Still to verify
- Python SDK installation and quick-start procedure
- Exact measured time to first partial/transcript
- Actual credit cost per call
- Supported language configuration for our Hinglish use case

## 2. Prisma Python SDK

Official documentation:
https://docs.gnani.ai/api/STT/stt-websocket

### Installation
- Package: `gnani-vachana`
- Install command: `pip install gnani-vachana`
- Requires Python 3.10 or newer.

### Python interface
- Import: `GnaniSTTStreamClient` from `gnani.stt`
- Supports asynchronous streaming.
- The SDK can pace audio frames in real time.
- Transcript events contain completed speech segments.

### Audio file requirement
- The documented file-streaming example uses raw PCM audio.
- Do not assume a WAV file can be sent directly.
- We must verify our test audio format before running the script.

### Hinglish language check
- The documentation lists `hi-IN` and `en-IN`.
- It also documents code-mixed examples, but we still need to test how accurately our Hinglish kirana orders are transcribed.

### Still to measure
- Actual transcription latency.
- Actual credit cost per call.
- Accuracy on Hinglish shop orders.

## 3. Timbre v2.5 — Text-to-Speech

Official SDK documentation:
https://github.com/Gnani-AI-Mintlify/Gnani-Vachana

### Python SDK
- Package: `gnani-vachana`
- Import: `GnaniTTSStreamClient` and `AudioConfig` from `gnani.tts`
- API key is passed to the client from the backend environment.

### Streaming options

**SSE streaming**
- Endpoint: `https://api.vachana.ai/api/v1/tts/sse`
- Streams audio chunks using Server-Sent Events.
- SDK client: `GnaniTTSStreamClient`
- Useful for testing generated speech and measuring time to first audio.

**Realtime WebSocket**
- Endpoint: `wss://api.vachana.ai/api/v1/tts`
- Supports realtime audio streaming.
- SDK client: `GnaniTTSRealtimeClient`
- Intended for low-latency interactive speech.

### Timbre v2.5 settings
- Model: `timbre-v2.5`
- Language options include `hi-IN` and `en-IN`.
- Voice is required.
- Audio output format is configurable through `AudioConfig`.

### Project relevance
Timbre will speak the order read-back to the customer.
We must measure time to first audio and actual credit cost.

### Still to verify
- Best voice and language settings for Hinglish orders.
- Actual audio playback format for our browser.
- Measured time to first audio chunk.
- Actual credit cost per call.

### Audio output — verified

- Timbre supports WAV, MP3, raw PCM and OGG/Opus.
- For the first test, use MP3 at 48,000 Hz and 128 kbps.
- Save the returned audio bytes as an `.mp3` file and play it to verify synthesis.
- The SDK also provides `synthesize_stream()` for chunk-by-chunk audio playback.
- The SDK README currently states Python 3.9+; this project will use Python 3.11 as required by the build guide.
- Do not expose the API key in browser JavaScript.

## File-based STT test — 18 October 2026

- Status: Successful
- SDK client: `GnaniSTTClient`
- Model returned: `gnani-prisma-v2.5`
- Language: `hi-IN`
- Input: `kirana-test.wav`
- Audio format: WAV, mono, 16 kHz, signed 16-bit PCM
- Result: API returned `success: True` and a transcript.
- Finding: The file-based SDK method rejects `.pcm` file extensions; WAV worked.
- Remaining issue: Streaming STT connected and processed audio but returned zero transcript segments.
- Cost per call: Not yet measured; check the Gnani dashboard.

## Timbre TTS test — 19 October 2026

- Status: Successful
- SDK client: `GnaniTTSClient`
- Model: `timbre-v2.5`
- Voice: `Nalini`
- Language: `hi-IN`
- Input: Hindi/Hinglish kirana order confirmation
- Output: `kirana-confirmation.mp3`
- Audio format: MP3, 48 kHz, 128 kbps
- Playback: Confirmed; speech sounded clear and natural to the listener.
- Cost per call: Not yet measured; check the Gnani dashboard.

## Actual API usage — 19 October 2026

Measured from the Gnani Usage dashboard:

| Service | Model | Usage | Cost |
|---|---|---|---|
| STT | prisma-v2.5 | 0.13 minutes | ₹0.06 |
| TTS | timbre-v2.5 | 57.0 characters | ₹0.16 |
| Total | — | 2 billable requests | ₹0.22 |

Notes:
- These are observed costs for these specific requests, not guaranteed costs for every request.
- The dashboard showed 4,999.72 credits remaining after these two recorded requests.
- Streaming STT attempts were not listed in this visible usage history; their individual costs remain unverified.

## Phase 0 — API Smoke Test Results

### Gnani Prisma STT
- Status: Successful using the file-based REST API
- Input: `kirana-test.wav`
- Language: `hi-IN`
- Model: `gnani-prisma-v2.5`
- Result: API returned `success: True` and a Hindi transcript
- Streaming STT: Pending investigation; returned zero transcript segments in our tests

### Gnani Timbre TTS
- Status: Successful using the REST API
- Model: `timbre-v2.5`
- Voice: `Pranav`
- Language: `hi-IN`
- Output: `order-confirmation.mp3`
- Format: MP3, 48 kHz, 128 kbps
- Playback: Confirmed; Hindi confirmation was audible and complete

### Remaining verification
- Measure actual credit cost for STT and TTS calls
- Verify streaming STT
