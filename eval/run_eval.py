
import json
from pathlib import Path
import time
import httpx

from server.order_parser import parse_order

TEST_FILE = Path(__file__).with_name("test_orders.json")
RESULTS_DIR = Path(__file__).with_name("results")

def normalize_items(items):
    combined = {}

    for item in items:
        key = (item["name"].strip().lower(), item["unit"].strip().lower())
        combined[key] = combined.get(key, 0) + item["quantity"]

    return combined


def main():
    test_cases = json.loads(TEST_FILE.read_text(encoding="utf-8"))
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    passed = 0

    for index, case in enumerate(test_cases, start=1):
        print(f"[{index}/{len(test_cases)}] Testing: {case['transcript']}")

        try:
            actual = parse_order(case["transcript"]).model_dump()
            expected = case["expected"]

            actual_items = normalize_items(actual["items"])
            expected_items = normalize_items(expected["items"])

            items_match = actual_items == expected_items

            clarification_match = (
                actual["needs_clarification"]
                == expected["needs_clarification"]
            )

            success = items_match and clarification_match
            passed += int(success)

            results.append({
                "transcript": case["transcript"],
                "expected": expected,
                "actual": actual,
                "passed": success,
            })

            print("  PASS" if success else "  FAIL")

        except Exception as exc:
            error_message = str(exc)

            if "429" in error_message:
                print("  Rate limited. Wait 10 seconds and retry this case...")
                time.sleep(15)

                try:
                    actual = parse_order(case["transcript"]).model_dump()
                    expected = case["expected"]

                    actual_items = normalize_items(actual["items"])
                    expected_items = normalize_items(expected["items"])

                    items_match = actual_items == expected_items
                    clarification_match = (
                        actual["needs_clarification"]
                        == expected["needs_clarification"]
                    )
                    success = items_match and clarification_match
                    passed += int(success)

                    results.append({
                        "transcript": case["transcript"],
                        "expected": expected,
                        "actual": actual,
                        "passed": success,
                    })
                    print("  PASS (retry)" if success else "  FAIL (retry)")

                except Exception as retry_exc:
                    results.append({
                        "transcript": case["transcript"],
                        "error": str(retry_exc),
                        "passed": False,
                    })
                    print(f"  Retry failed: {retry_exc}")

            else:
                results.append({
                    "transcript": case["transcript"],
                    "error": error_message,
                    "passed": False,
                })
                print(f"  ERROR: {exc}")

    output_file = RESULTS_DIR / "parser_eval.json"
    output_file.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nResults: {passed}/{len(test_cases)} passed")
    print(f"Accuracy: {passed / len(test_cases) * 100:.1f}%")
    print(f"Detailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
