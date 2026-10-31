import json
import time
from pathlib import Path

from server.order_parser import parse_order

RESULTS_FILE = Path("eval/results/parser_eval.json")
TEST_FILE = Path("eval/test_orders.json")


def normalize_items(items):
    combined = {}
    for item in items:
        key = (item["name"].strip().lower(), item["unit"].strip().lower())
        combined[key] = combined.get(key, 0) + item["quantity"]
    return combined


def main():
    results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    tests = json.loads(TEST_FILE.read_text(encoding="utf-8"))

    # Retry only cases that previously errored or did not pass.
    unresolved = [
        i for i, result in enumerate(results)
        if "error" in result or not result.get("passed", False)
    ]

    print(f"Retrying {len(unresolved)} unresolved cases.")
    print("Waiting 15 seconds between attempts to reduce rate limiting.")

    for index in unresolved:
        case = tests[index]
        print(f"\nCase {index + 1}/40: {case['transcript']}")

        try:
            actual = parse_order(case["transcript"]).model_dump()
            expected = case["expected"]

            passed = (
                normalize_items(actual["items"])
                == normalize_items(expected["items"])
                and actual["needs_clarification"]
                == expected["needs_clarification"]
            )

            results[index] = {
                "transcript": case["transcript"],
                "expected": expected,
                "actual": actual,
                "passed": passed,
            }
            print("PASS" if passed else "FAIL: prediction mismatch")

        except Exception as exc:
            results[index]["error"] = str(exc)
            results[index]["passed"] = False
            print(f"Request unresolved: {exc}")

        # Save progress after every attempt.
        RESULTS_FILE.write_text(
            json.dumps(results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        if index != unresolved[-1]:
            time.sleep(15)

    passed_count = sum(r.get("passed", False) for r in results)
    errors = sum("error" in r for r in results)

    print(f"\nPassed: {passed_count}/40")
    print(f"Unresolved errors: {errors}")
    print("Results saved.")


if __name__ == "__main__":
    main()