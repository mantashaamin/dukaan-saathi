import json
from pathlib import Path
from collections import defaultdict

from turntaking.classifier import turn_classifier


def main():
    eval_dir = Path(__file__).parent

    test_path = eval_dir / "turn_test_cases_expanded.json"
    output_path = eval_dir / "results" / "turntaking_eval_expanded.json"

    with open(test_path, "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    results = []
    category_stats = defaultdict(lambda: {"total": 0, "passed": 0})

    naive_correct = 0
    smart_correct = 0
    naive_backchannel_interruptions = 0
    smart_backchannel_interruptions = 0
    naive_missed_corrections = 0
    smart_missed_corrections = 0

    for case in test_cases:
        transcript = case["transcript"]
        duration = case["duration_seconds"]
        expected = case["expected"]
        category = case["category"]

        smart_prediction = turn_classifier.classify(
            transcript, duration
        ).value

        # Naive baseline: stop whenever speech is detected.
        naive_prediction = (
            "stop_and_correct" if transcript.strip() else "ask_again"
        )

        smart_passed = smart_prediction == expected
        naive_passed = naive_prediction == expected

        smart_correct += smart_passed
        naive_correct += naive_passed

        category_stats[category]["total"] += 1
        category_stats[category]["passed"] += smart_passed

        if category == "backchannel":
            naive_backchannel_interruptions += (
                naive_prediction != "continue"
            )
            smart_backchannel_interruptions += (
                smart_prediction != "continue"
            )

        if category == "correction":
            naive_missed_corrections += (
                naive_prediction != "stop_and_correct"
            )
            smart_missed_corrections += (
                smart_prediction != "stop_and_correct"
            )

        results.append({
            "transcript": transcript,
            "duration_seconds": duration,
            "category": category,
            "expected": expected,
            "naive_prediction": naive_prediction,
            "smart_prediction": smart_prediction,
            "smart_passed": smart_passed,
        })

    total = len(test_cases)
    backchannel_total = category_stats["backchannel"]["total"]
    correction_total = category_stats["correction"]["total"]

    summary = {
        "total_cases": total,
        "naive_accuracy_percent": round(naive_correct / total * 100, 2),
        "smart_accuracy_percent": round(smart_correct / total * 100, 2),
        "naive_false_interruption_rate_percent": round(
            naive_backchannel_interruptions / backchannel_total * 100, 2
        ),
        "smart_false_interruption_rate_percent": round(
            smart_backchannel_interruptions / backchannel_total * 100, 2
        ),
        "naive_missed_correction_rate_percent": round(
            naive_missed_corrections / correction_total * 100, 2
        ),
        "smart_missed_correction_rate_percent": round(
            smart_missed_corrections / correction_total * 100, 2
        ),
        "category_accuracy": {
            category: {
                "passed": stats["passed"],
                "total": stats["total"],
                "accuracy_percent": round(
                    stats["passed"] / stats["total"] * 100, 2
                ),
            }
            for category, stats in category_stats.items()
        },
        "cases": results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print("\n========== TURN-TAKING EVALUATION ==========")
    print(f"Total test cases: {total}")
    print(f"Naive accuracy: {summary['naive_accuracy_percent']}%")
    print(f"Smart accuracy: {summary['smart_accuracy_percent']}%")

    print("\n--- False interruption rate ---")
    print(
        "Naive:",
        f"{summary['naive_false_interruption_rate_percent']}%"
    )
    print(
        "Smart:",
        f"{summary['smart_false_interruption_rate_percent']}%"
    )

    print("\n--- Missed correction rate ---")
    print(
        "Naive:",
        f"{summary['naive_missed_correction_rate_percent']}%"
    )
    print(
        "Smart:",
        f"{summary['smart_missed_correction_rate_percent']}%"
    )

    print("\n--- Category accuracy ---")
    for category, stats in summary["category_accuracy"].items():
        print(
            f"{category}: {stats['passed']}/{stats['total']} "
            f"({stats['accuracy_percent']}%)"
        )

    print("\n--- Failed smart predictions ---")
    failures = [case for case in results if not case["smart_passed"]]

    if failures:
        for case in failures:
            print(
                f"Transcript: {case['transcript']!r} | "
                f"Expected: {case['expected']} | "
                f"Predicted: {case['smart_prediction']}"
            )
    else:
        print("No failures!")

    print(f"\nFull results saved to: {output_path}")


if __name__ == "__main__":
    main()