
import json
import re
import unicodedata
from pathlib import Path


INPUT_PATH = Path("data/indicvoices_samples/prisma_evaluation.json")


def normalize(text):
    """Normalize Hindi text before word-level comparison."""

    text = unicodedata.normalize("NFC", text)
    text = text.casefold()

    # Remove punctuation while preserving Hindi characters and spaces
    text = "".join(
        char if unicodedata.category(char)[0] in ("L", "M", "N")
        or char.isspace()
        else " "
        for char in text
    )

    return " ".join(text.split())


def calculate_errors(reference, hypothesis):
    """Calculate substitutions, deletions and insertions."""

    ref = normalize(reference).split()
    hyp = normalize(hypothesis).split()

    rows = len(ref) + 1
    cols = len(hyp) + 1

    dp = [[0] * cols for _ in range(rows)]
    operations = [[""] * cols for _ in range(rows)]

    for i in range(1, rows):
        dp[i][0] = i
        operations[i][0] = "D"

    for j in range(1, cols):
        dp[0][j] = j
        operations[0][j] = "I"

    for i in range(1, rows):
        for j in range(1, cols):

            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                operations[i][j] = "C"
            else:
                choices = [
                    (dp[i - 1][j - 1] + 1, "S"),
                    (dp[i - 1][j] + 1, "D"),
                    (dp[i][j - 1] + 1, "I"),
                ]

                dp[i][j], operations[i][j] = min(
                    choices,
                    key=lambda item: item[0],
                )

    substitutions = deletions = insertions = 0

    i, j = len(ref), len(hyp)

    while i > 0 or j > 0:
        operation = operations[i][j]

        if operation == "C":
            i -= 1
            j -= 1
        elif operation == "S":
            substitutions += 1
            i -= 1
            j -= 1
        elif operation == "D":
            deletions += 1
            i -= 1
        elif operation == "I":
            insertions += 1
            j -= 1
        else:
            break

    total_errors = substitutions + deletions + insertions
    wer = total_errors / len(ref) if ref else 0.0

    return {
        "reference_words": len(ref),
        "substitutions": substitutions,
        "deletions": deletions,
        "insertions": insertions,
        "errors": total_errors,
        "wer": wer,
    }


def main():
    if not INPUT_PATH.exists():
        print("Evaluation JSON not found:", INPUT_PATH)
        return

    results = json.loads(
        INPUT_PATH.read_text(encoding="utf-8")
    )

    total_substitutions = 0
    total_deletions = 0
    total_insertions = 0
    total_reference_words = 0

    successful_samples = 0

    print("\nINDICVOICES - WORD ERROR RATE EVALUATION")
    print("=" * 55)

    for sample in results:

        if sample.get("status") != "success":
            print(f"\nSample {sample['sample']}: SKIPPED")
            continue

        reference = sample.get("reference", "")
        predicted = sample.get("predicted", "")

        if not reference or not predicted:
            print(f"\nSample {sample['sample']}: SKIPPED - empty text")
            continue

        metrics = calculate_errors(reference, predicted)

        successful_samples += 1
        total_substitutions += metrics["substitutions"]
        total_deletions += metrics["deletions"]
        total_insertions += metrics["insertions"]
        total_reference_words += metrics["reference_words"]

        print(f"\nSAMPLE {sample['sample']}")
        print("Reference words :", metrics["reference_words"])
        print("Substitutions   :", metrics["substitutions"])
        print("Deletions       :", metrics["deletions"])
        print("Insertions      :", metrics["insertions"])
        print(f"WER             : {metrics['wer'] * 100:.2f}%")

    total_errors = (
        total_substitutions
        + total_deletions
        + total_insertions
    )

    overall_wer = (
        total_errors / total_reference_words
        if total_reference_words
        else 0.0
    )

    print("\n" + "=" * 55)
    print("OVERALL RESULTS")
    print("=" * 55)

    print("Successful samples :", successful_samples)
    print("Reference words     :", total_reference_words)
    print("Substitutions       :", total_substitutions)
    print("Deletions           :", total_deletions)
    print("Insertions          :", total_insertions)
    print("Total errors        :", total_errors)
    print(f"Overall WER         : {overall_wer * 100:.2f}%")
    print(f"Word accuracy proxy : {(1 - overall_wer) * 100:.2f}%")

    print("\nNote: WER is not capped at 100%.")
    print("Word accuracy proxy is 100% minus WER,")
    print("not a separate standardized accuracy metric.")


if __name__ == "__main__":
    main()
