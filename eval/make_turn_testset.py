
import json
from pathlib import Path

TEST_CASES = [
    # BACKCHANNELS — expected CONTINUE
    {"transcript": "haan", "duration_seconds": 0.4, "expected": "continue", "category": "backchannel"},
    {"transcript": "haan haan", "duration_seconds": 0.7, "expected": "continue", "category": "backchannel"},
    {"transcript": "हाँ", "duration_seconds": 0.4, "expected": "continue", "category": "backchannel"},
    {"transcript": "हाँहाँ", "duration_seconds": 0.6, "expected": "continue", "category": "backchannel"},
    {"transcript": "हम्म", "duration_seconds": 0.5, "expected": "continue", "category": "backchannel"},
    {"transcript": "अच्छा", "duration_seconds": 0.5, "expected": "continue", "category": "backchannel"},
    {"transcript": "जी", "duration_seconds": 0.4, "expected": "continue", "category": "backchannel"},
    {"transcript": "ठीक है", "duration_seconds": 0.8, "expected": "continue", "category": "backchannel"},
    {"transcript": "ओके", "duration_seconds": 0.5, "expected": "continue", "category": "backchannel"},
    {"transcript": "hmm", "duration_seconds": 0.5, "expected": "continue", "category": "backchannel"},

    # CORRECTIONS — expected STOP_AND_CORRECT
    {"transcript": "ruko", "duration_seconds": 0.5, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "nahi", "duration_seconds": 0.5, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "ek minute", "duration_seconds": 0.7, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "wait", "duration_seconds": 0.5, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "galat hai", "duration_seconds": 0.7, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "aloo nahi, pyaz de do", "duration_seconds": 1.5, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "namak ki jagah atta", "duration_seconds": 1.5, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "ek kilo nahi, do kilo", "duration_seconds": 1.5, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "रुको, नमक नहीं", "duration_seconds": 1.5, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "नहीं, प्याज दे दो", "duration_seconds": 1.5, "expected": "stop_and_correct", "category": "correction"},

    # AMBIGUOUS — expected ASK_AGAIN
    {"transcript": "", "duration_seconds": 0.0, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "umm", "duration_seconds": 0.4, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "uh", "duration_seconds": 0.5, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "शायद", "duration_seconds": 0.5, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "वो", "duration_seconds": 0.5, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "कुछ", "duration_seconds": 0.5, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "hmm maybe", "duration_seconds": 0.5, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "kya", "duration_seconds": 0.4, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "मतलब", "duration_seconds": 0.5, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "pata nahi", "duration_seconds": 0.7, "expected": "ask_again", "category": "ambiguous"},
]


def main():
    output_path = Path(__file__).with_name("turn_test_cases.json")

    output_path.write_text(
        json.dumps(TEST_CASES, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Created {len(TEST_CASES)} turn-taking test cases.")

    for category in ("backchannel", "correction", "ambiguous"):
        count = sum(case["category"] == category for case in TEST_CASES)
        print(f"{category}: {count}")


if __name__ == "__main__":
    main()
