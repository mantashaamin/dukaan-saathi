
# Phase 0 — Initial Test Results

## 1. Prisma file-based STT
- Status: PASS
- Model: gnani-prisma-v2.5
- Language: hi-IN
- Input: kirana-test.wav
- Result: API returned success=True and a transcript.

## 2. Prisma streaming STT
- Status: NOT PASSING YET
- Connection: Successful
- Audio sending: Completed
- Processing event: Received
- Transcript segments: 0
- Next action: Investigate event delivery and streaming behavior.

## 3. Timbre TTS
- Status: PASS
- Model: timbre-v2.5
- Voice: Nalini
- Language: hi-IN
- Output: kirana-confirmation.mp3
- Playback: Confirmed; sounded clear and natural.


## Measurements and remaining work

- File-based STT cost: ₹0.06 for the recorded request.
- TTS cost: ₹0.16 for the recorded request.
- Total recorded usage: ₹0.22 across 2 billable requests.
- Streaming transcript latency: Not measured; streaming returned 0 transcript segments.
- Remaining: Investigate streaming STT event delivery.

---

## 4. Order Parser Evaluation

### Objective

Evaluate whether the LLM-based order parser correctly converts Hindi/Hinglish grocery-order transcripts into structured order data.

### Test Dataset

- **Total test cases:** 40
- **Dataset:** `eval/test_orders.json`
- **Evaluation script:** `eval/run_eval.py`
- **Retry script:** `eval/retry_failed.py`
- **Detailed results:** `eval/results/parser_eval.json`
- **Data type:** Synthetic grocery-order examples

### Final Results

| Metric | Result |
|---|---:|
| Total test cases | 40 |
| Passed | 40 |
| Failed | 0 |
| Unresolved API errors | 0 |
| Pass rate on this test set | 100% |

### Evaluation Method

The evaluation compares the predicted order against the expected output.

- Product names and units are normalized for comparison.
- Repeated entries with the same product and unit are combined before comparing total quantities.
- The `needs_clarification` decision must match the expected result.
- API rate-limit errors are retried separately rather than treated as valid model predictions.

### Scenarios Tested

The synthetic test set includes single-item and multi-item orders, Hindi number words, quantity and unit extraction, repeated products, product corrections, ambiguous requests, packaged goods, and cancellation-style instructions.

### Improvements Made During Testing

- Expanded the test dataset from 16 to 40 cases.
- Added unit normalization for common unit variations.
- Updated evaluation logic to combine repeated product quantities.
- Added retry handling for rate-limited requests.
- Added a clearer cancellation rule to the parser prompt.
- Corrected the expected quantity for the repeated-aloo test case.

### Limitations

The 100% pass rate applies only to these 40 synthetic test cases. It does not establish 100% accuracy on unseen orders, real customer speech, noisy audio, or different accents.

Further evaluation is required after integrating the parser with the complete voice workflow.

## 5. Overall Project Status

- **File-based STT:** Successfully tested.
- **Streaming STT:** Not yet verified; previous tests returned zero transcript segments.
- **TTS:** Successfully generated and played a Hindi confirmation.
- **Order parser:** Passed all 40 cases in the current synthetic test set.
- **End-to-end voice workflow:** Still under development.
- **Turn-taking and interruption handling:** Still require integration and testing.

## 6. Next Steps

1. Integrate STT, order parsing, and TTS.
2. Build and test the browser voice interface.
3. Implement turn-taking and correction handling.
4. Evaluate the complete workflow, including audio transcription errors and response latency.
5. Update the results as new tests are completed.

