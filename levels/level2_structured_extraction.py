"""Level 2: Document Understanding and Structured Extraction.

Learner scaffold — complete the TODO sections using your AI coding assistant.

Usage:
    python levels/level2_structured_extraction.py --endpoint parks --park-code yell
    python levels/level2_structured_extraction.py --endpoint alerts --park-code acad
    python levels/level2_structured_extraction.py --endpoint campgrounds --park-code grca
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from dotenv import load_dotenv

try:
    from levels.llm_provider import make_llm_client
    from levels.nps_client import (
        fetch_park, fetch_alerts, fetch_campgrounds,
        format_park_text_for_inference, format_alert_text, format_campground_text,
    )
    from levels.schemas import ParkExtraction
except ModuleNotFoundError:
    from llm_provider import make_llm_client
    from nps_client import (
        fetch_park, fetch_alerts, fetch_campgrounds,
        format_park_text_for_inference, format_alert_text, format_campground_text,
    )
    from schemas import ParkExtraction


load_dotenv()


# ---------------------------------------------------------------------------
# TODO 1: Build the extraction prompt.
# ---------------------------------------------------------------------------
# Replace the placeholder string below with a real prompt that instructs the
# LLM to return structured JSON matching the ParkExtraction schema.
#
# Requirements:
#   1. Tell the LLM to extract structured data from the source text.
#   2. Specify the exact JSON schema (matching ParkExtraction). Look at
#      levels/schemas.py to understand every field and sub-field.
#   3. Instruct the model to use "unknown" for any missing information.
#   4. Require an evidence quote from the source text for every risk entry.
#   5. Tell the model to return ONLY valid JSON — no markdown fences, no
#      commentary before or after the JSON block.
#
# Hint: Open levels/schemas.py first and study the ParkExtraction model,
# including all nested models (ParkInfo, Risk, Recommendation, etc.).
# Your prompt should describe each field so the LLM knows exactly what to
# fill in.
# ---------------------------------------------------------------------------
EXTRACTION_PROMPT = "TODO: Write your extraction prompt here"


def fetch_source_text(endpoint: str, park_code: str) -> str:
    """Fetch and format text from the chosen NPS endpoint."""
    if endpoint == "parks":
        park = fetch_park(park_code)
        return format_park_text_for_inference(park)
    elif endpoint == "alerts":
        alerts = fetch_alerts(park_code)
        if not alerts:
            return f"No alerts found for park code '{park_code}'."
        return "\n\n---\n\n".join(format_alert_text(a) for a in alerts)
    elif endpoint == "campgrounds":
        campgrounds = fetch_campgrounds(park_code)
        if not campgrounds:
            return f"No campgrounds found for park code '{park_code}'."
        return "\n\n---\n\n".join(format_campground_text(c) for c in campgrounds)
    else:
        raise ValueError(f"Unknown endpoint: {endpoint}")


# ---------------------------------------------------------------------------
# TODO 2: Implement the structured extraction function.
# ---------------------------------------------------------------------------
# Replace the body of extract_structured() with working code.
#
# Steps:
#   1. Call make_llm_client() to get an (OpenAI client, LLMConfig) tuple.
#   2. Build the full user message: EXTRACTION_PROMPT + "\n\n" + source_text.
#   3. Send the prompt to the LLM using client.chat.completions.create().
#      Use temperature=0 for deterministic output and pass config.model as
#      the model name.  Also forward config.max_tokens, config.top_p, and
#      config.extra_body when they are not None (see level1_generic_inference.py
#      for the pattern).
#   4. Extract the text from response.choices[0].message.content.
#   5. Strip markdown code fences if the model wrapped its output in them
#      (e.g. ```json ... ```).  A simple .strip() plus removing leading
#      "```json" and trailing "```" is sufficient.
#   6. Parse the cleaned text with json.loads().
#   7. Validate the parsed dict with ParkExtraction.model_validate().
#   8. Return the validated ParkExtraction object.
#
# Error handling:
#   - If json.loads() fails, print the raw response and re-raise.
#   - If Pydantic validation fails, print the validation errors and re-raise.
# ---------------------------------------------------------------------------
def extract_structured(source_text: str) -> ParkExtraction:
    """Extract structured data from source text using the LLM.

    TODO: Implement this function. It should:
    1. Send the source text to the LLM with the extraction prompt
    2. Parse the response as JSON
    3. Validate with ParkExtraction
    4. Return the validated extraction
    """
    raise NotImplementedError("TODO: Implement extract_structured()")


def main() -> None:
    parser = argparse.ArgumentParser(description="Level 2: Structured Extraction")
    parser.add_argument("--endpoint", choices=["parks", "alerts", "campgrounds"], default="parks")
    parser.add_argument("--park-code", default="yell")
    args = parser.parse_args()

    # Step 1: Fetch source text
    source_text = fetch_source_text(args.endpoint, args.park_code)
    print(f"=== Source text from {args.endpoint} for {args.park_code.upper()} ===\n")
    print(source_text[:500] + ("..." if len(source_text) > 500 else ""))
    print()

    # Step 2: Extract structured data (TODO for learner)
    print("=== Running structured extraction... ===\n")
    extraction = extract_structured(source_text)

    # Step 3: Display validated result
    print("=== Validated extraction ===\n")
    print(extraction.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
