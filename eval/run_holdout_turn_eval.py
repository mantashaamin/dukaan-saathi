
import json
from pathlib import Path
from collections import defaultdict

from turntaking.classifier import turn_classifier


def main():
    eval_dir = Path(__file__).parent

    test_path = eval_dir / "turn_test_cases_holdout.json"
    output_path = eval_dir / "results" / "turntaking_holdout_eval.json"

    with open(test_path, "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    results = []
    stats = defaultdict(lambda: {"total": 0, "passed": 0})

    smart_correct = 0
    naive_correct = 0
    false_interruptions = 0
    missed_corrections = 0

    for case in test_cases:
        transcript = case["transcript"]
        duration = case["duration_seconds"]
        expected = case["expected"]
        category = case["category"]

        smart_prediction = turn_classifier.classify(
            transcript, duration
        ).value

        naive_prediction = (
            "stop_and_correct" if transcript.strip() else "ask_again"
        )

        smart_passed = smart_prediction == expected

        smart_correct += smart_passed
        naive_correct += naive_prediction == expected

        stats[category]["total"] += 1
        stats[category]["passed"] += smart_passed

        if category == "backchannel":
            false_interruptions += smart_prediction != "continue"

        if category == "correction":
            missed_corrections += (
                smart_prediction != "stop_and_correct"
            )

        results.append({
            "transcript": transcript,
            "duration_seconds": duration,
            "category": category,
            "expected": expected,
            "smart_prediction": smart_prediction,
            "naive_prediction": naive_prediction,
            "passed": smart_passed,
        })

    total = len(test_cases)
    backchannel_total = stats["backchannel"]["total"]
    correction_total = stats["correction"]["total"]

    summary = {
        "dataset": "holdout",
        "total_cases": total,
        "smart_accuracy_percent": round(
            smart_correct / total * 100, 2
        ),
        "naive_accuracy_percent": round(
            naive_correct / total * 100, 2
        ),
        "false_interruption_rate_percent": round(
            false_interruptions / backchannel_total * 100, 2
        ),
        "missed_correction_rate_percent": round(
            missed_corrections / correction_total * 100, 2
        ),
        "category_accuracy": {
            category: {
                "passed": values["passed"],
                "total": values["total"],
                "accuracy_percent": round(
                    values["passed"] / values["total"] * 100, 2
                ),
            }
            for category, values in stats.items()
        },
        "cases": results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n========== HOLDOUT EVALUATION ==========")
    print(f"Total cases: {total}")
    print(f"Smart accuracy: {summary['smart_accuracy_percent']}%")
    print(f"Naive accuracy: {summary['naive_accuracy_percent']}%")

    print("\n--- False interruption rate ---")
    print(f"Smart: {summary['false_interruption_rate_percent']}%")

    print("\n--- Missed correction rate ---")
    print(f"Smart: {summary['missed_correction_rate_percent']}%")

    print("\n--- Category accuracy ---")
    for category, values in summary["category_accuracy"].items():
        print(
            f"{category}: {values['passed']}/{values['total']} "
            f"({values['accuracy_percent']}%)"
        )

    print("\n--- Failed predictions ---")
    failures = [case for case in results if not case["passed"]]

    if failures:
        for case in failures:
            print(
                f"Transcript: {case['transcript']!r} | "
                f"Expected: {case['expected']} | "
                f"Predicted: {case['smart_prediction']}"
            )
    else:
        print("No failures!")

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
