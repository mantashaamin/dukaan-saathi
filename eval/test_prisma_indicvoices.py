
import json
from pathlib import Path

import httpx
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly


# Configuration
SAMPLES_DIR = Path("data/indicvoices_samples")
API_URL = "http://127.0.0.1:8000/api/transcribe"
OUTPUT_PATH = SAMPLES_DIR / "prisma_evaluation.json"

SAMPLE_COUNT = 5
TIMEOUT = 120.0



def prepare_audio(audio_path: Path) -> bytes:
    """Convert audio to mono 16 kHz PCM and add trailing silence."""

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    audio, sample_rate = sf.read(
        str(audio_path),
        dtype="float32",
        always_2d=True,
    )

    # Convert to mono
    audio = audio.mean(axis=1)

    # Resample to 16 kHz
    if sample_rate != 16000:
        audio = resample_poly(audio, 16000, sample_rate)

    audio = np.nan_to_num(audio)
    audio = np.clip(audio, -1.0, 1.0)

    # Inspect audio levels
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio ** 2)))

    print(f"Original sample rate: {sample_rate}")
    print(f"Peak amplitude: {peak:.4f}")
    print(f"RMS amplitude: {rms:.4f}")

    # Add 800 ms trailing silence
    silence = np.zeros(int(16000 * 0.8), dtype=np.float32)
    audio = np.concatenate([audio, silence])

    # Convert to signed 16-bit PCM
    pcm_audio = (audio * 32767).astype(np.int16)

    return pcm_audio.tobytes()

      


def evaluate_sample(client: httpx.Client, sample_number: int) -> dict:
    audio_path = SAMPLES_DIR / f"conversation_{sample_number:02d}.flac"
    metadata_path = SAMPLES_DIR / f"conversation_{sample_number:02d}.json"

    print(f"\n--- PROCESSING SAMPLE {sample_number} ---")

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {metadata_path}"
        )

    metadata = json.loads(
        metadata_path.read_text(encoding="utf-8")
    )

    audio_bytes = prepare_audio(audio_path)

    print(f"Audio size: {len(audio_bytes)} bytes")
    print("Sending audio to local Prisma endpoint...")

    response = client.post(
        API_URL,
        content=audio_bytes,
        headers={
            "x-audio-sample-rate": "16000",
            "Content-Type": "application/octet-stream",
        },
    )

    if response.status_code != 200:
        error = response.text

        print(f"FAILED: HTTP {response.status_code}")
        print("Error:", error)

        return {
            "sample": sample_number,
            "status": "failed",
            "reference": metadata.get("text", ""),
            "predicted": None,
            "duration": metadata.get("duration"),
            "error": error,
        }

    response_data = response.json()
    predicted = response_data.get("transcript", "").strip()

    if not predicted:
        print("FAILED: Empty transcript returned.")

        return {
            "sample": sample_number,
            "status": "failed",
            "reference": metadata.get("text", ""),
            "predicted": None,
            "duration": metadata.get("duration"),
            "error": "Empty transcript returned.",
        }

    result = {
        "sample": sample_number,
        "status": "success",
        "reference": metadata["text"],
        "predicted": predicted,
        "duration": metadata["duration"],
        "speaker_id": metadata.get("speaker_id"),
    }

    print("REFERENCE:", result["reference"])
    print("PRISMA   :", result["predicted"])
    print("STATUS   : SUCCESS")

    return result


def main():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    successful = 0
    failed = 0

    print("=" * 50)
    print("INDICVOICES - GNANI PRISMA EVALUATION")
    print("=" * 50)

    try:
        with httpx.Client(timeout=TIMEOUT) as client:

            # Verify that the local server is reachable
            try:
                response = client.get(
                    "http://127.0.0.1:8000/health",
                    timeout=10.0,
                )
                response.raise_for_status()
                print("\nLocal API is reachable.")

            except httpx.HTTPError as exc:
                print("\nERROR: Local FastAPI server is unavailable.")
                print("Start your server before running evaluation.")
                print("Details:", exc)
                return

            for i in range(1, SAMPLE_COUNT + 1):
                try:
                    result = evaluate_sample(client, i)
                    results.append(result)

                    if result["status"] == "success":
                        successful += 1
                    else:
                        failed += 1

                except Exception as exc:
                    failed += 1

                    print(f"\n--- SAMPLE {i} ERROR ---")
                    print(type(exc).__name__, ":", exc)

                    results.append({
                        "sample": i,
                        "status": "failed",
                        "reference": None,
                        "predicted": None,
                        "duration": None,
                        "error": str(exc),
                    })

    except Exception as exc:
        print("\nEvaluation stopped:", exc)

    # Save all results, including failures
    OUTPUT_PATH.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Total samples : {len(results)}")
    print(f"Successful    : {successful}")
    print(f"Failed        : {failed}")

    if results:
        print(
            f"Transcription success rate: "
            f"{successful / len(results) * 100:.2f}%"
        )

    print(f"\nResults saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
