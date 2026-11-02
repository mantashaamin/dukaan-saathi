python turntaking/test_normalization.pyfrom turntaking.features import extract_features

test_cases = [
    "हाँहाँ",
    "हाँ हाँ",
    "हाँ",
    "हां",
    "हम्म",
    "अच्छा",
    "जी",
    "ठीक है",
    "ओके",
    "haan haan",
    "haan",
    "hmm",
    "acha",
    "ji",
    "theek hai",
    "ok",
    "aloo nahi, pyaz de do",
]

print("\nBACKCHANNEL NORMALIZATION TESTS\n")

for transcript in test_cases:
    result = extract_features(transcript, 0.5)

    print(
        f"Input: {transcript:25} | "
        f"Normalized: {result['transcript']:20} | "
        f"Backchannel: {result['is_backchannel']}"
    )
