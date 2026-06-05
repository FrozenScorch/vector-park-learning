"""Level 1 Chainlit demo: generic inference modes over park text."""

from __future__ import annotations

from typing import Literal

import chainlit as cl
from dotenv import load_dotenv

try:
    from levels.llm_provider import make_llm_client
    from levels.nps_client import fetch_park, format_park_text_for_inference
except ModuleNotFoundError:
    from llm_provider import make_llm_client
    from nps_client import fetch_park, format_park_text_for_inference


Mode = Literal["summarize", "rewrite", "classify", "extract"]


load_dotenv()


def fetch_park_text(park_code: str) -> str:
    park = fetch_park(park_code)
    return format_park_text_for_inference(park)


def build_prompt(mode: Mode, text: str) -> str:
    prompts = {
        "summarize": "Summarize this for a first-time visitor in 4 practical bullets.",
        "rewrite": "Rewrite this for a family audience. Preserve safety nuance. Add no new facts.",
        "classify": (
            "Classify this into exactly one category: trip planning, safety/alerts, camping, "
            "hiking, accessibility, fees/logistics, or not enough information. Explain briefly."
        ),
        "extract": (
            "Extract action items. Return valid JSON with action_items, task, owner, deadline, and evidence. "
            "Use unknown when missing."
        ),
    }
    return f"{prompts[mode]}\n\nSource text:\n{text}"


def run_inference(mode: Mode, text: str) -> str:
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
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful field guide assistant. Use only the provided source text. "
                    "Say when there is not enough information."
                ),
            },
            {"role": "user", "content": build_prompt(mode, text)},
        ],
        **completion_kwargs,
    )
    return response.choices[0].message.content or ""


def parse_message(raw: str) -> tuple[Mode, str]:
    parts = raw.strip().split(maxsplit=1)
    if not parts or parts[0].lower() not in {"summarize", "rewrite", "classify", "extract"}:
        raise ValueError("Start with `summarize`, `rewrite`, `classify`, or `extract`.")
    if len(parts) == 1:
        raise ValueError("Add a park code or text after the mode.")
    return parts[0].lower(), parts[1].strip()  # type: ignore[return-value]


@cl.on_message
async def main(message: cl.Message) -> None:
    try:
        mode, value = parse_message(message.content)
        if mode in {"summarize", "rewrite"} and len(value) <= 5 and value.isalnum():
            source_text = fetch_park_text(value.lower())
        else:
            source_text = value
        answer = run_inference(mode, source_text)
    except Exception as exc:
        await cl.Message(content=f"Could not run inference: {exc}").send()
        return

    await cl.Message(content=answer).send()
