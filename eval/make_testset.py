
import json
from pathlib import Path

TEST_CASES = [
    {
        "transcript": "Bhaiya, do kilo chawal aur ek packet namak.",
        "expected": {
            "items": [
                {"name": "chawal", "quantity": 2, "unit": "kg"},
                {"name": "namak", "quantity": 1, "unit": "packet"},
            ],
            "needs_clarification": False,
        },
    },
    {
        "transcript": "Ek kilo aloo aur aadha kilo pyaz dena.",
        "expected": {
            "items": [
                {"name": "aloo", "quantity": 1, "unit": "kg"},
                {"name": "pyaz", "quantity": 0.5, "unit": "kg"},
            ],
            "needs_clarification": False,
        },
    },
    {
        "transcript": "Paanch packet Parle-G dena.",
        "expected": {
            "items": [
                {"name": "Parle-G", "quantity": 5, "unit": "packet"},
            ],
            "needs_clarification": False,
        },
    },
    {
        "transcript": "Teen kilo chawal nahi, paanch kilo chawal.",
        "expected": {
            "items": [
                {"name": "chawal", "quantity": 5, "unit": "kg"},
            ],
            "needs_clarification": False,
        },
    },
    {
        "transcript": "Ek packet namak nahi, atta.",
        "expected": {
            "items": [
                {"name": "atta", "quantity": 1, "unit": "packet"},
            ],
            "needs_clarification": False,
        },
    },
    {
        "transcript": "Bhaiya, woh wala biscuit de dena.",
        "expected": {
            "items": [],
            "needs_clarification": True,
        },
    },

    {
        "transcript": "Bhaiya, aadha kilo cheeni dena.",
        "expected": {"items": [{"name": "cheeni", "quantity": 0.5, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Paanch sau gram badam dena.",
        "expected": {"items": [{"name": "badam", "quantity": 500, "unit": "g"}], "needs_clarification": False},
    },
    {
        "transcript": "Do litre doodh aur ek kilo cheeni.",
        "expected": {"items": [{"name": "doodh", "quantity": 2, "unit": "litre"}, {"name": "cheeni", "quantity": 1, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Das ande dena.",
        "expected": {"items": [{"name": "ande", "quantity": 10, "unit": "piece"}], "needs_clarification": False},
    },
    {
        "transcript": "Teen packet Maggi aur do packet biscuit.",
        "expected": {"items": [{"name": "Maggi", "quantity": 3, "unit": "packet"}, {"name": "biscuit", "quantity": 2, "unit": "packet"}], "needs_clarification": False},
    },
    {
        "transcript": "Ek kilo aloo nahi, do kilo aloo.",
        "expected": {"items": [{"name": "aloo", "quantity": 2, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Do litre doodh nahi, ek litre doodh.",
        "expected": {"items": [{"name": "doodh", "quantity": 1, "unit": "litre"}], "needs_clarification": False},
    },
    {
        "transcript": "Ek packet namak aur ek packet namak.",
        "expected": {"items": [{"name": "namak", "quantity": 1, "unit": "packet"}, {"name": "namak", "quantity": 1, "unit": "packet"}], "needs_clarification": False},
    },
    {
        "transcript": "Bhaiya, kuch biscuit dena.",
        "expected": {"items": [], "needs_clarification": True},
    },
    {
        "transcript": "Ek kilo chawal aur do kilo aloo, bas.",
        "expected": {"items": [{"name": "chawal", "quantity": 1, "unit": "kg"}, {"name": "aloo", "quantity": 2, "unit": "kg"}], "needs_clarification": False},
    },
        {
        "transcript": "Ek kilo tamatar dena.",
        "expected": {"items": [{"name": "tamatar", "quantity": 1, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Aadha kilo bhindi aur do kilo baingan.",
        "expected": {"items": [{"name": "bhindi", "quantity": 0.5, "unit": "kg"}, {"name": "baingan", "quantity": 2, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Do sau gram kaju dena.",
        "expected": {"items": [{"name": "kaju", "quantity": 200, "unit": "g"}], "needs_clarification": False},
    },
    {
        "transcript": "Ek litre tel aur do kilo aata.",
        "expected": {"items": [{"name": "tel", "quantity": 1, "unit": "litre"}, {"name": "aata", "quantity": 2, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Chaar packet biscuit dena.",
        "expected": {"items": [{"name": "biscuit", "quantity": 4, "unit": "packet"}], "needs_clarification": False},
    },
    {
        "transcript": "Ek dozen ande dena.",
        "expected": {"items": [{"name": "ande", "quantity": 12, "unit": "piece"}], "needs_clarification": False},
    },
    {
        "transcript": "Teen kilo chawal aur aadha kilo daal.",
        "expected": {"items": [{"name": "chawal", "quantity": 3, "unit": "kg"}, {"name": "daal", "quantity": 0.5, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Ek packet namak aur do packet Maggi.",
        "expected": {"items": [{"name": "namak", "quantity": 1, "unit": "packet"}, {"name": "Maggi", "quantity": 2, "unit": "packet"}], "needs_clarification": False},
    },
    {
        "transcript": "Paanch kilo aloo nahi, teen kilo aloo.",
        "expected": {"items": [{"name": "aloo", "quantity": 3, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Do packet biscuit nahi, ek packet biscuit.",
        "expected": {"items": [{"name": "biscuit", "quantity": 1, "unit": "packet"}], "needs_clarification": False},
    },
    {
        "transcript": "Ek kilo pyaz nahi, aadha kilo pyaz.",
        "expected": {"items": [{"name": "pyaz", "quantity": 0.5, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Doodh nahi, dahi dena.",
        "expected": {"items": [], "needs_clarification": True},
    },
    {
        "transcript": "Woh wala tel dena.",
        "expected": {"items": [], "needs_clarification": True},
    },
    {
        "transcript": "Thoda sa cheeni dena.",
        "expected": {"items": [], "needs_clarification": True},
    },
    {
        "transcript": "Ek packet dena.",
        "expected": {"items": [], "needs_clarification": True},
    },
    {
        "transcript": "Do kilo chawal aur ek litre doodh aur paanch ande.",
        "expected": {"items": [{"name": "chawal", "quantity": 2, "unit": "kg"}, {"name": "doodh", "quantity": 1, "unit": "litre"}, {"name": "ande", "quantity": 5, "unit": "piece"}], "needs_clarification": False},
    },
    {
        "transcript": "Ek kilo cheeni aur ek kilo cheeni.",
        "expected": {"items": [{"name": "cheeni", "quantity": 1, "unit": "kg"}, {"name": "cheeni", "quantity": 1, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Aath packet Parle-G dena.",
        "expected": {"items": [{"name": "Parle-G", "quantity": 8, "unit": "packet"}], "needs_clarification": False},
    },
    {
        "transcript": "Do sau pachaas gram badam dena.",
        "expected": {"items": [{"name": "badam", "quantity": 250, "unit": "g"}], "needs_clarification": False},
    },
    {
        "transcript": "Ek litre doodh nahi, do litre doodh aur ek packet namak.",
        "expected": {"items": [{"name": "doodh", "quantity": 2, "unit": "litre"}, {"name": "namak", "quantity": 1, "unit": "packet"}], "needs_clarification": False},
    },
    {
        "transcript": "Teen kilo aloo aur teen kilo aloo.",
        "expected": {"items": [{"name": "aloo", "quantity": 3, "unit": "kg"}, {"name": "aloo", "quantity": 3, "unit": "kg"}], "needs_clarification": False},
    },
    {
        "transcript": "Ek kilo chawal dena, aur nahi rehne do.",
        "expected": {"items": [], "needs_clarification": True},
    },
    {
        "transcript": "Paanch packet Maggi nahi, do packet Maggi aur ek packet biscuit.",
        "expected": {"items": [{"name": "Maggi", "quantity": 2, "unit": "packet"}, {"name": "biscuit", "quantity": 1, "unit": "packet"}], "needs_clarification": False},
    },
    {
        "transcript": "Bas aadha kilo tamatar dena, aur kuch nahi.",
        "expected": {"items": [{"name": "tamatar", "quantity": 0.5, "unit": "kg"}], "needs_clarification": False},
    },

]

def main():
    output_path = Path(__file__).with_name("test_orders.json")
    output_path.write_text(
        json.dumps(TEST_CASES, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Created {len(TEST_CASES)} test cases at {output_path}")

if __name__ == "__main__":
    main()
