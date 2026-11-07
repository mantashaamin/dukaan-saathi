# Dukaan Saathi — Evaluation Results

## 1. Overview

This document records the evaluation of the major components of Dukaan Saathi:

- LLM-based grocery order parsing
- Gnani Prisma speech-to-text
- Conversational turn-taking classification
- Automated tests and integration checks

The evaluations use separate datasets and methods. Their results should not be combined into a single accuracy figure.

---

## 2. Order Parser Evaluation

**Objective:** Evaluate the ability of the LLM-based parser to convert Hindi/Hinglish grocery requests into structured order data.

**Dataset:** `eval/test_orders.json`  
**Test cases:** 40  
**Model:** `openai/gpt-oss-20b` through Groq

| Metric | Result |
|---|---:|
| Total test cases | 40 |
| Passed | 40 |
| Failed | 0 |
| Pass rate | 100% |

### Evaluation coverage

- Single-item and multi-item orders
- Hindi number words and quantity extraction
- Product and unit normalization
- Repeated product entries
- Product corrections
- Order cancellation instructions
- Ambiguous requests and clarification

### Evaluation limitation

The 100% pass rate applies only to the prepared synthetic test dataset. It does not establish equivalent performance on unseen customer orders or noisy real-world conversations.

---

## 3. Turn-Taking Engine Evaluation

**Objective:** Distinguish between ordinary acknowledgements, genuine corrections and unclear responses during conversational interaction.

The classifier produces three decisions:

- `CONTINUE` — preserve the current response for a recognized acknowledgement.
- `STOP_AND_CORRECT` — stop the current response and process a correction.
- `ASK_AGAIN` — request clarification when speech is unclear or ambiguous.

### 3.1 Development evaluation

A synthetic development dataset containing 90 examples was evaluated.

| Category | Correct | Total |
|---|---:|---:|
| Backchannels | 30 | 30 |
| Corrections | 30 | 30 |
| Ambiguous responses | 30 | 30 |
| **Overall** | **90** | **90** |

**Development accuracy: 100%**

This dataset was used during rule development and tuning. It is not an independent test set.

### 3.2 Initial independent holdout baseline

A separate 30-example dataset was initially evaluated before the subsequent rule improvements.

| Metric | Initial result |
|---|---:|
| Smart classifier accuracy | 66.67% |
| Naive baseline accuracy | 33.33% |
| False interruption rate | 40% |
| Missed correction rate | 50% |

The initial results exposed gaps in backchannel vocabulary and contextual correction recognition.

### 3.3 Final regression evaluation

Following improvements to Hindi and Hinglish normalization, phrase coverage and contextual rules, the original 30-case regression set was rerun.

| Metric | Final regression result |
|---|---:|
| Correct classifications | 30/30 |
| Regression accuracy | 100% |

**Important:** The original holdout examples were used during debugging and rule improvements. Therefore, this final 30/30 result is a regression result, not an independent generalization measurement. The original 66.67% result is retained as the initial holdout baseline.

### 3.4 Automated tests

The project test suite completed with:

**32 tests passed.**

The tests cover normalization, backchannel recognition, correction cues and ambiguous speech handling.

---

## 4. Gnani Prisma Speech Recognition Evaluation

Prisma was tested using audio samples from the IndicVoices Hindi dataset.

### 4.1 Initial five-sample evaluation

| Metric | Result |
|---|---:|
| Samples tested | 5 |
| Successful transcriptions | 5 |
| Transcription success rate | 100% |
| Reference words | 53 |
| Substitutions | 4 |
| Deletions | 2 |
| Insertions | 0 |
| Overall Word Error Rate | 11.32% |
| Word accuracy proxy | 88.68% |

The word accuracy proxy is calculated as 100% minus WER. It is not a separate standardized metric.

### 4.2 Thirty-speaker evaluation

A broader evaluation was conducted using 30 samples selected from different speakers.

| Metric | Result |
|---|---:|
| Total samples | 30 |
| Successful transcriptions | 6 |
| Failed transcriptions | 24 |
| Success rate | 20% |

The results varied significantly across recordings. Some short utterances returned no transcript, while longer samples were more likely to produce output.

### 4.3 Silence-padding experiment

A follow-up experiment added 400 ms of silence to both sides of six selected recordings.

| Metric | Result |
|---|---:|
| Samples tested | 6 |
| Successful | 2 |
| Failed | 4 |
| Success rate | 33.33% |

The two successful samples had also succeeded in the earlier evaluation. Padding did not recover the four failed samples, so it was not considered an effective improvement.

### 4.4 Speech recognition limitations

- Very short recordings frequently returned no detectable speech.
- Transcription quality varied across speakers and utterances.
- Some successful transcripts contained substitutions or omissions.
- A successful API response does not necessarily mean the transcript is completely accurate.
- The five-sample WER result must not be generalized to the separate 30-speaker dataset.

---

## 5. Overall Findings

| Component | Evaluation | Result |
|---|---|---|
| Order parser | 40 synthetic cases | 40/40 passed |
| Turn-taking development | 90 synthetic cases | 90/90 passed |
| Initial turn-taking holdout | 30 synthetic cases | 66.67% |
| Final turn-taking regression | 30 previously used cases | 30/30 passed |
| Prisma initial audio test | 5 recordings | 5/5 successful |
| Prisma WER | 5 recordings | 11.32% |
| Prisma speaker evaluation | 30 recordings | 6/30 successful |
| Silence padding | 6 recordings | 2/6 successful |
| Automated test suite | 32 tests | All passed |

## 6. Limitations and Future Improvements

1. Expand speech recognition evaluation with more diverse recordings and longer utterances.
2. Investigate short-utterance recognition failures.
3. Evaluate transcription quality across accents, speakers and background-noise conditions.
4. Collect a fresh, untouched turn-taking test set for independent evaluation.
5. Expand correction and ambiguous-response vocabulary.
6. Explore automatic interruption detection and real-time audio ducking in a future version.

## 7. Conclusion

Dukaan Saathi demonstrates a working Hindi/Hinglish grocery-ordering workflow with structured LLM-based order extraction, validation, contextual corrections and spoken confirmations.

The evaluation shows strong performance on the prepared synthetic order-parsing and turn-taking development datasets. However, the independent baseline and audio recognition experiments also reveal important generalization and speech-recognition limitations.

These findings are documented separately to keep the project's performance claims transparent and reproducible.