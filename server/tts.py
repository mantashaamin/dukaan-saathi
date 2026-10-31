
from dotenv import load_dotenv
from gnani.tts import GnaniTTSClient, AudioConfig

load_dotenv()


def synthesize_speech(text: str) -> bytes:
    """Convert the supplied text into Hindi speech and return MP3 bytes."""
    client = GnaniTTSClient()

    audio = client.synthesize(
        text,
        voice="Pranav",
        model="timbre-v2.5",
        language="hi-IN",
        speed=1.0,
        audio_config=AudioConfig(
            container="mp3",
            sample_rate=48000,
            bitrate="128k",
        ),
    )

    return audio


def main():
    text = (
        "Bhaiya, aapka order hai ek kilo chawal, "
        "do kilo aloo, aur paanch sau gram lehsun adrak. Sahi hai na?"
    )

    audio = synthesize_speech(text)
    output_path = "order-confirmation.mp3"

    with open(output_path, "wb") as audio_file:
        audio_file.write(audio)

    print(f"TTS successful. Audio saved to {output_path}")
    print(f"Audio size: {len(audio)} bytes")


if __name__ == "__main__":
    main()
