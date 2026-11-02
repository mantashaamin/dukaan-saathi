# Dukaan Saathi — Evaluation Results

## 1. Phase 0 — Initial Test Results

### 1.1 Prisma file-based STT

- **Status:** PASS
- **Model:** gnani-prisma-v2.5
- **Language:** hi-IN
- **Input:** `kirana-test.wav`
- **Result:** API returned `success=True` and a transcript.

### 1.2 Prisma streaming STT

- **Status:** NOT PASSING YET
- **Connection:** Successful
- **Audio sending:** Completed
- **Processing event:** Received
- **Transcript segments:** 0
- **Next action:** Investigate event delivery and streaming behavior.

### 1.3 Timbre TTS

- **Status:** PASS
- **Model:** timbre-v2.5
- **Voice:** Nalini
- **Language:** hi-IN
- **Output:** `kirana-confirmation.mp3`
- **Playback:** Confirmed; sounded clear and natural.

### Measurements and remaining work

- File-based STT cost: ₹0.06 for the recorded request.
- TTS cost: ₹0.16 for the recorded request.
- Total recorded usage: ₹0.22 across 2 billable requests.
- Streaming transcript latency: Not measured; streaming returned 0 transcript segments.
- Remaining: Investigate streaming STT event delivery.

---

## 2. Order Parser Evaluation

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

---

## 3. Turn-Taking Engine Evaluation

### Objective

Evaluate whether the rule-based turn-taking classifier can distinguish between customer acknowledgements, genuine corrections, and uncertain speech while the assistant is speaking.

The smart classifier is compared against a naive baseline that stops playback whenever non-empty customer speech is detected.

### Test Dataset

- **Total test cases:** 30
- **Dataset:** `eval/turn_test_cases.json`
- **Dataset generation script:** `eval/make_turn_testset.py`
- **Evaluation script:** `eval/run_turn_eval.py`
- **Detailed results:** `eval/results/turntaking_eval.json`
- **Data type:** Synthetic text-based test cases

### Final Results

| Metric | Naive baseline | Smart classifier |
|---|---:|---:|
| Overall accuracy | 36.67% | 100% |
| False interruption rate | 100% | 0% |
| Missed correction rate | 0% | 0% |

### Category-wise Results

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| Backchannel | 10 | 10 | 100% |
| Correction | 10 | 10 | 100% |
| Ambiguous speech | 10 | 10 | 100% |

### Classification Examples

| Customer speech | Expected decision | Result |
|---|---|---|
| `haan haan` | CONTINUE | Correct |
| `हाँहाँ` | CONTINUE | Correct |
| `ruko` | STOP_AND_CORRECT | Correct |
| `aloo nahi, pyaz de do` | STOP_AND_CORRECT | Correct |
| `pata nahi` | ASK_AGAIN | Correct |

### Improvements Made During Testing

- Added Hindi Devanagari backchannel normalization for common acknowledgements.
- Added recognition of Romanized and Devanagari backchannel expressions.
- Implemented complete-word and phrase matching for interruption cues.
- Added a contextual exception for ambiguous expressions such as `pata

### Expanded Development Evaluation

After the initial 30-case pilot, the turn-taking dataset was expanded to 90 synthetic text cases.

**Dataset details**

- Total cases: 90
- Backchannels: 30
- Corrections: 30
- Ambiguous speech: 30
- Dataset: `eval/turn_test_cases_expanded.json`
- Generation script: `eval/make_expanded_turn_testset.py`
- Detailed results: `eval/results/turntaking_eval_expanded.json`

**Results**

| Metric | Naive baseline | Smart classifier |
|---|---:|---:|
| Overall accuracy | 34.44% | 100% |
| False interruption rate | 100% | 0% |
| Missed correction rate | 0% | 0% |

| Category | Passed | Total |
|---|---:|---:|
| Backchannel | 30 | 30 |
| Correction | 30 | 30 |
| Ambiguous | 30 | 30 |

**Rule improvements identified during evaluation**

- Added contextual handling for `pata nahi`.
- Added contextual handling for `samajh nahi aaya`.
- Preserved the existing backchannel and correction classification behaviour.

**Evaluation limitation:** The expanded dataset was used during rule development and tuning. Its 100% result must not be presented as independent test performance or real-world voice accuracy. A separate holdout set and audio-based evaluation are still required.

### Independent Holdout Evaluation

A separate 30-case holdout dataset was created to evaluate how well the frozen rule-based classifier generalizes to previously unused utterances.

**Dataset details**

- Total cases: 30
- Backchannels: 10
- Corrections: 10
- Ambiguous speech: 10
- Dataset: `eval/turn_test_cases_holdout.json`
- Generation script: `eval/make_holdout_turn_testset.py`
- Evaluation script: `eval/run_holdout_turn_eval.py`
- Detailed results: `eval/results/turntaking_holdout_eval.json`

**Results**

| Metric | Naive baseline | Smart classifier |
|---|---:|---:|
| Overall accuracy | 33.33% | 83.33% |
| False interruption rate | — | 40% |
| Missed correction rate | — | 0% |

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| Backchannel | 6 | 10 | 60% |
| Correction | 10 | 10 | 100% |
| Ambiguous | 9 | 10 | 90% |

**Key observations**

- The classifier correctly handled all 10 correction cases.
- Four backchannel cases were incorrectly classified as ASK_AGAIN.
- One ambiguous expression, `abhi yaad nahi aa raha`, was incorrectly classified as STOP_AND_CORRECT.
- The results reveal limitations in backchannel vocabulary coverage and contextual handling of negation.

**Limitations**

This is a small, manually labelled holdout dataset. It provides an initial indication of generalization but is not sufficient to establish real-world voice accuracy.

The classifier rules were kept unchanged during this evaluation. The holdout results are preserved as the baseline measurement for this version of the classifier.

## Turn-Taking Evaluation

The turn-taking classifier was evaluated against a naive baseline that stops playback whenever speech is detected.

### Development Evaluation

A manually created development dataset containing 90 test cases was used to evaluate three categories: backchannels, corrections, and ambiguous speech.

| Metric | Naive Baseline | Smart Classifier |
|---|---:|---:|
| Overall accuracy | 34.44% | 100% |
| False interruption rate | 100% | 0% |
| Missed correction rate | 0% | 0% |

**Category accuracy:**
- Backchannels: 30/30 (100%)
- Corrections: 30/30 (100%)
- Ambiguous speech: 30/30 (100%)

### Independent Holdout Evaluation

To check generalization, the classifier was evaluated on a separate holdout dataset of 30 cases without tuning the rules against it.

| Metric | Naive Baseline | Smart Classifier |
|---|---:|---:|
| Overall accuracy | 33.33% | 66.67% |
| False interruption rate | — | 40% |
| Missed correction rate | — | 50% |

**Category accuracy:**
- Backchannels: 6/10 (60%)
- Corrections: 5/10 (50%)
- Ambiguous speech: 9/10 (90%)

### Key Observations

The development results show that the rule-based classifier handles the tested phrases effectively. However, the independent holdout results reveal that it struggles with unfamiliar expressions and variations in natural speech.

For example, phrases such as "haan bilkul" and "quantity badhi kar do" were not classified correctly.

This highlights an important limitation: performing well on known test phrases does not necessarily mean the system generalizes to real conversations.

### Limitations

- The evaluation datasets are manually created synthetic text examples.
- They do not represent large-scale real-world speech conditions.
- Human audio samples were tested separately and are not included in these accuracy figures.
- More diverse speech samples and further evaluation are needed.

**Conclusion:** The classifier demonstrates improvement over the naive baseline on the holdout set, but its generalization remains a work in progress. The results emphasize the importance of testing conversational AI beyond its development dataset.[  ]