
import os
import subprocess

from dotenv import load_dotenv
from gnani.stt import GnaniSTTClient
from server.tts import synthesize_speech

load_dotenv()

api_key = os.getenv("GNANI_API_KEY")
if not api_key:
    raise RuntimeError("GNANI_API_KEY is missing from .env")

# Step 1: Generate a short backchannel audio clip using Timbre.
audio = synthesize_speech("Haan haan.")

with open("haan-haan.mp3", "wb") as audio_file:
    audio_file.write(audio)

print("Timbre audio generated successfully.")

# Step 2: Convert the audio to mono, 16 kHz WAV for STT.
subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-i", "haan-haan.mp3",
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        "haan-haan.wav",
    ],
    check=True,
    capture_output=True,
)

print("Audio converted to WAV.")

# Step 3: Transcribe using the existing file-based Prisma client.
client = GnaniSTTClient(api_key=api_key)

result = client.transcribe(
    "haan-haan.wav",
    language_code="hi-IN",
    format="verbatim",
)

# Step 4: Inspect the exact API response.
print("\nRaw Prisma response:")
print(repr(result))
