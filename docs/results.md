
# Phase 0 — Initial Test Results

## 1. Prisma file-based STT
- Status: PASS
- Model: gnani-prisma-v2.5
- Language: hi-IN
- Input: kirana-test.wav
- Result: API returned success=True and a transcript.

## 2. Prisma streaming STT
- Status: NOT PASSING YET
- Connection: Successful
- Audio sending: Completed
- Processing event: Received
- Transcript segments: 0
- Next action: Investigate event delivery and streaming behavior.

## 3. Timbre TTS
- Status: PASS
- Model: timbre-v2.5
- Voice: Nalini
- Language: hi-IN
- Output: kirana-confirmation.mp3
- Playback: Confirmed; sounded clear and natural.


## Measurements and remaining work

- File-based STT cost: ₹0.06 for the recorded request.
- TTS cost: ₹0.16 for the recorded request.
- Total recorded usage: ₹0.22 across 2 billable requests.
- Streaming transcript latency: Not measured; streaming returned 0 transcript segments.
- Remaining: Investigate streaming STT event delivery.

