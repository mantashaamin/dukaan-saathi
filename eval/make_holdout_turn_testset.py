
import json
from pathlib import Path

HOLDOUT_CASES = [
    # BACKCHANNELS — expected CONTINUE
    {"transcript": "haan bilkul", "duration_seconds": 0.8, "expected": "continue", "category": "backchannel"},
    {"transcript": "ji ji", "duration_seconds": 0.7, "expected": "continue", "category": "backchannel"},
    {"transcript": "hmm haan", "duration_seconds": 0.8, "expected": "continue", "category": "backchannel"},
    {"transcript": "achha", "duration_seconds": 0.5, "expected": "continue", "category": "backchannel"},
    {"transcript": "haan sahi hai", "duration_seconds": 0.9, "expected": "continue", "category": "backchannel"},
    {"transcript": "हां जी", "duration_seconds": 0.7, "expected": "continue", "category": "backchannel"},
    {"transcript": "जी जी", "duration_seconds": 0.7, "expected": "continue", "category": "backchannel"},
    {"transcript": "हां बिल्कुल", "duration_seconds": 0.9, "expected": "continue", "category": "backchannel"},
    {"transcript": "हम्म हां", "duration_seconds": 0.8, "expected": "continue", "category": "backchannel"},
    {"transcript": "ठीक है जी", "duration_seconds": 0.9, "expected": "continue", "category": "backchannel"},

    # CORRECTIONS — expected STOP_AND_CORRECT
    {"transcript": "ek kaam karo, cheeni hata do", "duration_seconds": 1.4, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "aadha kilo ki jagah ek kilo likho", "duration_seconds": 1.5, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "rukna zara, tel do litre chahiye", "duration_seconds": 1.5, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "woh nahi, doosra wala", "duration_seconds": 1.3, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "चीनी मत डालिए", "duration_seconds": 1.2, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "एक पैकेट की जगह दो लिखिए", "duration_seconds": 1.5, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "रुकिए, तेल नहीं चाहिए", "duration_seconds": 1.3, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "quantity aadhi kar do", "duration_seconds": 1.3, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "bhai ek item aur add karna hai", "duration_seconds": 1.4, "expected": "stop_and_correct", "category": "correction"},
    {"transcript": "is order mein ek change hai", "duration_seconds": 1.4, "expected": "stop_and_correct", "category": "correction"},

    # AMBIGUOUS — expected ASK_AGAIN
    {"transcript": "woh... matlab", "duration_seconds": 0.7, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "abhi yaad nahi aa raha", "duration_seconds": 0.9, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "shayad woh wala", "duration_seconds": 0.8, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "kuch aur tha", "duration_seconds": 0.8, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "मुझे याद नहीं आ रहा", "duration_seconds": 0.9, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "वो कौन सा था", "duration_seconds": 0.8, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "शायद वही", "duration_seconds": 0.7, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "अभी सोचने दीजिए", "duration_seconds": 0.9, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "I am not sure", "duration_seconds": 0.8, "expected": "ask_again", "category": "ambiguous"},
    {"transcript": "umm, kaunsa item tha", "duration_seconds": 0.8, "expected": "ask_again", "category": "ambiguous"},
]


def main():
    output_path = Path(__file__).with_name("turn_test_cases_holdout.json")

    counts = {
        category: sum(
            case["category"] == category for case in HOLDOUT_CASES
        )
        for category in ("backchannel", "correction", "ambiguous")
    }

    assert len(HOLDOUT_CASES) == 30
    assert all(count == 10 for count in counts.values())

    output_path.write_text(
        json.dumps(HOLDOUT_CASES, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Created {len(HOLDOUT_CASES)} holdout cases.")
    for category, count in counts.items():
        print(f"{category}: {count}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
