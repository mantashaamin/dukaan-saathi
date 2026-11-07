import json
from pathlib import Path

from datasets import load_dataset, Audio

OUTPUT = Path("data/indicvoices_30_samples")
OUTPUT.mkdir(parents=True, exist_ok=True)

ds = load_dataset(
    "ai4bharat/IndicVoices",
    "hindi",
    split="valid",
    streaming=True,
)

ds = ds.cast_column(
    "audio_filepath",
    Audio(decode=False),
)

seen_speakers = set()
saved = 0

print("Preparing 30 samples from different speakers...")

for sample in ds:
    if sample["scenario"] != "Conversation":
        continue

    speaker = sample["speaker_id"]

    if speaker in seen_speakers:
        continue

    audio = sample["audio_filepath"]
    audio_bytes = audio.get("bytes") if audio else None

    if not audio_bytes:
        continue

    name = f"conversation_{saved + 1:02d}"

    (OUTPUT / f"{name}.flac").write_bytes(audio_bytes)

    metadata = {
        "text": sample["text"],
        "duration": sample["duration"],
        "speaker_id": speaker,
        "scenario": sample["scenario"],
        "state": sample["state"],
        "district": sample["district"],
        "source": "ai4bharat/IndicVoices",
    }

    (OUTPUT / f"{name}.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    seen_speakers.add(speaker)
    saved += 1

    print(f"Saved {saved}/30 | Speaker: {speaker}")

    if saved == 30:
        break

print(f"\nCompleted: {saved}/30 samples saved.")

if saved < 30:
    print("Warning: Dataset did not provide 30 usable unique speakers.")