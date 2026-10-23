
import asyncio
import os

from dotenv import load_dotenv
from gnani.stt import GnaniSTTStreamClient

load_dotenv()


async def main():
    audio_path = "kirana-test-silence.pcm"
    if not os.getenv("GNANI_API_KEY"):
        raise RuntimeError(
            "GNANI_API_KEY is missing. Check your root .env file."
        )

    if not os.path.exists(audio_path):
        raise FileNotFoundError(
            f"{audio_path} not found. Run this script from the project root."
        )

    print("Connecting to Gnani Prisma...")

    async with GnaniSTTStreamClient(
        language_code="hi-IN",
        sample_rate=16000,
    ) as stream:
        print("Connected. Sending your recording...")
        print("Prisma connection config:")
        print(stream.connected_config)
        print("Configured sample rate:", stream.connected_config.sample_rate)
        print("Configured chunk size:", stream.connected_config.chunk_size)
        print("PCM file size:", os.path.getsize(audio_path))        
        def on_transcript(event):
            print(f"Transcript: {event.text}")
            print(f"Audio duration: {event.audio_duration_ms} ms")
            print(f"Latency: {event.latency} ms")

        def on_processing(event):
            print(f"Prisma processing event: {event!r}")

        with open(audio_path, "rb") as audio_file:
            transcripts = await stream.stream_audio(
                audio_file,
                on_transcript=on_transcript,
                on_processing=on_processing,
                realtime_pace=True,
            )
            print("Returned transcript events:")
            for event in transcripts:
                print(repr(event))

        print(f"Total transcript segments: {len(transcripts)}")

if __name__ == "__main__":
    asyncio.run(main())

