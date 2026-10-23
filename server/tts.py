
from dotenv import load_dotenv
from gnani.tts import GnaniTTSClient, AudioConfig

load_dotenv()


def main():
    client = GnaniTTSClient()

    text = "Bhaiya, aapka order hai ek kilo chawal, do kilo aloo, aur paanch sau gram lehsun adrak. Sahi hai na?"

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

    output_path = "order-confirmation.mp3"

    with open(output_path, "wb") as audio_file:
        audio_file.write(audio)

    print(f"TTS successful. Audio saved to {output_path}")
    print(f"Audio size: {len(audio)} bytes")


if __name__ == "__main__":
    main()
