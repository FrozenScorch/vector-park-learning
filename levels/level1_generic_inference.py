"""Level 1 demo: make one generic LLM call over park-related text."""

from __future__ import annotations

import argparse
from typing import Literal

from dotenv import load_dotenv

try:
    from levels.llm_provider import make_llm_client
    from levels.nps_client import fetch_park, format_park_text_for_inference
except ModuleNotFoundError:
    from llm_provider import make_llm_client
    from nps_client import fetch_park, format_park_text_for_inference

Mode = Literal["summarize", "rewrite", "classify", "extract"]


def fetch_park_text(park_code: str) -> str:
    park = fetch_park(park_code)
    return format_park_text_for_inference(park)


def build_prompt(mode: Mode, text: str) -> str:
    prompts = {
        "summarize": (
            "Summarize the source text for a first-time national park visitor. "
            "Use 4 bullets. Keep it practical and do not add facts not present in the source."
        ),
        "rewrite": (
            "Rewrite the source text for a family audience planning a trip. "
            "Use plain language, keep safety nuance, and do not add new facts."
        ),
        "classify": (
            "Classify the visitor question into exactly one category: trip planning, "
            "safety/alerts, camping, hiking, accessibility, fees/logistics, or not enough information. "
            "Return the category and one sentence explaining why."
        ),
        "extract": (
            "Extract action items from the source text. Return valid JSON with this shape: "
            '{"action_items":[{"task":"string","owner":"unknown","deadline":"unknown","evidence":"string"}]}. '
            "Use unknown when the source does not say."
        ),
    }
    return f"{prompts[mode]}\n\nSource text:\n{text}"


def run_inference(mode: Mode, text: str, temperature: float) -> str:
    client, config = make_llm_client()
    completion_kwargs = {}
    if config.max_tokens:
        completion_kwargs["max_tokens"] = config.max_tokens
    if config.top_p:
        completion_kwargs["top_p"] = config.top_p
    if config.extra_body:
        completion_kwargs["extra_body"] = config.extra_body

    response = client.chat.completions.create(
        model=config.model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful field guide assistant. Ground every answer in the provided "
                    "source text. Say when the source does not contain enough information."
                ),
            },
            {"role": "user", "content": build_prompt(mode, text)},
        ],
        **completion_kwargs,
    )
    return response.choices[0].message.content or ""


def read_text_arg(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as file:
            return file.read()
    return fetch_park_text(args.park_code.strip().lower())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["summarize", "rewrite", "classify", "extract"], required=True)
    parser.add_argument("--park-code", default="yell", help="Used when --text or --text-file is omitted.")
    parser.add_argument("--text", help="Inline text to send to the LLM.")
    parser.add_argument("--text-file", help="Path to a text file to send to the LLM.")
    parser.add_argument("--temperature", type=float, default=0.2)
    args = parser.parse_args()

    load_dotenv()
    text = read_text_arg(args)
    print(run_inference(args.mode, text, args.temperature))


if __name__ == "__main__":
    main()
