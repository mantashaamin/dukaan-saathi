
import json
from pathlib import Path

import httpx
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly


# ============================================================
# CONFIGURATION
# ============================================================

SAMPLES_DIR = Path("data/indicvoices_30_samples")
API_URL = "http://127.0.0.1:8000/api/transcribe"

# Separate files: original 30-sample results stay untouched
OUTPUT_FILE = SAMPLES_DIR / "prisma_padding_experiment.json"
SUMMARY_FILE = SAMPLES_DIR / "padding_experiment_summary.json"

# Failed samples + successful control samples
SAMPLE_IDS = [1, 3, 4, 13, 24, 28]

SAMPLE_RATE = 16000
PADDING_SECONDS = 0.4


# ============================================================
# AUDIO PREPARATION
# ============================================================

def prepare_audio(audio_path):

    audio, original_rate = sf.read(
        audio_path,
        dtype="float32"
    )

    # Convert stereo to mono
    if audio.ndim == 2:
        audio = audio.mean(axis=1)

    # Resample to 16 kHz
    if original_rate != SAMPLE_RATE:
        audio = resample_poly(
            audio,
            SAMPLE_RATE,
            original_rate
        ).astype(np.float32)

    if len(audio) == 0:
        raise ValueError("Audio file is empty.")

    # Original audio diagnostics
    original_duration = len(audio) / SAMPLE_RATE
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio ** 2)))

    # Create 400 ms silence padding
    padding = np.zeros(
        int(PADDING_SECONDS * SAMPLE_RATE),
        dtype=np.float32
    )

    padded_audio = np.concatenate([
        padding,
        audio,
        padding
    ])

    # Convert to signed 16-bit PCM
    padded_audio = np.clip(
        padded_audio,
        -1.0,
        1.0
    )

    pcm_audio = (
        padded_audio * 32767
    ).astype(np.int16)

    return (
        pcm_audio.tobytes(),
        original_duration,
        peak,
        rms,
        len(padded_audio) / SAMPLE_RATE
    )


# ============================================================
# SAVE RESULTS
# ============================================================

def save_progress(results, failures):

    OUTPUT_FILE.write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    summary = {
        "experiment": "400ms silence padding",
        "padding_seconds_each_side": PADDING_SECONDS,
        "sample_ids": SAMPLE_IDS,
        "total_samples": len(SAMPLE_IDS),
        "successful": len(results),
        "failed": len(failures),
        "success_rate_percent": round(
            len(results) / len(SAMPLE_IDS) * 100,
            2
        ),
        "failures": failures
    }

    SUMMARY_FILE.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


# ============================================================
# MAIN EXPERIMENT
# ============================================================

def main():

    results = []
    failures = []

    print("=" * 60)
    print("GNANI PRISMA - SILENCE PADDING EXPERIMENT")
    print("=" * 60)

    print(f"\nSamples       : {SAMPLE_IDS}")
    print(f"Padding       : {PADDING_SECONDS * 1000:.0f} ms each side")
    print(f"Sample rate   : {SAMPLE_RATE} Hz")

    try:

        with httpx.Client(timeout=120.0) as client:

            # Check local API
            health = client.get(
                "http://127.0.0.1:8000/health"
            )

            health.raise_for_status()

            print("\nLocal API is reachable.")

            for index, sample_id in enumerate(
                SAMPLE_IDS,
                start=1
            ):

                name = f"conversation_{sample_id:02d}"

                audio_path = SAMPLES_DIR / f"{name}.flac"
                metadata_path = SAMPLES_DIR / f"{name}.json"

                print("\n" + "-" * 60)
                print(
                    f"PROCESSING SAMPLE {index}/{len(SAMPLE_IDS)} "
                    f"(Original ID: {sample_id})"
                )
                print("-" * 60)

                try:

                    metadata = json.loads(
                        metadata_path.read_text(
                            encoding="utf-8"
                        )
                    )

                    (
                        audio_bytes,
                        duration,
                        peak,
                        rms,
                        padded_duration
                    ) = prepare_audio(audio_path)

                    print(f"Speaker          : {metadata['speaker_id']}")
                    print(f"Original duration: {duration:.2f}s")
                    print(f"Padded duration  : {padded_duration:.2f}s")
                    print(f"Peak amplitude   : {peak:.4f}")
                    print(f"RMS amplitude    : {rms:.4f}")
                    print(f"Audio size       : {len(audio_bytes)} bytes")

                    print("\nSending padded audio to Prisma...")

                    response = client.post(
                        API_URL,
                        content=audio_bytes,
                        headers={
                            "x-audio-sample-rate": str(SAMPLE_RATE)
                        }
                    )

                    if response.status_code != 200:

                        try:
                            error_message = response.json().get(
                                "detail",
                                response.text
                            )
                        except ValueError:
                            error_message = response.text

                        failure = {
                            "sample": sample_id,
                            "speaker_id": metadata.get("speaker_id"),
                            "reference": metadata.get("text"),
                            "duration": duration,
                            "padded_duration": padded_duration,
                            "status_code": response.status_code,
                            "error": str(error_message)
                        }

                        failures.append(failure)

                        print("\nSTATUS: FAILED")
                        print("HTTP STATUS:", response.status_code)
                        print("ERROR:", error_message)

                    else:

                        predicted = response.json().get(
                            "transcript",
                            ""
                        ).strip()

                        if not predicted:
                            raise ValueError(
                                "Prisma returned an empty transcript."
                            )

                        result = {
                            "sample": sample_id,
                            "speaker_id": metadata["speaker_id"],
                            "reference": metadata["text"],
                            "predicted": predicted,
                            "duration": duration,
                            "padded_duration": padded_duration,
                            "state": metadata.get("state"),
                            "district": metadata.get("district"),
                            "status": "success"
                        }

                        results.append(result)

                        print("\nREFERENCE:", result["reference"])
                        print("PRISMA   :", predicted)
                        print("STATUS   : SUCCESS")

                except Exception as exc:

                    failures.append({
                        "sample": sample_id,
                        "error": str(exc)
                    })

                    print("\nSTATUS: FAILED")
                    print("ERROR:", exc)

                # Save after each sample
                save_progress(results, failures)

                print(
                    f"\nProgress: {index}/{len(SAMPLE_IDS)} | "
                    f"Successful: {len(results)} | "
                    f"Failed: {len(failures)}"
                )

    except Exception as exc:

        print("\nAPI CONNECTION ERROR:", exc)
        return

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    success_rate = round(
        len(results) / len(SAMPLE_IDS) * 100,
        2
    )

    print("\n" + "=" * 60)
    print("PADDING EXPERIMENT SUMMARY")
    print("=" * 60)

    print("Total samples :", len(SAMPLE_IDS))
    print("Successful    :", len(results))
    print("Failed        :", len(failures))
    print("Success rate  :", f"{success_rate}%")

    print("\nResults saved :", OUTPUT_FILE)
    print("Summary saved :", SUMMARY_FILE)

    print("\nExperiment completed.")


if __name__ == "__main__":
    main()
