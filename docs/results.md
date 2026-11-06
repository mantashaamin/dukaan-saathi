# Dukaan Saathi — Evaluation Results

## 1. Evaluation Overview

This document records the testing and evaluation performed on Dukaan Saathi.

The project uses multiple evaluation approaches:

- API smoke tests for Gnani Prisma and Timbre.
- Synthetic grocery-order examples for the LLM order parser.
- Synthetic conversational examples for the turn-taking engine.
- Automated unit tests using Pytest.
- Real-audio evaluation planned using publicly available speech datasets.

Results from synthetic text datasets should not be interpreted as real-world speech accuracy.

---

## 2. Gnani API Smoke Tests

### 2.1 Prisma Speech-to-Text

| Parameter | Result |
|---|---|
| Model | `gnani-prisma-v2.5` |
| Language | `hi-IN` |
| Input | `kirana-test.wav` |
| Status | Successful |
| Result | API returned `success=True` and a transcript |

The initial file-based STT test successfully returned a Hindi transcript.

### 2.2 Prisma Streaming STT

| Parameter | Result |
|---|---|
| Connection | Successful |
| Audio sending | Completed |
| Processing event | Received |
| Transcript segments | 0 |
| Status | Not passing in the initial test |

Streaming transcript delivery remains an area for further investigation. The successful file-based transcription test should not be confused with successful streaming transcription.

### 2.3 Timbre Text-to-Speech

| Parameter | Result |
|---|---|
| Model | `timbre-v2.5` |
| Voice | Nalini |
| Language | `hi-IN` |
| Output | `kirana-confirmation.mp3` |
| Playback | Successful |

The generated Hindi confirmation audio was played successfully and sounded clear and natural to the listener.

### 2.4 Recorded API Usage

The following costs were observed during the initial API tests:

| Service | Model | Recorded usage | Cost |
|---|---|---:|---:|
| STT | prisma-v2.5 | 0.13 minutes | ₹0.06 |
| TTS | timbre-v2.5 | 57 characters | ₹0.16 |
| **Total** | — | 2 billable requests | **₹0.22** |

These are costs from specific recorded requests, not guaranteed costs for every future request.

---

## 3. Order Parser Evaluation

### Objective

Evaluate whether the LLM-based order parser can convert Hindi and Hinglish grocery-order transcripts into structured order data.

### Dataset

| Parameter | Details |
|---|---|
| Total test cases | 40 |
| Dataset | `eval/test_orders.json` |
| Evaluation script | `eval/run_eval.py` |
| Retry script | `eval/retry_failed.py` |
| Detailed results | `eval/results/parser_eval.json` |
| Dataset type | Synthetic grocery-order examples |

### Final Results

| Metric | Result |
|---|---:|
| Total test cases | 40 |
| Passed | 40 |
| Failed | 0 |
| Unresolved API errors | 0 |
| Pass rate on this test set | 100% |

### Evaluation Method

The evaluation compares the parser's predicted structured order against the expected output.

The evaluation includes:

- Product-name normalization.
- Quantity and unit comparison.
- Combining repeated entries with the same product and unit.
- Checking the `needs_clarification` decision.
- Retry handling for API rate-limit errors.

### Scenarios Tested

The synthetic dataset includes:

- Single-product orders.
- Multiple-product orders.
- Hindi number words.
- Quantity and unit extraction.
- Repeated products.
- Product corrections.
- Ambiguous requests.
- Packaged goods.
- Cancellation-style instructions.

### Improvements Made

- Expanded the dataset from 16 to 40 cases.
- Added unit normalization.
- Updated evaluation logic to combine repeated product quantities.
- Added retry handling for rate-limited requests.
- Improved cancellation instructions in the parser prompt.
- Corrected expected quantities in test cases.

### Limitation

The 100% result applies only to the 40 prepared synthetic examples. It does not establish 100% accuracy on unseen orders, real customer speech, noisy recordings or different accents.

---

## 4. Turn-Taking Engine Evaluation

### Objective

Evaluate whether the rule-based turn-taking engine can distinguish between customer acknowledgements, corrections and ambiguous speech while the assistant is speaking.

The smart classifier is compared against a naive baseline that stops playback whenever non-empty customer speech is detected.

### Classification Categories

| Category | Expected action |
|---|---|
| Backchannel | `CONTINUE` |
| Correction | `STOP_AND_CORRECT` |
| Ambiguous speech | `ASK_AGAIN` |

---

## 5. Initial Turn-Taking Development Evaluation

### Dataset

| Parameter | Details |
|---|---|
| Total test cases | 30 |
| Dataset | `eval/turn_test_cases.json` |
| Evaluation script | `eval/run_turn_eval.py` |
| Dataset type | Synthetic text examples |

### Results

| Metric | Naive baseline | Smart classifier |
|---|---:|---:|
| Overall accuracy | 36.67% | 100% |
| False interruption rate | 100% | 0% |
| Missed correction rate | 0% | 0% |

### Category Accuracy

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| Backchannel | 10 | 10 | 100% |
| Correction | 10 | 10 | 100% |
| Ambiguous speech | 10 | 10 | 100% |

These results describe the initial prepared development dataset and are not independent generalization results.

---

## 6. Expanded Development Evaluation

The development dataset was expanded to include more conversational expressions.

### Dataset

| Parameter | Details |
|---|---|
| Total cases | 90 |
| Backchannels | 30 |
| Corrections | 30 |
| Ambiguous speech | 30 |
| Dataset | `eval/turn_test_cases_expanded.json` |
| Evaluation script | `eval/run_turn_eval.py` |
| Results | `eval/results/turntaking_eval_expanded.json` |

### Results

| Metric | Naive baseline | Smart classifier |
|---|---:|---:|
| Overall accuracy | 34.44% | 100% |
| False interruption rate | 100% | 0% |
| Missed correction rate | 0% | 0% |

### Category Accuracy

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| Backchannel | 30 | 30 | 100% |
| Correction | 30 | 30 | 100% |
| Ambiguous speech | 30 | 30 | 100% |

### Improvements Made

- Expanded Hindi Devanagari normalization.
- Added Romanized Hindi spelling variations.
- Added more backchannel expressions.
- Improved contextual correction phrase coverage.
- Added handling for ambiguous expressions such as `pata nahi` and `samajh nahi aaya`.
- Preserved Devanagari vowel signs and combining marks during text cleanup.

### Limitation

The expanded development dataset was used during rule development and tuning. Its 100% result must not be treated as independent test performance.

---

## 7. Earlier Holdout Evaluation

An earlier separate 30-case holdout evaluation was used to examine generalization beyond the development examples.

### Dataset

| Parameter | Details |
|---|---|
| Total cases | 30 |
| Backchannels | 10 |
| Corrections | 10 |
| Ambiguous speech | 10 |
| Dataset | `eval/turn_test_cases_holdout.json` |
| Evaluation script | `eval/run_holdout_turn_eval.py` |
| Results | `eval/results/turntaking_holdout_eval.json` |

### Recorded Results

| Metric | Naive baseline | Smart classifier |
|---|---:|---:|
| Overall accuracy | 33.33% | 83.33% |
| False interruption rate | — | 40% |
| Missed correction rate | — | 0% |

### Category Accuracy

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| Backchannel | 6 | 10 | 60% |
| Correction | 10 | 10 | 100% |
| Ambiguous speech | 9 | 10 | 90% |

### Observations

- All 10 correction cases were classified correctly.
- Four backchannel cases were classified as `ASK_AGAIN`.
- One ambiguous expression was incorrectly classified as `STOP_AND_CORRECT`.
- The results highlighted gaps in vocabulary coverage and contextual handling.

This evaluation is retained as an earlier historical measurement. It should not be confused with the later independent evaluation described below.

---

## 8. Additional Independent Evaluation and Rule Improvements

A separate 30-case dataset was used to investigate the behaviour of the updated turn-taking engine.

### Dataset

| Parameter | Details |
|---|---|
| Total cases | 30 |
| Backchannels | 10 |
| Corrections | 10 |
| Ambiguous speech | 10 |
| Dataset | `eval/turn_test_cases_independent.json` |
| Evaluation script | `eval/run_independent_eval.py` |
| Results | `eval/results/turntaking_independent_eval.json` |

### Evaluation Progression

The same 30-case dataset was evaluated across successive rule improvements.

| Evaluation stage | Smart accuracy | False interruption rate | Missed correction rate |
|---|---:|---:|---:|
| Initial evaluation | 63.33% | 60% | 30% |
| After backchannel improvements | 83.33% | 0% | 30% |
| After contextual correction improvements | 100% | 0% | 0% |

### Latest Post-Fix Results

| Metric | Naive baseline | Smart classifier |
|---|---:|---:|
| Overall accuracy | 33.33% | 100% |
| False interruption rate | 100% | 0% |
| Missed correction rate | 0% | 0% |

### Category Accuracy

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| Backchannel | 10 | 10 | 100% |
| Correction | 10 | 10 | 100% |
| Ambiguous speech | 10 | 10 | 100% |

### Improvements Made

The failed cases helped identify several gaps:

- Conversational acknowledgements such as `achha samajh gaya`.
- Expressions such as `haan aage bolo`.
- Correction phrases such as `ruk jaiye, ek change hai`.
- Additional-product requests such as `ek aur bread add karna`.
- Contextual order changes such as `mera order change karna hai`.
- Ambiguous expressions such as `nahi matlab woh nahi`.
- Thinking pauses such as `ek minute, sochne do`.

The rules and phrase coverage were updated to address these cases.

### Important Evaluation Limitation

The independent dataset was inspected during error analysis and used to guide subsequent rule changes. Therefore, the latest 100% result is a post-fix re-evaluation on the same dataset, not an untouched independent benchmark.

The earlier scores are retained to show the actual improvement process.

A new unseen dataset is required to measure generalization without tuning against its examples.

---

## 9. Automated Testing

Pytest is used to verify the normalization and turn-taking implementation.

### Latest Recorded Result

<text id="test-result">38 tests passed.</text>

```text
38 passed in 182.51s
```

### Testing Coverage

- Transcript normalization.
- Hindi Devanagari expressions.
- Romanized Hindi variations.
- Backchannel classification.
- Correction classification.
- Ambiguous speech handling.
- Empty transcript handling.
- Feature extraction.
- Turn-taking classification.

The test suite provides automated regression coverage for the implemented behaviour.

---

## 10. Real-Audio Dataset Evaluation — Planned

Synthetic transcript evaluation does not fully represent real conversational speech.

The next evaluation phase will use publicly available Hindi speech recordings to examine how the system behaves with real voices.

### Selected Dataset

**IndicVoices — AI4Bharat**

Dataset page:

https://huggingface.co/datasets/ai4bharat/IndicVoices

### Dataset Characteristics

- Natural and spontaneous speech.
- More than 23,000 hours of speech described in the dataset overview.
- Recordings from multiple Indian languages.
- Multiple speakers and regional variations.
- Read, extempore and conversational speech.

The Hindi subset will be explored for relevant audio samples.

### Planned Evaluation

1. Obtain access to the dataset and inspect its Hindi subset.
2. Select a manageable collection of audio recordings.
3. Run the recordings through the speech-to-text pipeline.
4. Examine transcript quality and normalization.
5. Identify suitable conversational utterances for turn-taking evaluation.
6. Manually label selected examples as backchannel, correction or ambiguous where the context supports a reliable label.
7. Compare the classifier's predictions against those labels.
8. Record transcription errors separately from turn-taking classification errors.

### Current Status

<badge color="warning">Planned — not yet evaluated</badge>

No real-audio accuracy figure is claimed at this stage.

IndicVoices is a general speech dataset, not a dedicated kirana-order correction dataset. It may not contain enough suitable conversational corrections to evaluate every turn-taking category.

---

## 11. Overall Limitations

The current evaluation has several limitations:

1. Most parser and turn-taking metrics come from synthetic text examples.
2. The datasets are relatively small.
3. The independent 30-case dataset was used during rule refinement, so its final score is not an untouched benchmark.
4. Real-world speech introduces accents, background noise, overlapping speech and recognition errors.
5. The initial Prisma streaming test returned zero transcript segments.
6. Continuous automatic interruption detection and real-time audio ducking have not yet been implemented.
7. Real-audio turn-taking accuracy has not yet been measured.

These limitations are important when interpreting the current results.

---

## 12. Conclusion

Dukaan Saathi has successfully implemented a voice-based grocery-ordering workflow combining speech recognition, LLM-based structured order extraction, data validation, spoken confirmation and contextual corrections.

The order parser achieved a 40/40 pass rate on its prepared synthetic evaluation dataset.

The turn-taking engine achieved 100% on its expanded development dataset and on a later post-fix re-evaluation of the same additional 30-case dataset. Earlier holdout results are preserved to show the challenges encountered during generalization.

The automated test suite currently reports 38 passing tests.

The next major evaluation milestone is testing with real Hindi and Hinglish audio recordings, measuring transcription quality and evaluating conversational turn-taking under more realistic conditions.

**The objective is not simply to achieve high accuracy on prepared examples, but to build a voice assistant that behaves reliably in real kirana-store conversations.**