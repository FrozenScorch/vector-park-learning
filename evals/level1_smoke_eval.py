"""Tiny Level 1 eval harness.

This does not judge model quality deeply yet. It establishes the habit:
define cases, run them, and check simple constraints.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from levels.level1_generic_inference import run_inference  # noqa: E402
from levels.llm_provider import load_llm_config  # noqa: E402


CASES = [
    {
        "mode": "classify",
        "text": "Are dogs allowed on hiking trails at this park?",
        "allowed_terms": ["hiking", "trip planning", "not enough information"],
    },
    {
        "mode": "extract",
        "text": "Call the visitor center, check road closures, and pack extra water before leaving.",
        "allowed_terms": ["action_items", "visitor center", "road closures", "water"],
    },
]


def main() -> None:
    load_dotenv()
    load_llm_config()

    failures = []
    for case in CASES:
        output = run_inference(case["mode"], case["text"], temperature=0.0)
        lower_output = output.lower()
        if not any(term.lower() in lower_output for term in case["allowed_terms"]):
            failures.append({"case": case, "output": output})

    if failures:
        print("FAIL")
        for failure in failures:
            print(failure)
        raise SystemExit(1)

    print(f"PASS: {len(CASES)} Level 1 smoke evals passed.")


if __name__ == "__main__":
    main()
